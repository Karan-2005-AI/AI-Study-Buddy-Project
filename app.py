import gradio as gr
import google.generativeai as genai
import os

# ==========================================
# GEMINI API SETUP
# ==========================================

API_KEY = os.getenv("GEMINI_API_KEY")
API_KEY_MISSING = not API_KEY

if API_KEY:
    genai.configure(api_key=API_KEY)

MODEL = "gemini-1.5-flash"

# ==========================================
# SYSTEM PROMPT — Study Buddy Personality
# ==========================================

SYSTEM_PROMPT = """You are AI Study Buddy, a friendly and intelligent AI assistant created to help engineering students learn better.

Your personality:
- Friendly, encouraging, and patient
- You explain things clearly in simple English
- You can answer ANY question — not just study topics
- You remember the conversation history and refer back to it
- You format your answers with markdown: use **bold**, bullet points, code blocks, tables where helpful
- You give real examples to make concepts easy to understand
- If someone asks something off-topic (like jokes, general knowledge, life advice), you still help them warmly

You were built by Karan Dewangan, a B.Tech CS (AIML) student at Chouksey Engineering College, Bilaspur, Chhattisgarh as a Minor Project.

Always be helpful, conversational, and supportive — just like a real study buddy!"""


# ==========================================
# FEATURE 1: AI CHAT (with memory + streaming)
# ==========================================

def chat_stream(user_message, history):
    """
    Streaming chat with full conversation memory.
    history is a list of {"role": "user"/"assistant", "content": "..."} dicts.
    """
    if API_KEY_MISSING:
        yield history + [{"role": "assistant", "content": "⚠️ **API key not configured.** The space owner needs to add `GEMINI_API_KEY` in the Space Settings → Variables and secrets."}], ""
        return
    if not user_message.strip():
        yield history, ""
        return

    # Build conversation history for Gemini
    gemini_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # Add user message to display history immediately
    history = history + [{"role": "user", "content": user_message}]

    # Stream the response
    full_response = ""
    try:
        model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
        chat = model.start_chat(history=gemini_history)
        stream = chat.send_message(user_message, stream=True)

        for chunk in stream:
            if chunk.text:
                full_response += chunk.text
                current_history = history + [{"role": "assistant", "content": full_response}]
                yield current_history, ""

    except Exception as e:
        error_msg = f"⚠️ Error: {str(e)}"
        history = history + [{"role": "assistant", "content": error_msg}]
        yield history, ""
        return

    # Final yield with complete response
    final_history = history + [{"role": "assistant", "content": full_response}]
    yield final_history, ""


def clear_chat():
    return [], ""


# ==========================================
# FEATURE 2: CONCEPT EXPLAINER
# ==========================================

def explain_topic(topic):
    if API_KEY_MISSING:
        return "⚠️ **API key not configured.** The space owner needs to add `GEMINI_API_KEY` in the Space Settings → Variables and secrets."
    if not topic.strip():
        return "Please enter a topic."

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(f"""
Explain this topic in simple and easy English for engineering students.

Topic: {topic}

Give:
- Simple definition
- Key points (with examples)
- One real-world application
- Short conclusion

Use markdown formatting with bold headings and bullet points.
""")
        return response.text

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ==========================================
# FEATURE 3: NOTES SUMMARIZER
# ==========================================

def summarize_notes(notes):
    if API_KEY_MISSING:
        return "⚠️ **API key not configured.** The space owner needs to add `GEMINI_API_KEY` in the Space Settings → Variables and secrets."
    if not notes.strip():
        return "Please paste your notes."

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(f"""
Summarize these study notes for an engineering student.

Use:
- Short bullet points
- **Bold** for important concepts
- Important definitions
- Key formulas if present (in code blocks)

Do not add information that is not in the notes.

Notes:
{notes}
""")
        return response.text

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ==========================================
# FEATURE 4: QUIZ GENERATOR
# ==========================================

def generate_quiz(topic):
    if API_KEY_MISSING:
        return "⚠️ **API key not configured.** The space owner needs to add `GEMINI_API_KEY` in the Space Settings → Variables and secrets."
    if not topic.strip():
        return "Please enter a topic."

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(f"""
Create 5 multiple-choice questions about: {topic}

For each question provide:
**Q1.** Question text
- A. Option
- B. Option
- C. Option
- D. Option

After all 5 questions, provide:

---
**Answer Key:**
1. A
2. B
...

Keep the questions suitable for engineering students.
Use markdown formatting.
""")
        return response.text

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ==========================================
# FEATURE 5: CODE HELPER
# ==========================================

def help_with_code(language, problem):
    if API_KEY_MISSING:
        return "⚠️ **API key not configured.** The space owner needs to add `GEMINI_API_KEY` in the Space Settings → Variables and secrets."
    if not problem.strip():
        return "Please describe your coding problem."

    lang = language if language else "any language"

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(f"""
You are an expert programming tutor helping an engineering student.

Language: {lang}
Problem: {problem}

Provide:
1. A clear explanation of the approach
2. Complete working code with comments
3. Explanation of the key lines
4. Time/space complexity if relevant

Use proper markdown code blocks.
""")
        return response.text

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ==========================================
# GRADIO INTERFACE
# ==========================================

