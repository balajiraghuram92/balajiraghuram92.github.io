import gradio as gr
from summarize import summarize

gr.Interface(
    fn=summarize,
    inputs=gr.Textbox(label="Website URL"),
    outputs=gr.Markdown(label="Summary"),
    title="🔎 AI Website Summarizer",
).launch(share=True)