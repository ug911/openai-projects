import yaml
import openai
import gradio as gr
from datetime import datetime
from mongo_connect import MongoConnect


class InterviewAssistant:
    def __init__(self):
        # Initialize any necessary attributes or resources here
        with open("configs/config.yaml", "r") as f:
            cx = yaml.safe_load(f)

        self.client = openai.OpenAI(
            # This is the default and can be omitted
            api_key=cx['openai']['api_key'],
        )
        self.mongo_client = MongoConnect()
        self.object_id = self.mongo_client.create_new()
        self.assistant_instructions = None
        self.questions = None
        self.skills = None
        self.conversation_messages = []
        self.analysis = None
        self.assistant_id = self.get_assistant(name="Interview Assistant")
        self.model = cx['openai'].get('model', 'gpt-3.5-turbo')
        pass

    def chat_completion(self, messages, key):
        """
        Generates skills for the employee based on input parameters.

        Args:
            messages: Array of user, assistant and system messages
            key: Specify the type of task that the chat completion is being used for

        Returns:
            str: Generated response
        """
        print(messages)
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
        )
        response = chat_completion.choices[0].message.to_dict()['content']
        self.mongo_client.update({
            "$addToSet": {
                "runs": {
                    "run_at": datetime.now(),
                    "key": key,
                    "messages": messages,
                    "model": self.model,
                    "response": chat_completion.to_dict()
                }
            }
        })
        return response

    def get_assistant(self, name="Interview Assistant"):
        assistant_name = name

        self.assistant_instructions = '''## Aim: 
            - Ask questions to gather information about the skills of the user  
            - Use the provided questions as a guideline to ask questions

            ## Persona: 
            - Always stay on point and do not get distracted
            - Encourage user to think deeply and articulate their thoughts clearly
            - Be encouraging and inquisitive
            - Maintain professionalism in all circumstances
            - Ensure the user feels supported throughout the conversation

            ## Restrictions
            - Do not deviate from a professional demeanor
            - Do not use slang, jargon, or inappropriate language under any circumstances
            - Do not provide answers or opinions on the topics discussed
            - Do not disclose or discuss any specific reasons behind asking the questions

            ## Ending the conversation
            - End after all information is gathered
            - End with this exact phrase "Thank you for your answers. Hope you have a good day. Bye.'''

        all_assistants = self.client.beta.assistants.list(
            order="desc",
            limit="20",
        )

        assistant_id = None
        for _asst in all_assistants.to_dict().get('data', []):
            if _asst.get('name', '') == assistant_name:
                assistant_id = _asst.get('id')
                print('Found the assistant - {} | {}'.format(assistant_name, assistant_id))

        if not assistant_id:
            print("No Assistant Found.")
            print("Creating a new assistant...")
            assistant = self.client.beta.assistants.create(
                name="Interview Assistant",
                instructions=self.assistant_instructions,
                model="gpt-3.5-turbo"
            )
            assistant_id = assistant.to_dict().get('id')
        self.mongo_client.update({"$set": {"assistant_id": assistant_id}})
        return assistant_id

    def generate_questions(self, company_info, designation, department):
        """
        Generates interview questions based on input parameters.

        Args:
            company_info: Basic info about the company
            designation: Employee designation in the company
            department: Department where the employee works in the company

        Returns:
            str: Generated interview questions.
        """
        # Validate if all the parameters are available
        if company_info == '' or designation == '' or department == '':
            raise gr.Error("Can not generate questions without Company, Designation and Department")

        # Create a prompt based on input parameters and use chat completion to generate questions
        prompt = '''
        You are an expert interviewer and have conducted various skill assessment interviews for tech people from all over the world.
        You have help me interview a person who is {designation} in {department} working in a {company}. 
        My main objective is to identfy the skill this person has. 
        Give me a set of 10 questions I should ask this person such that I should be able to assess the skills this person has.
        Note the Following:
        1. I want you to generate questions which a friend would ask another friend. 
        2. Do not be intrusive, the questions should not feel as if those questions are meant to judge them 
        3. Ask encouraging questions which gets people excited to answer, giving them a chance to brag and highlight achievements
        4. Be Highly informal in your tone but make sure you are always appropriate with no foul language
        5. Ask general questions related to their designation to see their interest and expertise level.
        6. Ask at least 2 questions about any programming languages, frameworks or tools used in everyday work and used in general.''' \
            .format(designation=designation, department=department, company=company_info)

        messages = [{
            "role": "user",
            "content": prompt
        }]

        # Use OpenAI chat completion to generate questions
        self.questions = self.chat_completion(messages, key='questions')
        return prompt, self.questions

    def generate_skills(self, company_info, designation, department):
        """
        Generates skills for the employee based on input parameters.

        Args:
            company_info: Basic info about the company
            designation: Employee designation in the company
            department: Department where the employee works in the company

        Returns:
            str: Generated interview questions.
        """
        # Validate if all the parameters are available
        if company_info == '' or designation == '' or department == '':
            raise gr.Error("Can not generate skills without Company, Designation and Department")

        # Create a prompt based on input parameters and use chat completion to generate questions
        prompt = ("What should be skills that a {designation} in {department} should have who is working in a " +
                  "{company}? Provide the categories and skills inside those categories").format(
            designation=designation, department=department, company=company_info)

        messages = [{
            "role": "user",
            "content": prompt
        }]

        # Use OpenAI chat completion to generate skills
        self.skills = self.chat_completion(messages, key='skills')
        return prompt, self.skills

    def respond_assistant(self, message, history):
        """
        Generates a response based on the given prompt.

        Args:
            message: Input message from the user
            history: History of the conversation so far

        Returns:
            str: Generated response.
        """
        # Use chat completion to generate a response
        # Implement your logic here
        pass

    def respond_completion(self, message, history):
        """
        Generates a response based on the given prompt.

        Args:
            message: Input message from the user
            history: History of the conversation so far

        Returns:
            str: Generated response.
        """
        print(message)
        completion_messages = self.build_completion_prompt(history)
        completion_messages += [{"role": "user", "content": message}]

        # Use OpenAI chat completion to generate a response
        response = self.chat_completion(completion_messages, key='chat')
        self.conversation_messages = completion_messages + [{"role": "assistant", "content": response}]
        return response

    def build_completion_prompt(self, history):
        """
        Using the history of the conversation, build the input message for completion

        Args:
            history: History of the conversation so far

        Returns:
            str: Analysis of the conversation.
        """
        # Create system instructions using assistant instructions and additional instructions
        messages = [
            {"role": "system", "content": self.assistant_instructions},
            {"role": "system", "content": "## Questions to keep as guidelines:\n{questions}".format(
                questions=self.questions
            )},
        ]

        # Process the history and add User and Assistant message to the conversation
        for _conv_step in history:
            messages += [
                {"role": "user", "content": _conv_step[0]},
                {"role": "assistant", "content": _conv_step[1]},
            ]
        return messages

    def build_conversation_text(self):
        # messages = self.client.beta.threads.messages.list(self.thread_id, limit=100).to_dict()
        # conversation_text = ''
        # for _msg in messages['data'][::-1]:
        #     conversation_text += '{}: {}\n'.format(_msg['role'], _msg['content'][0]['text']['value'])
        conversation_text = ''
        for _msg in self.conversation_messages:
            conversation_text += '{}: {}\n'.format(_msg['role'], _msg['content'])
        return conversation_text

    def analyse_conversation(self):
        """
        Analyses a conversation based on skills and conversation input.

        Returns:
            str: Analysis of the conversation.
        """
        conversation_text = self.build_conversation_text()
        analysis_prompt = '''## Aim: Based on the conversation, 
        - Evaluate the user's skills
        - For each of the mentioned skills, give a rating as mentioned
        
        ## Output
        For each required skill, provide the following information
        - Skill Present: Does conversation mention about the skill
            - Value should be "Yes" if the skill is mentioned in the conversation
            - Value should be "No" if the skill is not mentioned
        - Level of knowledge of the skill: How well the user demonstrates this skill
            - Good: Demonstrates exceptional abilities about the skill
            - Medium: User demonstrates some abilities and willingness to learn
            - Low: User lacks enough knowledge of the skill
            - Not present: There is no mention of the skill in the conversation
            
        ## Skills
        {skills}
        
        ## Conversation
        {conversation}
        '''.format(skills=self.skills, conversation=conversation_text)

        messages = [{
            "role": "user",
            "content": analysis_prompt
        }]

        # Use OpenAI chat completion to generate skills
        self.analysis = self.chat_completion(messages, key='analysis')
        return self.analysis

