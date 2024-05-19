import os
from openai import OpenAI, ChatCompletion

class OpenAIAssistant:
    def __init__(self, assistant_id):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.assistant_id = assistant_id
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4.0-turbo"
        # TODO: Create a ChatCompletion prompt for finding the questions to ask for a designation and department
        self.question_client = ChatCompletion.create(
            model=self.model,
            messages=[{"role": "system", "content": "You are a helpful assistant."}],
        )
        # TODO: Create a ChatCompletion prompt for finding the skills for a designation and department
        self.skills_client = ChatCompletion.create(
            model=self.model,
            messages=[{"role": "system", "content": "You are a helpful assistant."}],
        )
        # TODO: Create a ChatCompletion prompt for skills analysis
        self.analysis_client = ChatCompletion.create(
            model=self.model,
            messages=[{"role": "system", "content": "You are a helpful assistant."}],
        )

    def create_assistant(self):
        assistant = self.client.beta.assistants.create(
            name="X Threads Converter",
            instructions="You are a helpful assistant. Given a set of files, you extract the most interesting information and restructure it into Threads format for Twitter.",
            model=self.model,
            tools=[{"type": "retrieval"}]
        )
        return assistant

    def get_questions(self, designation, department):
        # TODO: Need to add the prompt for generating questions
        user_message = '{} {}'.format(designation, department)
        question_response = self.question_client.update(
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "I can help with that!"},
            ]
        )

        questions = question_response.choices[0].message["content"]
        return questions

    def get_skills(self, designation, department):
        # TODO: Need to add the prompt for generating skills
        user_message = '{} {}'.format(designation, department)
        skills_response = self.skills_client.update(
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "I can help with that!"},
            ]
        )

        skills = skills_response.choices[0].message["content"]
        return skills

    def create_assistant_thread_run(self, thread_id, questions):
        run = ''
        return run

    def analyse_skills(self, skills, conversation):
        # TODO: Need to add the prompt for generating skills
        user_message = '{} {}'.format(skills, conversation)
        skills_analysis_response = self.analysis_client.update(
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "I can help with that!"},
            ]
        )

        skill_analysis = skills_analysis_response.choices[0].message["content"]
        return skill_analysis


# Example usage:
if __name__ == "__main__":
    my_api_key = "your_api_key_here"
    my_assistant_id = "your_assistant_id_here"

    assistant = OpenAIAssistant(api_key=my_api_key, assistant_id=my_assistant_id)
    user_input = "Can you generate a catchy YouTube title for my video?"
    assistant_response = assistant.ask(user_input)
    print("Assistant's response:", assistant_response)
