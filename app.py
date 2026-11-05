import streamlit as st
import os
import base64
import io
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai

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

CHAT_MODEL      = "gemini-3.5-flash-lite"
IMAGE_GEN_MODEL = "gemini-2.5-flash-image"
IMAGE_VIS_MODEL = "gemini-3.5-flash-lite"

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

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

def gemini_stream(prompt, history=None):
    """Stream text response via Gemini."""
    gemini_history = []
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
    model = genai.GenerativeModel(CHAT_MODEL, system_instruction=SYSTEM_PROMPT)
    chat = model.start_chat(history=gemini_history)
    stream = chat.send_message(prompt, stream=True)
    for chunk in stream:
        if chunk.text:
            yield chunk.text


def gemini_generate(prompt):
    """Single text response via Gemini."""
    model = genai.GenerativeModel(CHAT_MODEL, system_instruction=SYSTEM_PROMPT)
    response = model.generate_content(prompt)
    return response.text


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
    <p style="color: #666;">Your intelligent AI-powered study assistant — powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)

if not GEMINI_KEY:
    st.error("⚠️ **GEMINI_API_KEY** is not set. Go to Space Settings → Variables and secrets → New secret.")
    st.stop()

# ==========================================
# TABS
# ==========================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "💬 AI Chat",
    "🎨 Image Generator",
    "📷 Image Analyzer",
    "📚 Concept Explainer",
    "📝 Notes Summarizer",
    "🧠 Quiz Generator",
    "💻 Code Helper",
    "🃏 Flashcard Generator",
    "📄 PDF Q&A",
    "📅 Study Planner",
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
# TAB 5: NOTES SUMMARIZER (Groq)
# ======================================

with tab5:
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
# TAB 6: QUIZ GENERATOR (Groq)
# ======================================

with tab6:
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

# ======================================
# TAB 8: FLASHCARD GENERATOR
# ======================================

with tab8:
    st.markdown("Generate **Q&A flashcards** from any topic or your own notes to boost revision!")

    fc_mode = st.radio("Generate flashcards from:", ["A Topic", "My Notes"], horizontal=True)

    if fc_mode == "A Topic":
        fc_input = st.text_input("Enter Topic", placeholder="Example: Operating Systems, Linked Lists, Thermodynamics...")
    else:
        fc_input = st.text_area("Paste Your Notes", placeholder="Paste your study notes here...", height=200)

    fc_count = st.slider("Number of flashcards", min_value=5, max_value=20, value=10, step=5)

    if st.button("Generate Flashcards 🃏", type="primary"):
        if fc_input.strip():
            with st.spinner("Creating flashcards..."):
                try:
                    source_label = f"topic: {fc_input}" if fc_mode == "A Topic" else f"the following notes:\n{fc_input}"
                    prompt = f"""Create exactly {fc_count} flashcards based on {source_label}.

Format each flashcard EXACTLY like this (no deviations):

**Card 1**
**Q:** Question here
**A:** Answer here

**Card 2**
**Q:** Question here
**A:** Answer here

...and so on up to Card {fc_count}.

Keep questions concise and answers clear (2–4 sentences max).
Make the questions test real understanding, not just definitions."""

                    result = gemini_generate(prompt)

                    # Parse and display as expandable cards
                    st.markdown("---")
                    st.markdown(f"### 🃏 Your {fc_count} Flashcards")

                    # Try to split into individual cards
                    import re
                    cards = re.split(r"\*\*Card\s+\d+\*\*", result)
                    cards = [c.strip() for c in cards if c.strip()]

                    if len(cards) >= 2:
                        for idx, card in enumerate(cards, 1):
                            # Extract Q and A
                            q_match = re.search(r"\*\*Q:\*\*\s*(.*?)(?=\*\*A:\*\*)", card, re.DOTALL)
                            a_match = re.search(r"\*\*A:\*\*\s*(.*)", card, re.DOTALL)
                            q_text = q_match.group(1).strip() if q_match else card
                            a_text = a_match.group(1).strip() if a_match else ""
                            with st.expander(f"Card {idx}: {q_text[:80]}{'...' if len(q_text) > 80 else ''}"):
                                st.markdown(f"**❓ Question:** {q_text}")
                                st.markdown(f"**✅ Answer:** {a_text}")
                    else:
                        # Fallback: show raw markdown
                        st.markdown(result)

                    # Download as text
                    st.download_button(
                        label="⬇️ Download Flashcards (.txt)",
                        data=result,
                        file_name="flashcards.txt",
                        mime="text/plain",
                    )
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("Please enter a topic or paste your notes.")

# ======================================
# TAB 9: PDF Q&A
# ======================================

