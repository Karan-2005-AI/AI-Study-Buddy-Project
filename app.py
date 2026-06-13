import gradio as gr
import google.generativeai as genai
import os

# ---------------- API SETUP ----------------
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


# ---------------- AI CORE ----------------
def build_prompt(message, mode):
    base_style = {
        "Explain Mode": "Explain like a teacher step-by-step with simple examples.",
        "Exam Mode": "Give exam-ready answers with headings, points, and keywords.",
        "Quick Mode": "Give short, crisp answers in 3-5 lines.",
        "Deep Mode": "Give detailed explanation with concepts, intuition, and examples."
    }

    instruction = base_style.get(mode, base_style["Explain Mode"])

    prompt = f"""
You are AI Study Buddy for an engineering student.

{instruction}

Question:
{message}
"""
    return prompt


def chat(message, history, mode):
    try:
        prompt = build_prompt(message, mode)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ---------------- UI ----------------
with gr.Blocks(theme=gr.themes.Soft(), title="AI Study Buddy 📚") as demo:

    # Sidebar
    with gr.Sidebar():
        gr.Markdown("## 📚 Study Controls")

        mode = gr.Radio(
            choices=["Explain Mode", "Exam Mode", "Quick Mode", "Deep Mode"],
            value="Explain Mode",
            label="Select Mode"
        )

        gr.Markdown("---")
        gr.Markdown("💡 Tip: Choose mode before asking questions")

    # Main Chat Area
    gr.Markdown("# 🧠 AI Study Buddy")
    gr.Markdown("Your personal AI tutor for engineering subjects 🚀")

    chatbot = gr.ChatInterface(
        fn=lambda msg, history: chat(msg, history, mode.value),
        title="",
        description=""
    )

# ---------------- LAUNCH ----------------
demo.launch(server_name="0.0.0.0", server_port=7860)