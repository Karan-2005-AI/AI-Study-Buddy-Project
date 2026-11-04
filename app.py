import streamlit as st
import os
import base64
import io
import requests as http_requests
from PIL import Image
import google.generativeai as genai
from groq import Groq

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="centered",
)

# ==========================================
# API SETUP
# ==========================================

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY   = os.getenv("GROQ_API_KEY")

GROQ_MODEL      = "llama-3.3-70b-versatile"
IMAGE_GEN_MODEL = "gemini-2.5-flash-image"
IMAGE_VIS_MODEL = "gemini-2.5-flash"

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

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
# HELPER FUNCTIONS
# ==========================================

def groq_stream(prompt, history=None):
    """Stream text response via Groq (unlimited free tier)."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})
    stream = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text


def groq_generate(prompt, history=None):
    """Single text response via Groq."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


def gemini_analyze_image(image_bytes, prompt):
    """Analyze an uploaded image using Gemini vision."""
    image = Image.open(io.BytesIO(image_bytes))
    model = genai.GenerativeModel(IMAGE_VIS_MODEL)
    response = model.generate_content([prompt, image])
    return response.text


def gemini_generate_image(prompt):
    """Generate an image using Gemini image model."""
    model = genai.GenerativeModel(IMAGE_GEN_MODEL)
    response = model.generate_content(
        prompt,
        generation_config={"response_modalities": ["TEXT", "IMAGE"]},
    )
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            return base64.b64decode(part.inline_data.data)
    return None


# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <h1>🎓 AI Study Buddy</h1>
    <p style="color: #666;">Your intelligent AI-powered study assistant — powered by Groq + Google Gemini</p>
</div>
""", unsafe_allow_html=True)

# Show warnings if keys missing
if not GROQ_KEY:
    st.error("⚠️ **GROQ_API_KEY** is not set. Add it in Space Settings → Variables and secrets.")
    st.stop()
if not GEMINI_KEY:
    st.warning("⚠️ **GEMINI_API_KEY** not set — Image Generator & Image Analyzer will not work. Other features work fine.")

# ==========================================
# TABS
# ==========================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "💬 AI Chat",
    "🎨 Image Generator",
    "📷 Image Analyzer",
    "📚 Concept Explainer",
    "📝 Notes Summarizer",
    "🧠 Quiz Generator",
    "💻 Code Helper",
])

# ======================================
# TAB 1: AI CHAT (Groq)
# ======================================

with tab1:
    st.markdown("**Chat with your Study Buddy!** Ask anything — study topics, coding help, or just have a conversation.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask me anything...") or st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            try:
                for chunk in groq_stream(prompt, st.session_state.messages[:-1]):
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
            st.session_state.pending_prompt = ex
            st.rerun()

# ======================================
# TAB 2: IMAGE GENERATOR (Gemini)
# ======================================

with tab2:
    st.markdown("Generate images from text descriptions using Gemini's image generation capability.")

    if not GEMINI_KEY:
        st.error("⚠️ GEMINI_API_KEY is required for image generation. Add it in Space Settings.")
    else:
        img_prompt = st.text_area(
            "Describe the image you want to generate",
            placeholder="Example: A futuristic classroom with AI robots teaching students, digital art style",
            height=100,
        )
        if st.button("Generate Image 🎨", type="primary"):
            if img_prompt.strip():
                with st.spinner("Generating image... this may take a moment ✨"):
                    try:
                        img_bytes = gemini_generate_image(img_prompt)
                        if img_bytes:
                            st.image(img_bytes, caption=img_prompt, use_container_width=True)
                            st.download_button(
                                label="⬇️ Download Image",
                                data=img_bytes,
                                file_name="generated_image.png",
                                mime="image/png",
                            )
                        else:
                            st.warning("No image was returned. Try a different prompt.")
                    except Exception as e:
                        st.error(f"⚠️ Error: {str(e)}")
            else:
                st.warning("Please describe the image you want to generate.")

        st.markdown("**💡 Example prompts:**")
        img_examples = [
            "A diagram showing how neural networks work, educational style",
            "Binary search tree data structure visualization",
            "The OSI model as a colorful infographic",
            "A futuristic AI-powered study room",
        ]
        img_cols = st.columns(2)
        for i, ex in enumerate(img_examples):
            img_cols[i % 2].code(ex, language=None)

# ======================================
# TAB 3: IMAGE ANALYZER (Gemini)
# ======================================

with tab3:
    st.markdown("Upload any image — diagrams, notes, screenshots, charts — and ask Gemini to analyze it.")

    if not GEMINI_KEY:
        st.error("⚠️ GEMINI_API_KEY is required for image analysis. Add it in Space Settings.")
    else:
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "gif"],
        )
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            analysis_prompt = st.text_input(
                "What do you want to know about this image?",
                value="Describe this image in detail and explain what it shows.",
            )
            if st.button("Analyze Image 🔍", type="primary"):
                with st.spinner("Analyzing..."):
                    try:
                        result = gemini_analyze_image(uploaded_file.read(), analysis_prompt)
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"⚠️ Error: {str(e)}")
        else:
            st.info("👆 Upload an image to get started. You can upload diagrams, handwritten notes, flowcharts, code screenshots, etc.")

# ======================================
# TAB 4: CONCEPT EXPLAINER (Groq)
# ======================================

with tab4:
    st.markdown("Enter any topic and get a clear, structured explanation perfect for engineering students.")
    topic = st.text_input("Enter Topic", placeholder="Example: Machine Learning, Recursion, Dijkstra's Algorithm...")
    if st.button("Explain Topic ✨", type="primary"):
        if topic.strip():
            with st.spinner("Explaining..."):
                try:
                    result = groq_generate(f"""Explain this topic in simple and easy English for engineering students.

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
# TAB 5: NOTES SUMMARIZER (Groq)
# ======================================

with tab5:
    st.markdown("Paste your lengthy study notes and get a concise, bullet-point summary instantly.")
    notes = st.text_area("Paste Your Notes", placeholder="Paste your study notes here...", height=250)
    if st.button("Summarize Notes 📋", type="primary"):
        if notes.strip():
            with st.spinner("Summarizing..."):
                try:
                    result = groq_generate(f"""Summarize these study notes for an engineering student.

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
# TAB 6: QUIZ GENERATOR (Groq)
# ======================================

with tab6:
    st.markdown("Generate 5 MCQ questions on any topic to test your knowledge!")
    quiz_topic = st.text_input("Enter Topic", placeholder="Example: Artificial Intelligence, Data Structures, DBMS...", key="quiz_topic")
    if st.button("Generate Quiz 🎯", type="primary"):
        if quiz_topic.strip():
            with st.spinner("Generating quiz..."):
                try:
                    result = groq_generate(f"""Create 5 multiple-choice questions about: {quiz_topic}

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
# TAB 7: CODE HELPER (Groq)
# ======================================

with tab7:
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
                    result = groq_generate(f"""You are an expert programming tutor helping an engineering student.

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
