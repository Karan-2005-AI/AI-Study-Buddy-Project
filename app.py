import streamlit as st
import os
import requests
import json

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="centered",
)

# ==========================================
# GEMINI API SETUP
# ==========================================

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
GEMINI_STREAM_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:streamGenerateContent"

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


def gemini_generate(prompt, history=None):
    contents = []
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
    }
    response = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json"},
        params={"key": API_KEY},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def gemini_stream(prompt, history=None):
    contents = []
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
    }
    with requests.post(
        GEMINI_STREAM_URL,
        headers={"Content-Type": "application/json"},
        params={"key": API_KEY, "alt": "sse"},
        json=payload,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        text = data["candidates"][0]["content"]["parts"][0].get("text", "")
                        if text:
                            yield text
                    except (KeyError, json.JSONDecodeError):
                        continue


# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <h1>🎓 AI Study Buddy</h1>
    <p style="color: #666;">Your intelligent AI-powered study assistant — powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)

if not API_KEY:
    st.error("⚠️ **GEMINI_API_KEY** is not set. Go to Space Settings → Variables and secrets → New secret.")
    st.stop()

# ==========================================
# TABS
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 AI Chat", "📚 Concept Explainer", "📝 Notes Summarizer", "🧠 Quiz Generator", "💻 Code Helper"
])

# ======================================
# TAB 1: AI CHAT
# ======================================

with tab1:
    st.markdown("**Chat with your Study Buddy!** Ask anything — study topics, coding help, or just have a conversation.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            try:
                for chunk in gemini_stream(prompt, st.session_state.messages[:-1]):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"⚠️ Error: {str(e)}"
                response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("**💡 Try these examples:**")
    examples = [
        "Explain machine learning in simple words",
        "What is the difference between AI, ML, and Deep Learning?",
        "Write a Python program to implement binary search",
        "Explain the OSI model with layers",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"ex_{i}"):
            st.session_state.messages.append({"role": "user", "content": ex})
            st.rerun()

# ======================================
# TAB 2: CONCEPT EXPLAINER
# ======================================

with tab2:
    st.markdown("Enter any topic and get a clear, structured explanation perfect for engineering students.")
    topic = st.text_input("Enter Topic", placeholder="Example: Machine Learning, Recursion, Dijkstra's Algorithm...")
    if st.button("Explain Topic ✨", type="primary"):
        if topic.strip():
            with st.spinner("Explaining..."):
                try:
                    result = gemini_generate(f"""Explain this topic in simple and easy English for engineering students.

Topic: {topic}

Give:
- Simple definition
- Key points (with examples)
- One real-world application
- Short conclusion

Use markdown formatting with bold headings and bullet points.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("Please enter a topic.")

# ======================================
# TAB 3: NOTES SUMMARIZER
# ======================================

with tab3:
    st.markdown("Paste your lengthy study notes and get a concise, bullet-point summary instantly.")
    notes = st.text_area("Paste Your Notes", placeholder="Paste your study notes here...", height=250)
    if st.button("Summarize Notes 📋", type="primary"):
        if notes.strip():
            with st.spinner("Summarizing..."):
                try:
                    result = gemini_generate(f"""Summarize these study notes for an engineering student.

Use:
- Short bullet points
- **Bold** for important concepts
- Important definitions
- Key formulas if present (in code blocks)

Do not add information that is not in the notes.

Notes:
{notes}""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("Please paste your notes.")

# ======================================
# TAB 4: QUIZ GENERATOR
# ======================================

with tab4:
    st.markdown("Generate 5 MCQ questions on any topic to test your knowledge!")
    quiz_topic = st.text_input("Enter Topic", placeholder="Example: Artificial Intelligence, Data Structures, DBMS...", key="quiz_topic")
    if st.button("Generate Quiz 🎯", type="primary"):
        if quiz_topic.strip():
            with st.spinner("Generating quiz..."):
                try:
                    result = gemini_generate(f"""Create 5 multiple-choice questions about: {quiz_topic}

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
Use markdown formatting.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("Please enter a topic.")

# ======================================
# TAB 5: CODE HELPER
# ======================================

with tab5:
    st.markdown("Describe any coding problem and get a complete solution with explanation.")
    col1, col2 = st.columns([1, 3])
    with col1:
        language = st.selectbox("Language", ["Python", "C", "C++", "Java", "JavaScript", "SQL", "Other"])
    with col2:
        problem = st.text_area("Describe your problem", placeholder="Example: Write a program to find the factorial of a number using recursion", height=100)
    if st.button("Solve It 🔧", type="primary"):
        if problem.strip():
            with st.spinner("Solving..."):
                try:
                    result = gemini_generate(f"""You are an expert programming tutor helping an engineering student.

Language: {language}
Problem: {problem}

Provide:
1. A clear explanation of the approach
2. Complete working code with comments
3. Explanation of the key lines
4. Time/space complexity if relevant

Use proper markdown code blocks.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("Please describe your problem.")

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:12px;'>"
    "Built with ❤️ by <b>Karan Dewangan</b> | B.Tech CS (AIML) | Chouksey Engineering College, Bilaspur | Minor Project Phase 1"
    "</div>",
    unsafe_allow_html=True,
)
