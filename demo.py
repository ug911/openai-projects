import gradio as gr
from openai_assistant import InterviewAssistant

interview_assistant = InterviewAssistant()

CSS = """
.contain {
    display: flex;
    flex-direction: column;
}
div#chatbot-column {
    height: 70vh !important;  # Set to desired height (e.g., 650px)
}
.tabitem {
    height: 80vh !important;  # Set to desired height (e.g., 650px)
}
"""


with gr.Blocks(title = "Inputs") as inputs:
    with gr.Row():
        gr.Markdown('### Inputs')
        with gr.Column(scale=4):
            with gr.Row():
                in_cmp = gr.Textbox(label="Company Type", container=False, placeholder="Enter company info")
                in_dsg = gr.Textbox(label="Designation", container=False, placeholder="Enter designation")
                in_dpt = gr.Textbox(label="Department", container=False, placeholder="Enter department")
    with gr.Row():
        gr.Markdown('### Prompts')
        with gr.Column(scale=2):
            gr.Markdown('#### Prompt for Questions')
            question_prompt_txt = gr.Textbox("Question Prompt", container=False, lines=3, placeholder="Question prompt")
        with gr.Column(scale=2):
            gr.Markdown('#### Prompt for Skills')
            skills_prompt_txt = gr.Textbox("Skills Prompt", container=False, lines=3, placeholder="Skills prompt")
    with gr.Row():
        gr.Markdown('### Results for Bot')
        with gr.Column(scale=2):
            gr.Markdown('#### Actual Questions')
            question_text = gr.Textbox("Questions for Bot", container=False, lines=3, max_lines=10, placeholder="Question text", interactive=False, show_copy_button=True)
            btn1 = gr.Button("Fetch Questions for Bot")
            btn1.click(fn=interview_assistant.generate_questions,
                       inputs=[in_cmp, in_dsg, in_dpt],
                       outputs=[question_prompt_txt, question_text])
        with gr.Column(scale=2):
            gr.Markdown('#### Actual Skills')
            skills_text = gr.Textbox("Skills for Bot", container=False, lines=3, max_lines=10, placeholder="Skills text", interactive=False, show_copy_button=True)
            btn2 = gr.Button("Fetch Skills for Bot")
            btn2.click(fn=interview_assistant.generate_skills,
                       inputs=[in_cmp, in_dsg, in_dpt],
                       outputs=[skills_prompt_txt, skills_text])

with gr.Blocks(css=CSS) as chat:
    gr.Markdown('## Chat with the employee')
    with gr.Column(elem_id='chatbot-column'):
        gr.ChatInterface(fn=interview_assistant.respond_completion)

with gr.Blocks(title="Analyse the Skills") as analysis:
    gr.Markdown('## Analyse the Conversation for Skills')
    btn5 = gr.Button("Analyse Conversation")
    analysis_text = gr.Textbox(label="Conversation Analysis", container=False, lines = 10, max_lines=10)
    btn5.click(fn=interview_assistant.analyse_conversation, inputs=None, outputs=analysis_text)

demo = gr.TabbedInterface(
    title="Interview Bot",
    interface_list=[inputs, chat, analysis],
    tab_names=["Inputs", "Chat", "Analysis"],
    css=CSS
)

demo.launch()
