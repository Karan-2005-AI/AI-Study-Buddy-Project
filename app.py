import gradio as gr
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def chat(prompt):
    return model.generate_content(prompt).text

gr.Interface(fn=chat, inputs="text", outputs="text").launch()