with tab9:
    st.markdown("Upload a **PDF** (textbook chapter, notes, paper) and ask any question about its content.")

    if not GEMINI_KEY:
        st.error("⚠️ GEMINI_API_KEY is required. Add it in Space Settings.")
    else:
        pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

        if pdf_file:
            # Extract text from PDF using PyMuPDF
            if "pdf_text" not in st.session_state or st.session_state.get("pdf_name") != pdf_file.name:
                with st.spinner("Reading PDF..."):
                    try:
                        pdf_bytes = pdf_file.read()
                        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                        all_text = ""
                        for page in doc:
                            all_text += page.get_text()
                        doc.close()

                        # Limit to ~12,000 chars to stay within token limits
                        MAX_CHARS = 12000
                        if len(all_text) > MAX_CHARS:
                            all_text = all_text[:MAX_CHARS] + "\n\n[...content truncated for length...]"

                        st.session_state.pdf_text = all_text
                        st.session_state.pdf_name = pdf_file.name
                        st.session_state.pdf_qa_history = []
                    except Exception as e:
                        st.error(f"⚠️ Could not read PDF: {str(e)}")
                        st.stop()

            st.success(f"✅ **{pdf_file.name}** loaded — {len(st.session_state.pdf_text):,} characters extracted.")

            # Show a preview toggle
            with st.expander("👁️ Preview extracted text"):
                st.text(st.session_state.pdf_text[:1500] + "..." if len(st.session_state.pdf_text) > 1500 else st.session_state.pdf_text)

            st.markdown("---")
            st.markdown("### 💬 Ask questions about this PDF")

            # Show Q&A history
            if "pdf_qa_history" not in st.session_state:
                st.session_state.pdf_qa_history = []

            for item in st.session_state.pdf_qa_history:
                with st.chat_message("user"):
                    st.markdown(item["question"])
                with st.chat_message("assistant"):
                    st.markdown(item["answer"])

            pdf_question = st.chat_input("Ask a question about the PDF...")

            if pdf_question:
                with st.chat_message("user"):
                    st.markdown(pdf_question)

                with st.chat_message("assistant"):
                    answer_placeholder = st.empty()
                    full_answer = ""
                    try:
                        pdf_prompt = f"""You are an AI assistant. Answer the question based ONLY on the document content provided below.
If the answer is not in the document, say "I couldn't find that in the document."

--- DOCUMENT CONTENT ---
{st.session_state.pdf_text}
--- END OF DOCUMENT ---

Question: {pdf_question}

Give a clear, concise answer with markdown formatting where helpful."""

                        for chunk in gemini_stream(pdf_prompt):
                            full_answer += chunk
                            answer_placeholder.markdown(full_answer + "▌")
                        answer_placeholder.markdown(full_answer)
                    except Exception as e:
                        full_answer = f"⚠️ Error: {str(e)}"
                        answer_placeholder.markdown(full_answer)

                st.session_state.pdf_qa_history.append({
                    "question": pdf_question,
                    "answer": full_answer,
                })

            if st.session_state.get("pdf_qa_history"):
                if st.button("🗑️ Clear Q&A History"):
                    st.session_state.pdf_qa_history = []
                    st.rerun()
        else:
            st.info("👆 Upload a PDF to get started. Works great with textbook chapters, lecture notes, and research papers.")

            st.markdown("**💡 Example questions you can ask after uploading:**")
            example_qs = [
                "Summarize the main points of this document",
                "What are the key definitions mentioned?",
                "Explain the concept discussed on page 2",
                "List all the important formulas",
            ]
            for eq in example_qs:
                st.markdown(f"- *{eq}*")

# ======================================
# TAB 10: STUDY PLANNER
# ======================================

with tab10:
    st.markdown("Generate a **personalized study schedule** for any exam or set of topics.")

    col_a, col_b = st.columns(2)
    with col_a:
        exam_name = st.text_input("Exam / Subject Name", placeholder="Example: DBMS End-Sem, Data Structures Mid-Term...")
    with col_b:
        days_available = st.number_input("Days available to study", min_value=1, max_value=90, value=7, step=1)

    topics_input = st.text_area(
        "Topics to cover (one per line)",
        placeholder="Example:\nRelational Algebra\nSQL Queries\nNormalization\nTransactions & ACID\nIndexing & Hashing",
        height=150,
    )

    col_c, col_d = st.columns(2)
    with col_c:
        hours_per_day = st.slider("Study hours per day", min_value=1, max_value=12, value=4)
    with col_d:
        difficulty = st.selectbox("Your current level", ["Beginner", "Intermediate", "Advanced"])

    include_revision = st.checkbox("Include revision days at the end", value=True)

    if st.button("Generate Study Plan 📅", type="primary"):
        if exam_name.strip() and topics_input.strip():
            with st.spinner("Creating your personalized study plan..."):
                try:
                    topics_list = [t.strip() for t in topics_input.strip().splitlines() if t.strip()]
                    revision_note = "Reserve the last 1–2 days for full revision and practice tests." if include_revision else ""

                    prompt = f"""Create a detailed day-by-day study plan for an engineering student.

Exam/Subject: {exam_name}
Total days available: {days_available}
Study hours per day: {hours_per_day} hours
Student level: {difficulty}
Topics to cover:
{chr(10).join(f"- {t}" for t in topics_list)}
{revision_note}

Instructions:
- Distribute topics logically across the {days_available} days
- Harder topics should get more time
- Each day should have a clear title and hourly breakdown
- Include short breaks (e.g., 10 min every hour)
- Add a motivational tip at the end of each day
- {revision_note}

Format using markdown with:
- ## Day X: [Focus Topic]
- A table or bullet list of hourly slots
- A 💡 tip at the end of each day
- A final **Summary Table** at the end showing all days and topics"""

                    result = gemini_generate(prompt)
                    st.markdown("---")
                    st.markdown(f"### 📅 Study Plan for **{exam_name}**")
                    st.markdown(result)

                    st.download_button(
                        label="⬇️ Download Study Plan (.txt)",
                        data=result,
                        file_name=f"study_plan_{exam_name.replace(' ', '_')}.txt",
                        mime="text/plain",
                    )
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
        else:
            st.warning("Please fill in the exam name and at least one topic.")

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
