from llm_client import invoke_llmquery
import gradio as gr
 

system_prompt= """
                Your as personal assisant and help answers User queries on any subject
                """
def arena_ai(user_msg):
   res1 = gemini_ai(user_msg)
   res2 = muse_ai(user_msg)
   return res1,res2,res1,res2,gr.update(visible=True),gr.update(visible=True)

def gemini_ai(user_msg):
   return invoke_llmquery(system_prompt,
      user_msg,
      model="gemini-3.1-flash-lite",
      reasoning_effort="minimal",
      provider="gemini",
   )


def muse_ai(user_msg):
    return invoke_llmquery(system_prompt,
       user_msg,
       model="muse-spark-1.3-contributor",
       reasoning_effort="minimal",
       provider="muse_ai"
    )

def pick_a(user_msg, prev_msg):
    more = f"[A] Nice, understood could you provide more detail on '{user_msg}' (building on: {prev_msg})"
    return gemini_ai(more), gr.update(visible=False)

def pick_b(user_msg, prev_msg):
    more = f"Nice, understood could you provide more detail on '{user_msg}' (building on: {prev_msg})"
    return muse_ai(more), gr.update(visible=False)

with gr.Blocks(title="🔎 Arena Battle madness") as demo: 
    prompt_box = gr.Textbox(label="Enter your question :")
    ask_btn = gr.Button("Ask")

    state_a = gr.State()
    state_b = gr.State()

    with gr.Row():
        with gr.Column() as col_1:
            view_a = gr.Markdown(label="Gemini Response")
            accept_response_a = gr.Button("Yes")

        with gr.Column() as col_2:
            view_b = gr.Markdown(label="Muse AI Response")
            accept_response_b = gr.Button("Yes") 

    ask_btn.click(
        fn=arena_ai,
        inputs=prompt_box,
        outputs=[view_a, view_b, state_a, state_b, col_1, col_2])

    accept_response_a.click(
        fn=pick_a,
        inputs=[prompt_box, state_a],
        outputs=[view_a,col_2])

    accept_response_b.click(
        fn=pick_b,
        inputs=[prompt_box, state_b],
        outputs=[view_b, col_1])

demo.launch()