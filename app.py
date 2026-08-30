import gradio as gr
from google import genai
import os

# Gemini API Key 

API_KEY = "PASTE_YOUR_API_KEY_HERE"

client = genai.Client(api_key=API_KEY)

# Feature 1: Concept Explainer

def explain_topic(topic):
response = client.models.generate_content(
model="gemini-2.5-flash",
contents=f"Explain {topic} in simple words for engineering students."
)
return response.text

# Feature 2: Notes Summarizer

def summarize_notes(notes):
response = client.models.generate_content(
model="gemini-2.5-flash",
contents=f"Summarize the following notes in bullet points:\n\n{notes}"
)
return response.text

# Feature 3: Quiz Generator

def generate_quiz(topic):
response = client.models.generate_content(
model="gemini-2.5-flash",
contents=f"Generate 5 MCQs with answers on {topic}."
)
return response.text

with gr.Blocks(title="AI Study Buddy") as demo:

```
gr.Markdown("# 🎓 AI Study Buddy")
gr.Markdown("Powered by Gemini AI")

with gr.Tab("Concept Explainer"):
    topic = gr.Textbox(label="Enter Topic")
    output1 = gr.Textbox(lines=10)
    btn1 = gr.Button("Explain")
    btn1.click(explain_topic, topic, output1)

with gr.Tab("Notes Summarizer"):
    notes = gr.Textbox(lines=10, label="Paste Notes")
    output2 = gr.Textbox(lines=10)
    btn2 = gr.Button("Summarize")
    btn2.click(summarize_notes, notes, output2)

with gr.Tab("Quiz Generator"):
    quiz_topic = gr.Textbox(label="Enter Topic")
    output3 = gr.Textbox(lines=12)
    btn3 = gr.Button("Generate Quiz")
    btn3.click(generate_quiz, quiz_topic, output3)
```

demo.launch()