with gr.Blocks(
    title="AI Study Buddy",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="indigo",
    ),
    css="""
    .chat-header { text-align: center; padding: 10px 0; }
    .footer-text { text-align: center; color: #888; font-size: 12px; margin-top: 10px; }
    """
) as demo:

    gr.Markdown(
        """
        <div class="chat-header">

        # 🎓 AI Study Buddy
        ### Your intelligent AI-powered study assistant — powered by Google Gemini
        *Ask me anything! I can explain concepts, summarize notes, generate quizzes, help with code, and have full conversations.*

        </div>
        """,
    )

    # ======================================
    # TAB 1: AI CHAT (Main feature)
    # ======================================

    with gr.Tab("💬 AI Chat"):

        gr.Markdown("**Chat with your Study Buddy!** Ask anything — study topics, general questions, coding help, or just have a conversation.")

        chatbot = gr.Chatbot(
            label="AI Study Buddy Chat",
            height=500,
            type="messages",
            show_copy_button=True,
            bubble_full_width=False,
        )

        with gr.Row():
            chat_input = gr.Textbox(
                label="",
                placeholder="Ask me anything... (e.g. 'Explain neural networks', 'Write a Python sorting algorithm', 'What is quantum computing?')",
                scale=9,
                lines=1,
                autofocus=True,
            )
            send_btn = gr.Button("Send ➤", variant="primary", scale=1)

        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")

        gr.Examples(
            examples=[
                "Explain machine learning in simple words",
                "What is the difference between AI, ML, and Deep Learning?",
                "Write a Python program to implement binary search",
                "Explain the OSI model with layers",
                "What is DBMS and explain normalization?",
                "Tell me a fun fact about computer science",
            ],
            inputs=chat_input,
            label="💡 Try these examples:",
        )

        send_btn.click(
            fn=chat_stream,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_input],
        )
        chat_input.submit(
            fn=chat_stream,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_input],
        )
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot, chat_input],
        )

    # ======================================
    # TAB 2: CONCEPT EXPLAINER
    # ======================================

    with gr.Tab("📚 Concept Explainer"):

        gr.Markdown("Enter any topic and get a clear, structured explanation perfect for engineering students.")

        topic = gr.Textbox(
            label="Enter Topic",
            placeholder="Example: Machine Learning, Recursion, Dijkstra's Algorithm..."
        )

        explain_btn = gr.Button("Explain Topic ✨", variant="primary")
        explanation = gr.Markdown(label="Explanation")

        explain_btn.click(fn=explain_topic, inputs=topic, outputs=explanation)
        topic.submit(fn=explain_topic, inputs=topic, outputs=explanation)

    # ======================================
    # TAB 3: NOTES SUMMARIZER
    # ======================================

    with gr.Tab("📝 Notes Summarizer"):

        gr.Markdown("Paste your lengthy study notes and get a concise, bullet-point summary instantly.")

        notes = gr.Textbox(
            label="Paste Your Notes",
            placeholder="Paste your study notes here...",
            lines=12
        )

        summarize_btn = gr.Button("Summarize Notes 📋", variant="primary")
        summary = gr.Markdown(label="Summary")

        summarize_btn.click(fn=summarize_notes, inputs=notes, outputs=summary)

    # ======================================
    # TAB 4: QUIZ GENERATOR
    # ======================================

    with gr.Tab("🧠 Quiz Generator"):

        gr.Markdown("Generate 5 MCQ questions on any topic to test your knowledge!")

        quiz_topic = gr.Textbox(
            label="Enter Topic",
            placeholder="Example: Artificial Intelligence, Data Structures, DBMS..."
        )

        quiz_btn = gr.Button("Generate Quiz 🎯", variant="primary")
        quiz = gr.Markdown(label="Quiz")

        quiz_btn.click(fn=generate_quiz, inputs=quiz_topic, outputs=quiz)
        quiz_topic.submit(fn=generate_quiz, inputs=quiz_topic, outputs=quiz)

    # ======================================
    # TAB 5: CODE HELPER
    # ======================================

    with gr.Tab("💻 Code Helper"):

        gr.Markdown("Describe any coding problem and get a complete solution with explanation.")

        with gr.Row():
            code_language = gr.Dropdown(
                choices=["Python", "C", "C++", "Java", "JavaScript", "SQL", "Other"],
                label="Programming Language",
                value="Python",
                scale=2,
            )
            code_problem = gr.Textbox(
                label="Describe your problem",
                placeholder="Example: Write a program to find the factorial of a number using recursion",
                scale=8,
                lines=3,
            )

        code_btn = gr.Button("Solve It 🔧", variant="primary")
        code_output = gr.Markdown(label="Solution")

        code_btn.click(fn=help_with_code, inputs=[code_language, code_problem], outputs=code_output)

    # Footer
    gr.Markdown(
        """
        <div class="footer-text">

        ---
        Built with ❤️ by **Karan Dewangan** | B.Tech CS (AIML) | Chouksey Engineering College, Bilaspur | Minor Project Phase 1

        </div>
        """,
    )

# ==========================================
# LAUNCH
# ==========================================

demo.launch()
