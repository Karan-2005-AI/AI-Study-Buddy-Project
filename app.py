import gradio as gr
from google import genai
import os

# ==========================================
# GEMINI API
# ==========================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-2.5-flash"


# ==========================================
# FEATURE 1: CONCEPT EXPLAINER
# ==========================================

def explain_topic(topic):
    if not topic.strip():
        return "Please enter a topic."

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"""
Explain this topic in simple and easy English for engineering students.

Topic: {topic}

Give:
- Simple definition
- Key points
- One easy example
- Short conclusion

Keep the answer concise.
"""
        )

        return response.text

    except Exception as e:
        return f"Error: {str(e)}"


# ==========================================
# FEATURE 2: NOTES SUMMARIZER
# ==========================================

def summarize_notes(notes):
    if not notes.strip():
        return "Please paste your notes."

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"""
Summarize these study notes for an engineering student.

Use:
- Short bullet points
- Important concepts
- Important definitions
- Key formulas if present

Do not add information that is not in the notes.

Notes:
{notes}
"""
        )

        return response.text

    except Exception as e:
        return f"Error: {str(e)}"


# ==========================================
# FEATURE 3: QUIZ GENERATOR
# ==========================================

def generate_quiz(topic):
    if not topic.strip():
        return "Please enter a topic."

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"""
Create 5 multiple-choice questions about:

{topic}

For each question provide:
1. Question
A. Option
B. Option
C. Option
D. Option

At the end provide:
Answer Key:
1. A
2. B
3. C
4. D
5. A

Keep the questions suitable for engineering students.
"""
        )

        return response.text

    except Exception as e:
        return f"Error: {str(e)}"


# ==========================================
# GRADIO INTERFACE
# ==========================================

with gr.Blocks(
    title="AI Study Buddy"
) as demo:

    gr.Markdown(
        """
        # 🎓 AI Study Buddy
        ### Your AI-powered study assistant
        """
    )

    # --------------------------------------
    # Concept Explainer
    # --------------------------------------

    with gr.Tab("📚 Concept Explainer"):

        topic = gr.Textbox(
            label="Enter Topic",
            placeholder="Example: Machine Learning"
        )

        explain_btn = gr.Button(
            "Explain Topic",
            variant="primary"
        )

        explanation = gr.Markdown(
            label="Explanation"
        )

        explain_btn.click(
            fn=explain_topic,
            inputs=topic,
            outputs=explanation
        )


    # --------------------------------------
    # Notes Summarizer
    # --------------------------------------

    with gr.Tab("📝 Notes Summarizer"):

        notes = gr.Textbox(
            label="Paste Your Notes",
            placeholder="Paste your study notes here...",
            lines=12
        )

        summarize_btn = gr.Button(
            "Summarize Notes",
            variant="primary"
        )

        summary = gr.Markdown(
            label="Summary"
        )

        summarize_btn.click(
            fn=summarize_notes,
            inputs=notes,
            outputs=summary
        )


    # --------------------------------------
    # Quiz Generator
    # --------------------------------------

    with gr.Tab("🧠 Quiz Generator"):

        quiz_topic = gr.Textbox(
            label="Enter Topic",
            placeholder="Example: Artificial Intelligence"
        )

        quiz_btn = gr.Button(
            "Generate Quiz",
            variant="primary"
        )

        quiz = gr.Markdown(
            label="Quiz"
        )

        quiz_btn.click(
            fn=generate_quiz,
            inputs=quiz_topic,
            outputs=quiz
        )


# ==========================================
# LAUNCH
# ==========================================

demo.launch()
