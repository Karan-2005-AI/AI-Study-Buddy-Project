import streamlit as st
import os
import base64
import io
import re
import json
import requests
import pymupdf  # PyMuPDF
from PIL import Image
import google.generativeai as genai_legacy
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# PROFESSIONAL CSS
# ==========================================

st.markdown("""
<style>
/* ---- Google Font ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ---- Root variables ---- */
:root {
    --primary:    #4f46e5;
    --primary-lt: #818cf8;
    --accent:     #06b6d4;
    --success:    #10b981;
    --warning:    #f59e0b;
    --danger:     #ef4444;
    --bg:         #0f172a;
    --surface:    #1e293b;
    --surface2:   #273349;
    --border:     #334155;
    --text:       #f1f5f9;
    --muted:      #94a3b8;
    --radius:     12px;
}

/* ---- Global ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ---- Hide default Streamlit chrome ---- */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 1100px; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ---- Tabs ---- */
[data-testid="stTabs"] [data-testid="stTab"] {
    background: var(--surface2) !important;
    color: var(--muted) !important;
    border-radius: 8px 8px 0 0 !important;
    border: 1px solid var(--border) !important;
    border-bottom: none !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 8px 14px !important;
    margin-right: 4px !important;
    transition: all 0.2s;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
    border-color: var(--primary) !important;
}
[data-testid="stTabsContent"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 var(--radius) var(--radius) var(--radius) !important;
    padding: 1.5rem !important;
}

/* ---- Inputs ---- */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] > div,
[data-testid="stNumberInput"] input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-size: 14px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.2) !important;
}

/* ---- Buttons ---- */
[data-testid="stButton"] > button {
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.5rem 1.25rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.3px;
}
[data-testid="stButton"] > button:hover {
    background: #4338ca !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79,70,229,0.4) !important;
}

/* ---- Metric cards ---- */
[data-testid="stMetric"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: var(--primary-lt) !important; font-size: 28px !important; font-weight: 700 !important; }

/* ---- Expander ---- */
[data-testid="stExpander"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ---- Info / Success / Error / Warning ---- */
[data-testid="stAlert"] { border-radius: var(--radius) !important; }

/* ---- Dataframe ---- */
[data-testid="stDataFrame"] { border-radius: var(--radius) !important; overflow: hidden; }

/* ---- Chat messages ---- */
[data-testid="stChatMessage"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 0.5rem !important;
}

/* ---- Code blocks ---- */
pre, code {
    background: #0d1117 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* ---- Spinner ---- */
[data-testid="stSpinner"] { color: var(--primary-lt) !important; }

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ---- Feature card grid ---- */
.feat-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.feat-card:hover { border-color: var(--primary); }
.feat-card h4 { margin: 0 0 4px 0; color: var(--text); font-size: 15px; }
.feat-card p  { margin: 0; color: var(--muted); font-size: 13px; }

/* ---- Badge ---- */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.badge-blue   { background: rgba(79,70,229,0.2);  color: var(--primary-lt); }
.badge-green  { background: rgba(16,185,129,0.2); color: #34d399; }
.badge-orange { background: rgba(245,158,11,0.2); color: #fcd34d; }
.badge-red    { background: rgba(239,68,68,0.2);  color: #fca5a5; }

/* ---- Section heading ---- */
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-sub {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 1.25rem;
}

/* ---- Divider ---- */
hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }

/* ---- Sidebar nav links ---- */
.nav-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    border-radius: 8px;
    color: var(--muted);
    font-size: 13px;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.15s;
    cursor: pointer;
    margin-bottom: 2px;
}
.nav-link:hover, .nav-link.active {
    background: rgba(79,70,229,0.15);
    color: var(--primary-lt);
}
.nav-section {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--muted);
    padding: 12px 16px 4px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# API SETUP
# ==========================================

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN   = os.getenv("HF_TOKEN")
NEWS_KEY   = os.getenv("NEWS_API_KEY")

CHAT_MODEL      = "gemini-2.5-flash"
IMAGE_VIS_MODEL = "gemini-2.5-flash"

HF_IMG_GEN_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
HF_IMG_CAP_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
HF_VQA_URL     = "https://api-inference.huggingface.co/models/dandelin/vilt-b32-finetuned-vqa"

# Support both old (AIzaSy...) and new (AQ....) Gemini API key formats
if GEMINI_KEY:
    try:
        client = genai.Client(api_key=GEMINI_KEY)
    except Exception:
        client = None
else:
    client = None

# Configure legacy SDK as fallback for new AQ. key format
if GEMINI_KEY:
    genai_legacy.configure(api_key=GEMINI_KEY)

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

def _use_legacy():
    """Use legacy SDK when new client fails (AQ. key format)."""
    model = genai_legacy.GenerativeModel(
        model_name=CHAT_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )
    return model


def gemini_stream(prompt, history=None):
    # Try new SDK first, fall back to legacy
    try:
        contents = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
        contents.append(types.Content(role="user", parts=[types.Part(text=prompt)]))
        response = client.models.generate_content_stream(
            model=CHAT_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception:
        # Legacy SDK fallback
        model = _use_legacy()
        chat_history = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text


def gemini_generate(prompt):
    # Try new SDK first, fall back to legacy
    try:
        response = client.models.generate_content(
            model=CHAT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        return response.text
    except Exception:
        model = _use_legacy()
        response = model.generate_content(prompt)
        return response.text


def hf_headers():
    if HF_TOKEN:
        return {"Authorization": f"Bearer {HF_TOKEN}"}
    return {}


def hf_generate_image(prompt):
    payload = {"inputs": prompt}
    response = requests.post(HF_IMG_GEN_URL, headers=hf_headers(), json=payload, timeout=60)
    if response.status_code == 200:
        return response.content
    raise RuntimeError(f"HF Image Generation failed ({response.status_code}): {response.text[:200]}")


def hf_analyze_image(image_bytes, question=None):
    if question and question.strip():
        img_b64 = base64.b64encode(image_bytes).decode()
        payload = {"inputs": {"image": img_b64, "question": question}}
        response = requests.post(HF_VQA_URL, headers=hf_headers(), json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                return "\n".join(f"**{d.get('answer','?')}** (score: {d.get('score',0):.2f})" for d in data[:3])
            return str(data)
    response = requests.post(HF_IMG_CAP_URL, headers=hf_headers(), data=image_bytes, timeout=30)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            return data[0].get("generated_text", str(data))
        return str(data)
    raise RuntimeError(f"HF Image Analysis failed ({response.status_code}): {response.text[:200]}")


def section_header(icon, title, subtitle=""):
    st.markdown(f'<div class="section-title">{icon} {title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 10px; border-bottom:1px solid var(--border); margin-bottom:8px;">
        <div style="font-size:22px; font-weight:800; color:#f1f5f9; letter-spacing:-0.5px;">
            🎓 AI Study Buddy
        </div>
        <div style="font-size:11px; color:#94a3b8; margin-top:2px;">Powered by Gemini & Hugging Face</div>
    </div>
    """, unsafe_allow_html=True)

    if not GEMINI_KEY:
        st.error("⚠️ Set **GEMINI_API_KEY** in Space secrets to start.")
        st.stop()

    # Quick stats
    chat_msgs  = len(st.session_state.get("messages", []))
    note_count = len(st.session_state.get("sticky_notes", []))
    st.markdown(f"""
    <div style="display:flex; gap:8px; padding:8px 16px; margin-bottom:4px;">
        <div style="flex:1; background:rgba(79,70,229,0.15); border-radius:8px; padding:8px; text-align:center;">
            <div style="font-size:18px; font-weight:700; color:#818cf8;">{chat_msgs}</div>
            <div style="font-size:10px; color:#94a3b8;">Chats</div>
        </div>
        <div style="flex:1; background:rgba(16,185,129,0.15); border-radius:8px; padding:8px; text-align:center;">
            <div style="font-size:18px; font-weight:700; color:#34d399;">{note_count}</div>
            <div style="font-size:10px; color:#94a3b8;">Notes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section">🧠 Learning</div>', unsafe_allow_html=True)
    for label in ["💬 AI Chat", "📚 Concept Explainer", "📐 Formula Explorer", "🗺️ Mind Map", "🎓 Interview Prep"]:
        st.markdown(f'<div class="nav-link">{label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="nav-section">📝 Writing & Study</div>', unsafe_allow_html=True)
    for label in ["📝 Notes Summarizer", "🧠 Quiz Generator", "🃏 Flashcards", "📋 Assignment Helper", "📝 Essay Writer", "📌 Presentation"]:
        st.markdown(f'<div class="nav-link">{label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="nav-section">💻 Code Tools</div>', unsafe_allow_html=True)
    for label in ["💻 Code Helper", "🐛 Code Debugger", "🔄 Code Converter", "🧪 Unit Test Gen"]:
        st.markdown(f'<div class="nav-link">{label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="nav-section">🛠️ Utilities</div>', unsafe_allow_html=True)
    for label in ["📄 PDF Q&A", "🌐 Translator", "📊 Data Visualizer", "🎨 Image Generator", "📷 Image Analyzer", "📰 News", "📅 Study Planner", "📖 Dictionary"]:
        st.markdown(f'<div class="nav-link">{label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="nav-section">⚡ Productivity</div>', unsafe_allow_html=True)
    for label in ["🎙️ Speech Tools", "⏱️ Pomodoro Timer", "🗒️ Sticky Notes", "✍️ Grammar Checker", "🔢 Math Solver", "📈 Dashboard", "💡 Motivation"]:
        st.markdown(f'<div class="nav-link">{label}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="padding:0 16px 16px; font-size:11px; color:#64748b; line-height:1.6;">
        Built by <b style="color:#94a3b8;">Karan Dewangan</b><br>
        B.Tech CS (AIML) · Chouksey Engineering College<br>
        Minor Project Phase 1 · Lenovo Leap
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN HEADER
# ==========================================

st.markdown("""
<div style="background:linear-gradient(135deg,#1e1b4b 0%,#1e293b 60%,#0c4a6e 100%);
     border:1px solid #334155; border-radius:16px; padding:28px 32px; margin-bottom:1.5rem;
     display:flex; align-items:center; justify-content:space-between;">
    <div>
        <div style="font-size:30px; font-weight:800; color:#f1f5f9; letter-spacing:-1px; line-height:1.1;">
            🎓 AI Study Buddy
        </div>
        <div style="font-size:14px; color:#94a3b8; margin-top:6px;">
            Your all-in-one intelligent study platform · 35 AI-powered features
        </div>
        <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
            <span class="badge badge-blue">Gemini 2.5 Flash</span>
            <span class="badge badge-green">FLUX.1 Image Gen</span>
            <span class="badge badge-orange">25 Study Tools</span>
            <span class="badge badge-red">Free on HF Spaces</span>
        </div>
    </div>
    <div style="font-size:72px; opacity:0.15;">🎓</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# TABS — ALL 35 FEATURES
# ==========================================

(tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10,
 tab11, tab12, tab13, tab14, tab15, tab16, tab17, tab18, tab19, tab20,
 tab21, tab22, tab23, tab24, tab25, tab26, tab27, tab28, tab29, tab30,
 tab31, tab32, tab33, tab34, tab35) = st.tabs([
    "💬 Chat",
    "🎨 Image Gen",
    "📷 Analyzer",
    "📚 Explainer",
    "📝 Summarizer",
    "🧠 Quiz",
    "💻 Code",
    "🃏 Flashcards",
    "📄 PDF Q&A",
    "📅 Planner",
    "🌐 Translator",
    "🗺️ Mind Map",
    "📐 Formulas",
    "🎙️ Speech",
    "📊 Visualizer",
    "📰 News",
    "🐛 Debugger",
    "🔄 Converter",
    "🧪 Unit Tests",
    "📋 Assignment",
    "✍️ Essay",
    "📌 Slides",
    "⏱️ Pomodoro",
    "🗒️ Notes",
    "📈 Dashboard",
    "✏️ Grammar",
    "🎓 Interview",
    "🔢 Math",
    "📖 Dictionary",
    "📑 Resume",
    "🗓️ Timetable",
    "💡 Motivation",
    "🔍 Research",
    "📃 Plagiarism",
    "🧬 Topic Path",
])

# ==============================
# TAB 1: AI CHAT
# ==============================
with tab1:
    section_header("💬", "AI Chat", "Ask anything — study topics, coding help, or just have a conversation.")

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
            ph = st.empty()
            full = ""
            try:
                for chunk in gemini_stream(prompt, st.session_state.messages[:-1]):
                    full += chunk
                    ph.markdown(full + "▌")
                ph.markdown(full)
            except Exception as e:
                full = f"⚠️ {e}"
                ph.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🗑️ Clear"):
            st.session_state.messages = []
            st.rerun()

    st.markdown("**💡 Quick prompts:**")
    examples = [
        "Explain machine learning simply", "Difference between AI, ML and Deep Learning",
        "Binary search in Python", "OSI model explained", "What is Big O notation?",
        "How does a neural network learn?",
    ]
    ec = st.columns(3)
    for i, ex in enumerate(examples):
        if ec[i % 3].button(ex, key=f"ex_{i}"):
            st.session_state.pending_prompt = ex
            st.rerun()

# ==============================
# TAB 2: IMAGE GENERATOR
# ==============================
with tab2:
    section_header("🎨", "Image Generator", "Generate images from text using FLUX.1-schnell on Hugging Face (free).")
    img_prompt = st.text_area("Describe the image", placeholder="A futuristic classroom with AI robots teaching students, digital art style", height=100)
    if st.button("Generate Image 🎨", type="primary"):
        if img_prompt.strip():
            with st.spinner("Generating via Hugging Face FLUX.1-schnell..."):
                try:
                    img_bytes = hf_generate_image(img_prompt)
                    st.image(img_bytes, caption=img_prompt, use_container_width=True)
                    st.download_button("⬇️ Download Image", data=img_bytes, file_name="generated.png", mime="image/png")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Please enter a description.")
    st.info("💡 Model: **FLUX.1-schnell** (black-forest-labs) via HF Inference API. Add `HF_TOKEN` secret for better rate limits.")
    st.markdown("**Example prompts:**")
    for ex in ["Neural network diagram, educational style", "Binary search tree visualization", "OSI model colorful infographic"]:
        st.code(ex, language=None)

# ==============================
# TAB 3: IMAGE ANALYZER
# ==============================
with tab3:
    section_header("📷", "Image Analyzer", "Upload any image and analyze it using BLIP captioning + ViLT VQA (Hugging Face, free).")
    uf = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "webp"])
    if uf:
        st.image(uf, caption="Uploaded", use_container_width=True)
        ap = st.text_input("Ask about this image (blank = auto-describe)", placeholder="What does this diagram show?")
        if st.button("Analyze 🔍", type="primary"):
            with st.spinner("Analyzing via Hugging Face..."):
                try:
                    result = hf_analyze_image(uf.read(), ap)
                    st.markdown("### Result")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
    else:
        st.info("👆 Upload diagrams, handwritten notes, flowcharts, screenshots, etc.")

# ==============================
# TAB 4: CONCEPT EXPLAINER
# ==============================
with tab4:
    section_header("📚", "Concept Explainer", "Get a clear, structured explanation of any topic for engineering students.")
    topic = st.text_input("Enter topic", placeholder="Machine Learning, Recursion, Dijkstra's Algorithm...")
    detail = st.radio("Detail level", ["Brief overview", "Standard explanation", "In-depth with examples"], horizontal=True)
    if st.button("Explain ✨", type="primary"):
        if topic.strip():
            with st.spinner("Explaining..."):
                try:
                    depth_map = {"Brief overview": "briefly in 150 words", "Standard explanation": "clearly with examples",
                                 "In-depth with examples": "in depth with multiple examples and diagrams described in text"}
                    result = gemini_generate(f"""Explain this topic {depth_map[detail]} for engineering students.
Topic: {topic}
Include: simple definition, key points, real-world application, short conclusion.
Use markdown formatting.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Please enter a topic.")

# ==============================
# TAB 5: NOTES SUMMARIZER
# ==============================
with tab5:
    section_header("📝", "Notes Summarizer", "Paste lengthy study notes and get a concise bullet-point summary.")
    notes = st.text_area("Paste your notes", height=250, placeholder="Paste your study notes here...")
    smode = st.radio("Summary style", ["Bullet points", "Paragraph summary", "Key terms only", "Mind map style"], horizontal=True)
    if st.button("Summarize 📋", type="primary"):
        if notes.strip():
            with st.spinner("Summarizing..."):
                try:
                    style_map = {
                        "Bullet points": "Use short bullet points with **bold** for key terms.",
                        "Paragraph summary": "Write a flowing paragraph summary keeping it concise.",
                        "Key terms only": "Extract only the key terms and their one-line definitions as a list.",
                        "Mind map style": "Format as a hierarchical text mind map showing concept relationships.",
                    }
                    result = gemini_generate(f"""Summarize these study notes for an engineering student.
Style: {style_map[smode]}
Do not add information not present in the notes.
Notes:\n{notes}""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Summary", data=result, file_name="summary.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Please paste your notes.")

# ==============================
# TAB 6: QUIZ GENERATOR
# ==============================
with tab6:
    section_header("🧠", "Quiz Generator", "Generate MCQ, True/False, or short-answer questions on any topic.")
    quiz_topic = st.text_input("Topic", placeholder="Artificial Intelligence, Data Structures, DBMS...", key="quiz_topic")
    qc1, qc2, qc3 = st.columns(3)
    quiz_count = qc1.slider("Questions", 5, 20, 5, 5)
    quiz_type  = qc2.selectbox("Question type", ["MCQ (4 options)", "True/False", "Short Answer", "Mixed"])
    quiz_diff  = qc3.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
    if st.button("Generate Quiz 🎯", type="primary"):
        if quiz_topic.strip():
            with st.spinner("Generating..."):
                try:
                    result = gemini_generate(f"""Create {quiz_count} {quiz_type} questions on: {quiz_topic}
Difficulty: {quiz_diff}
For MCQ: provide 4 options (A-D) per question.
For True/False: state the fact clearly.
For Short Answer: ask a specific factual question.
After all questions, provide a complete Answer Key.
Use markdown formatting. Keep questions suitable for engineering students.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Quiz", data=result, file_name="quiz.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Please enter a topic.")

# ==============================
# TAB 7: CODE HELPER
# ==============================
with tab7:
    section_header("💻", "Code Helper", "Describe any coding problem and get a complete solution with explanation.")
    cc1, cc2 = st.columns([1, 3])
    language = cc1.selectbox("Language", ["Python", "C", "C++", "Java", "JavaScript", "SQL", "TypeScript", "Go", "Rust", "Other"])
    problem  = cc2.text_area("Describe problem", height=100, placeholder="Write a program to find the factorial using recursion...")
    code_mode = st.radio("Mode", ["Write new code", "Explain existing code", "Optimize code"], horizontal=True)
    if st.button("Solve 🔧", type="primary"):
        if problem.strip():
            with st.spinner("Processing..."):
                try:
                    mode_map = {
                        "Write new code": f"Write complete {language} code for this problem with explanation:",
                        "Explain existing code": f"Explain this {language} code line by line:",
                        "Optimize code": f"Optimize this {language} code and explain the improvements:",
                    }
                    result = gemini_generate(f"""{mode_map[code_mode]}

{problem}

Include:
1. Clear approach explanation
2. Complete working code with comments
3. Key line explanations
4. Time/space complexity
Use proper markdown code blocks.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Please describe your problem.")

# ==============================
# TAB 8: FLASHCARD GENERATOR
# ==============================
with tab8:
    section_header("🃏", "Flashcard Generator", "Generate Q&A flashcards from any topic or notes for quick revision.")
    fc_mode  = st.radio("Source", ["A Topic", "My Notes"], horizontal=True)
    fc_input = st.text_input("Enter topic", placeholder="Operating Systems, Linked Lists...") if fc_mode == "A Topic" else st.text_area("Paste notes", height=180)
    fc1, fc2 = st.columns(2)
    fc_count = fc1.slider("Number of cards", 5, 20, 10, 5)
    fc_style = fc2.selectbox("Card style", ["Q&A (Question & Answer)", "Term & Definition", "Fill in the blank"])
    if st.button("Generate Flashcards 🃏", type="primary"):
        if fc_input.strip():
            with st.spinner("Creating flashcards..."):
                try:
                    src = f"topic: {fc_input}" if fc_mode == "A Topic" else f"notes:\n{fc_input}"
                    result = gemini_generate(f"""Create exactly {fc_count} {fc_style} flashcards from {src}.
Format EXACTLY:
**Card 1**
**Q:** Question
**A:** Answer
...up to Card {fc_count}.
Answers should be 2-4 sentences. Test real understanding.""")
                    st.markdown(f"### Your {fc_count} Flashcards")
                    cards = re.split(r"\*\*Card\s+\d+\*\*", result)
                    cards = [c.strip() for c in cards if c.strip()]
                    if len(cards) >= 2:
                        for idx, card in enumerate(cards, 1):
                            qm = re.search(r"\*\*Q:\*\*\s*(.*?)(?=\*\*A:\*\*)", card, re.DOTALL)
                            am = re.search(r"\*\*A:\*\*\s*(.*)", card, re.DOTALL)
                            qt = qm.group(1).strip() if qm else card
                            at = am.group(1).strip() if am else ""
                            with st.expander(f"Card {idx}: {qt[:75]}{'...' if len(qt)>75 else ''}"):
                                st.markdown(f"**❓** {qt}")
                                st.markdown(f"**✅** {at}")
                    else:
                        st.markdown(result)
                    st.download_button("⬇️ Download Flashcards", data=result, file_name="flashcards.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Please enter a topic or notes.")

# ==============================
# TAB 9: PDF Q&A
# ==============================
with tab9:
    section_header("📄", "PDF Q&A", "Upload any PDF and have a conversation about its content.")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file:
        if "pdf_text" not in st.session_state or st.session_state.get("pdf_name") != pdf_file.name:
            with st.spinner("Extracting text..."):
                try:
                    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
                    text = "".join(page.get_text() for page in doc)
                    doc.close()
                    if len(text) > 12000:
                        text = text[:12000] + "\n\n[...truncated...]"
                    st.session_state.pdf_text = text
                    st.session_state.pdf_name = pdf_file.name
                    st.session_state.pdf_qa_history = []
                except Exception as e:
                    st.error(f"⚠️ {e}"); st.stop()
        st.success(f"✅ **{pdf_file.name}** — {len(st.session_state.pdf_text):,} chars extracted.")
        with st.expander("👁️ Preview text"):
            st.text(st.session_state.pdf_text[:1500] + "...")
        for item in st.session_state.get("pdf_qa_history", []):
            with st.chat_message("user"):    st.markdown(item["question"])
            with st.chat_message("assistant"): st.markdown(item["answer"])
        pq = st.chat_input("Ask about the PDF...")
        if pq:
            with st.chat_message("user"): st.markdown(pq)
            with st.chat_message("assistant"):
                ph = st.empty(); ans = ""
                try:
                    for chunk in gemini_stream(f"""Answer based ONLY on this document. If not found say so.
--- DOCUMENT ---\n{st.session_state.pdf_text}\n--- END ---\nQuestion: {pq}\nUse markdown."""):
                        ans += chunk; ph.markdown(ans + "▌")
                    ph.markdown(ans)
                except Exception as e:
                    ans = f"⚠️ {e}"; ph.markdown(ans)
            st.session_state.pdf_qa_history.append({"question": pq, "answer": ans})
        if st.session_state.get("pdf_qa_history"):
            if st.button("🗑️ Clear History"): st.session_state.pdf_qa_history = []; st.rerun()
    else:
        st.info("Upload a PDF textbook chapter, lecture notes, or research paper to start.")

# ==============================
# TAB 10: STUDY PLANNER
# ==============================
with tab10:
    section_header("📅", "Study Planner", "Generate a personalized day-by-day study schedule for any exam.")
    pc1, pc2 = st.columns(2)
    exam_name     = pc1.text_input("Exam / Subject", placeholder="DBMS End-Sem, Data Structures Mid-Term...")
    days_avail    = pc2.number_input("Days available", min_value=1, max_value=90, value=7)
    topics_input  = st.text_area("Topics (one per line)", height=130, placeholder="Relational Algebra\nSQL Queries\nNormalization")
    pc3, pc4, pc5 = st.columns(3)
    hours_pd   = pc3.slider("Hours/day", 1, 12, 4)
    difficulty = pc4.selectbox("Your level", ["Beginner", "Intermediate", "Advanced"])
    plan_style = pc5.selectbox("Plan style", ["Detailed hourly", "Topic-wise blocks", "Flexible goals"])
    inc_rev    = st.checkbox("Include revision days", value=True)
    if st.button("Generate Plan 📅", type="primary"):
        if exam_name.strip() and topics_input.strip():
            with st.spinner("Building plan..."):
                try:
                    tl = [t.strip() for t in topics_input.splitlines() if t.strip()]
                    result = gemini_generate(f"""Create a {plan_style} study plan for an engineering student.
Exam: {exam_name} | Days: {days_avail} | Hours/day: {hours_pd} | Level: {difficulty}
Topics: {', '.join(tl)}
{'Include revision days at the end.' if inc_rev else ''}
Use ## Day X: headings, hourly schedule, 💡 tip per day, final Summary Table.""")
                    st.markdown(f"### Study Plan: {exam_name}")
                    st.markdown(result)
                    st.download_button("⬇️ Download Plan", data=result, file_name=f"plan_{exam_name[:20]}.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Fill exam name and at least one topic.")

# ==============================
# TAB 11: LANGUAGE TRANSLATOR
# ==============================
with tab11:
    section_header("🌐", "Language Translator", "Translate any text, notes or concepts into 24+ languages.")
    LANGUAGES = ["Hindi", "French", "Spanish", "German", "Japanese", "Chinese (Simplified)",
                 "Arabic", "Portuguese", "Russian", "Bengali", "Tamil", "Telugu", "Marathi",
                 "Gujarati", "Kannada", "Malayalam", "Punjabi", "Urdu", "Korean", "Italian",
                 "Dutch", "Turkish", "Polish", "Swedish", "Vietnamese", "Thai", "Indonesian"]
    tc1, tc2 = st.columns([2, 1])
    with tc1:
        trans_text = st.text_area("Text to translate", height=200, key="trans_input", placeholder="Paste any text, notes, or concept...")
    with tc2:
        tgt_lang    = st.selectbox("Target language", LANGUAGES)
        keep_fmt    = st.checkbox("Keep markdown formatting", value=True)
        simplify    = st.checkbox("Simplify for beginners", value=False)
        formal      = st.checkbox("Formal/Academic tone", value=False)
    if st.button("Translate 🌐", type="primary"):
        if trans_text.strip():
            with st.spinner(f"Translating to {tgt_lang}..."):
                try:
                    extras = []
                    if keep_fmt: extras.append("Preserve all markdown formatting.")
                    if simplify: extras.append("Simplify content for a beginner.")
                    if formal:   extras.append("Use formal/academic tone.")
                    result = gemini_generate(f"""Translate to {tgt_lang}. {' '.join(extras)} Return ONLY the translation.
Text:\n{trans_text}""")
                    st.markdown("### Translation")
                    st.markdown(result)
                    st.download_button("⬇️ Download", data=result, file_name=f"translation_{tgt_lang}.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter text to translate.")

# ==============================
# TAB 12: MIND MAP
# ==============================
with tab12:
    section_header("🗺️", "Mind Map Generator", "Visualize any topic as a structured text mind map.")
    mm_topic = st.text_input("Topic", placeholder="Machine Learning, Database Management, Thermodynamics...")
    md1, md2 = st.columns(2)
    mm_depth = md1.radio("Depth", ["2 levels", "3 levels", "4 levels"], horizontal=True)
    mm_focus = md2.text_input("Focus area (optional)", placeholder="Focus on algorithms only...")
    if st.button("Generate Mind Map 🗺️", type="primary"):
        if mm_topic.strip():
            with st.spinner("Building..."):
                try:
                    dv = int(mm_depth[0])
                    focus_note = f"Focus specifically on: {mm_focus}" if mm_focus.strip() else ""
                    result = gemini_generate(f"""Create a {dv}-level mind map for: {mm_topic}. {focus_note}
Use tree characters (├──, └──, │). Add emojis to main branches. 4-6 main branches, 2-4 sub-topics each.
After the tree, add a Key Takeaways section with 3-5 bullets.""")
                    st.code(result, language=None)
                    with st.expander("📖 Formatted view"):
                        st.markdown(result)
                    st.download_button("⬇️ Download", data=result, file_name=f"mindmap_{mm_topic[:20]}.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a topic.")

# ==============================
# TAB 13: FORMULA EXPLORER
# ==============================
with tab13:
    section_header("📐", "Formula Explorer", "Look up formulas with definitions, worked examples, and applications.")
    SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Statistics", "Engineering Mathematics",
                "Electronics", "Thermodynamics", "Fluid Mechanics", "Electrical Circuits", "Signal Processing",
                "Structural Engineering", "Control Systems"]
    fe1, fe2 = st.columns([2, 1])
    formula_q   = fe1.text_input("Formula or topic", placeholder="Quadratic Formula, Newton's Laws, Ohm's Law...")
    formula_sub = fe2.selectbox("Subject", SUBJECTS)
    fe3, fe4   = st.columns(2)
    explain_lv  = fe3.radio("Level", ["Simple (Class 12)", "Engineering", "Advanced"], horizontal=True)
    show_proof  = fe4.checkbox("Include derivation/proof", value=False)
    if st.button("Explore 📐", type="primary"):
        if formula_q.strip():
            with st.spinner("Fetching..."):
                try:
                    proof_note = "Also include the mathematical derivation or proof." if show_proof else ""
                    result = gemini_generate(f"""Explain the formula for a {explain_lv} student.
Subject: {formula_sub} | Formula: {formula_q}
Provide: 1) Formula clearly written 2) Symbol meanings 3) Plain-English explanation
4) Step-by-step numerical example 5) Real-world application 6) Related formulas. {proof_note}
Use clear markdown.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a formula or topic.")

# ==============================
# TAB 14: SPEECH TOOLS
# ==============================
with tab14:
    section_header("🎙️", "Speech Tools", "Speech-to-Text and Text-to-Speech powered by the browser's Web Speech API.")
    smode = st.radio("Mode", ["🎙️ Speech to Text", "🔊 Text to Speech"], horizontal=True)

    if smode == "🎙️ Speech to Text":
        st.info("Uses your browser's built-in microphone. Works best in Chrome/Edge.")
        st.components.v1.html("""
        <div style="text-align:center;padding:16px;background:#1e293b;border-radius:12px;border:1px solid #334155;">
            <button id="startBtn" onclick="startRec()"
                style="background:#4f46e5;color:white;border:none;padding:12px 28px;border-radius:8px;font-size:15px;cursor:pointer;margin:5px;font-weight:600;">
                🎙️ Start Recording</button>
            <button id="stopBtn" onclick="stopRec()" disabled
                style="background:#ef4444;color:white;border:none;padding:12px 28px;border-radius:8px;font-size:15px;cursor:pointer;margin:5px;font-weight:600;">
                ⏹️ Stop</button>
            <p id="status" style="color:#94a3b8;margin:10px 0 6px;">Click Start to begin speaking...</p>
            <textarea id="transcript" rows="6"
                style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#f1f5f9;font-size:14px;resize:vertical;"
                placeholder="Your speech will appear here..."></textarea>
            <br>
            <button onclick="navigator.clipboard.writeText(document.getElementById('transcript').value);document.getElementById('status').innerText='✅ Copied!'"
                style="background:#10b981;color:white;border:none;padding:8px 20px;border-radius:6px;font-size:13px;cursor:pointer;margin-top:10px;font-weight:600;">
                📋 Copy Text</button>
        </div>
        <script>
        let rec;
        function startRec(){
            if(!('webkitSpeechRecognition' in window||'SpeechRecognition' in window)){
                document.getElementById('status').innerText='❌ Not supported. Use Chrome or Edge.';return;
            }
            rec=new(window.SpeechRecognition||window.webkitSpeechRecognition)();
            rec.continuous=true;rec.interimResults=true;rec.lang='en-US';
            rec.onstart=()=>{document.getElementById('startBtn').disabled=true;document.getElementById('stopBtn').disabled=false;document.getElementById('status').innerText='🔴 Recording...';};
            rec.onresult=e=>{let t='';for(let i=0;i<e.results.length;i++)t+=e.results[i][0].transcript;document.getElementById('transcript').value=t;};
            rec.onerror=e=>{document.getElementById('status').innerText='⚠️ '+e.error;};
            rec.onend=()=>{document.getElementById('startBtn').disabled=false;document.getElementById('stopBtn').disabled=true;document.getElementById('status').innerText='✅ Done. Copy the text.';};
            rec.start();
        }
        function stopRec(){if(rec)rec.stop();}
        </script>""", height=300)

    else:
        tts_text = st.text_area("Text to speak", height=150, placeholder="Paste study notes, formula explanations...")
        t1, t2, t3 = st.columns(3)
        tts_rate  = t1.slider("Speed", 0.5, 2.0, 1.0, 0.1)
        tts_pitch = t2.slider("Pitch", 0.5, 2.0, 1.0, 0.1)
        tts_lang  = t3.selectbox("Language", ["en-US","en-GB","hi-IN","fr-FR","de-DE","ja-JP","zh-CN","es-ES","ar-SA"])
        if tts_text.strip():
            safe = tts_text.replace("\\","\\\\").replace("`","\\`").replace("'","\\'").replace('"','\\"').replace("\n"," ")
            st.components.v1.html(f"""
            <div style="text-align:center;padding:16px;background:#1e293b;border-radius:12px;border:1px solid #334155;">
                <button onclick="speak()" style="background:#4f46e5;color:white;border:none;padding:12px 24px;border-radius:8px;font-size:15px;cursor:pointer;margin:4px;font-weight:600;">▶️ Play</button>
                <button onclick="window.speechSynthesis.pause()" style="background:#f59e0b;color:white;border:none;padding:12px 24px;border-radius:8px;font-size:15px;cursor:pointer;margin:4px;font-weight:600;">⏸️ Pause</button>
                <button onclick="window.speechSynthesis.cancel()" style="background:#ef4444;color:white;border:none;padding:12px 24px;border-radius:8px;font-size:15px;cursor:pointer;margin:4px;font-weight:600;">⏹️ Stop</button>
                <p id="s" style="color:#94a3b8;margin-top:10px;">Click Play to listen</p>
            </div>
            <script>
            function speak(){{
                window.speechSynthesis.cancel();
                const u=new SpeechSynthesisUtterance("{safe}");
                u.rate={tts_rate};u.pitch={tts_pitch};u.lang="{tts_lang}";
                u.onstart=()=>document.getElementById('s').innerText='🔊 Playing...';
                u.onend=()=>document.getElementById('s').innerText='✅ Done';
                window.speechSynthesis.speak(u);
            }}
            </script>""", height=140)
        else:
            st.info("Enter text above to enable playback controls.")

# ==============================
# TAB 15: DATA VISUALIZER
# ==============================
with tab15:
    section_header("📊", "Data Visualizer", "Paste CSV/table data and instantly create interactive charts with AI insight.")
    viz_data = st.text_area("Paste CSV data (first row = headers)", height=160,
                            placeholder="Subject, Score\nMath, 85\nPhysics, 72\nChemistry, 90")
    vc1, vc2, vc3, vc4 = st.columns(4)
    chart_type  = vc1.selectbox("Chart type", ["Bar", "Pie", "Line", "Horizontal Bar", "Scatter", "Area", "Funnel", "Radar"])
    chart_title = vc2.text_input("Title", placeholder="My Chart")
    color_theme = vc3.selectbox("Theme", ["plotly_dark", "plotly", "ggplot2", "seaborn", "simple_white"])
    show_ai     = vc4.checkbox("AI insight", value=True)
    if st.button("Visualize 📊", type="primary"):
        if viz_data.strip():
            try:
                df = pd.read_csv(StringIO(viz_data.strip()))
                df.columns = [c.strip() for c in df.columns]
                for col in df.columns:
                    if df[col].dtype == object:
                        df[col] = df[col].str.strip()
                st.dataframe(df, use_container_width=True)
                x, y = df.columns[0], df.columns[1] if len(df.columns) > 1 else df.columns[0]
                title = chart_title or f"{y} by {x}"
                fig = None
                if chart_type == "Bar":           fig = px.bar(df, x=x, y=y, title=title, template=color_theme, color=x)
                elif chart_type == "Pie":          fig = px.pie(df, names=x, values=y, title=title, template=color_theme)
                elif chart_type == "Line":         fig = px.line(df, x=x, y=y, title=title, template=color_theme, markers=True)
                elif chart_type == "Horizontal Bar": fig = px.bar(df, x=y, y=x, title=title, template=color_theme, orientation="h", color=x)
                elif chart_type == "Scatter":      fig = px.scatter(df, x=x, y=y, title=title, template=color_theme, text=x)
                elif chart_type == "Area":         fig = px.area(df, x=x, y=y, title=title, template=color_theme)
                elif chart_type == "Funnel":       fig = px.funnel(df, x=y, y=x, title=title, template=color_theme)
                elif chart_type == "Radar":
                    fig = go.Figure(go.Scatterpolar(r=df[y].tolist(), theta=df[x].tolist(), fill="toself"))
                    fig.update_layout(title=title, template=color_theme)
                if fig:
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                if show_ai:
                    with st.spinner("Generating AI insight..."):
                        try:
                            ins = gemini_generate(f"Analyze this data briefly (3-5 sentences). Highlight max, min, trends:\n{viz_data}")
                            st.markdown("**🤖 AI Insight:**")
                            st.info(ins)
                        except Exception:
                            pass
            except Exception as e:
                st.error(f"⚠️ Parse error: {e}")
        else:
            st.warning("Paste some data first.")

# ==============================
# TAB 16: NEWS UPDATES
# ==============================
with tab16:
    section_header("📰", "News Updates", "Get AI-summarized news or live articles on any topic.")
    nc1, nc2 = st.columns([2, 1])
    news_topic  = nc1.text_input("Search topic", placeholder="Artificial Intelligence, Python, Space, Climate...")
    news_count  = nc2.slider("Items", 3, 10, 5)
    news_source = st.radio("Source", ["AI Summary (Gemini)", "Live News (NewsAPI key required)"], horizontal=True)
    if st.button("Get News 📰", type="primary"):
        if news_topic.strip():
            if news_source == "AI Summary (Gemini)":
                with st.spinner("Fetching..."):
                    try:
                        result = gemini_generate(f"""Provide {news_count} recent important updates about: {news_topic}
Format each as:
### 📰 [Headline]
**Summary:** 2-3 sentences
**Significance:** Why it matters
**Source type:** Research/Industry/Academic
---
Be factual and informative.""")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"⚠️ {e}")
            else:
                if not NEWS_KEY:
                    st.error("⚠️ Set **NEWS_API_KEY** in Space secrets. Get free key at newsapi.org")
                else:
                    with st.spinner("Fetching live news..."):
                        try:
                            r = requests.get("https://newsapi.org/v2/everything",
                                params={"q": news_topic, "pageSize": news_count, "sortBy": "publishedAt",
                                        "language": "en", "apiKey": NEWS_KEY}, timeout=10)
                            d = r.json()
                            if d.get("status") == "ok":
                                for a in d["articles"]:
                                    st.markdown(f"### 📰 [{a['title']}]({a['url']})")
                                    if a.get("description"): st.markdown(a["description"])
                                    c1, c2 = st.columns(2)
                                    c1.caption(f"🗞️ {a.get('source',{}).get('name','')}")
                                    c2.caption(f"🕐 {a.get('publishedAt','')[:10]}")
                                    st.markdown("---")
                        except Exception as e:
                            st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a topic.")

# ==============================
# TAB 17: CODE DEBUGGER
# ==============================
with tab17:
    section_header("🐛", "Code Debugger", "Paste broken code — AI finds every bug, explains why it fails, and fixes it.")
    db1, db2 = st.columns([1, 3])
    debug_lang  = db1.selectbox("Language", ["Python","C","C++","Java","JavaScript","SQL","Other"], key="debug_lang")
    debug_error = db2.text_input("Error message (optional)", placeholder="Paste the exception/error message here...")
    broken_code = st.text_area("Broken code", height=220, placeholder="# Paste buggy code here...")
    if st.button("Debug 🐛", type="primary"):
        if broken_code.strip():
            with st.spinner("Analyzing bugs..."):
                try:
                    err_ctx = f"\nError:\n```\n{debug_error}\n```" if debug_error.strip() else ""
                    result = gemini_generate(f"""Debug this {debug_lang} code for an engineering student.{err_ctx}
Code:\n```{debug_lang.lower()}\n{broken_code}\n```
1. 🔍 Bug Analysis (line numbers where possible)
2. 💡 Root cause explanation
3. ✅ Complete fixed code with comments on changed lines
4. 📚 Key concept to prevent this bug
Use markdown.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Paste your code.")

# ==============================
# TAB 18: CODE CONVERTER
# ==============================
with tab18:
    section_header("🔄", "Code Converter", "Convert code between programming languages with explanation of key differences.")
    cv1, cv2, cv3 = st.columns([1, 1, 2])
    from_lang = cv1.selectbox("From", ["Python","C","C++","Java","JavaScript","TypeScript","Go","Rust","SQL"], key="from_lang")
    to_lang   = cv2.selectbox("To",   ["Java","Python","C++","C","JavaScript","TypeScript","Go","Rust","SQL"], key="to_lang")
    add_cmt   = cv3.checkbox("Add detailed inline comments", value=True)
    src_code  = st.text_area("Source code", height=220, placeholder="# Paste source code here...")
    if st.button("Convert 🔄", type="primary"):
        if src_code.strip():
            with st.spinner(f"Converting {from_lang} → {to_lang}..."):
                try:
                    cmt_note = "Add inline comments explaining language differences." if add_cmt else ""
                    result = gemini_generate(f"""Convert this code from {from_lang} to idiomatic {to_lang}. {cmt_note}
Source:\n```{from_lang.lower()}\n{src_code}\n```
After code, add **Key Differences** section: syntax, imports, memory, behavior differences.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Paste source code.")

# ==============================
# TAB 19: UNIT TEST GENERATOR
# ==============================
with tab19:
    section_header("🧪", "Unit Test Generator", "Paste any function and get a complete test suite with edge cases.")
    ut1, ut2 = st.columns([1, 2])
    test_lang = ut1.selectbox("Language", ["Python","Java","JavaScript","C++","Go"], key="test_lang")
    fw_map = {"Python":["pytest","unittest"],"Java":["JUnit 5","JUnit 4"],"JavaScript":["Jest","Mocha"],"C++":["Google Test","Catch2"],"Go":["testing (built-in)"]}
    test_fw   = ut1.selectbox("Framework", fw_map.get(test_lang,["Default"]))
    test_desc = ut2.text_input("What does this function do?", placeholder="Calculates factorial recursively...")
    fn_code   = st.text_area("Function / class", height=200, placeholder="# Paste function here...")
    if st.button("Generate Tests 🧪", type="primary"):
        if fn_code.strip():
            with st.spinner("Writing tests..."):
                try:
                    result = gemini_generate(f"""Write comprehensive {test_fw} unit tests for this {test_lang} code.
{f'Function: {test_desc}' if test_desc.strip() else ''}
Code:\n```{test_lang.lower()}\n{fn_code}\n```
Cover: happy path, edge cases (empty/null/zero), error cases, boundary conditions.
Provide a complete runnable test file with imports, descriptive names, and comments.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Paste your function.")

# ==============================
# TAB 20: ASSIGNMENT HELPER
# ==============================
with tab20:
    section_header("📋", "Assignment Helper", "Paste any assignment question and get a well-structured, complete answer.")
    ah1, ah2 = st.columns([2, 1])
    assign_q   = ah1.text_area("Assignment question", height=150, placeholder="Explain normalization in DBMS with 1NF, 2NF, 3NF examples.")
    assign_sub = ah2.text_input("Subject (optional)", placeholder="DBMS, OS, ML...")
    assign_wds = ah2.number_input("Word limit (0 = no limit)", 0, 5000, 0, 100)
    assign_sty = ah2.selectbox("Answer style", ["Detailed explanation","Point-wise","Essay format","Short answer"])
    if st.button("Generate Answer 📋", type="primary"):
        if assign_q.strip():
            with st.spinner("Writing answer..."):
                try:
                    result = gemini_generate(f"""Write a complete assignment answer for an engineering student.
{f'Subject: {assign_sub}' if assign_sub.strip() else ''}
Style: {assign_sty}
{f'Word limit: ~{assign_wds} words' if assign_wds > 0 else ''}
Question:\n{assign_q}
Include definitions, examples, diagrams (described), proper headings, conclusion. Use markdown.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Answer", data=result, file_name="assignment.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Paste your question.")

# ==============================
# TAB 21: ESSAY / REPORT WRITER
# ==============================
with tab21:
    section_header("✍️", "Essay / Report Writer", "Generate full essays, technical reports, or research summaries on any topic.")
    essay_topic = st.text_input("Topic / Title", placeholder="Impact of AI on Healthcare, Climate Change Solutions...")
    ew1, ew2, ew3 = st.columns(3)
    essay_type  = ew1.selectbox("Type", ["Academic Essay","Technical Report","Research Summary","Opinion Essay","Lab Report","Review Article"])
    essay_words = ew2.selectbox("Length", ["500 words","800 words","1000 words","1500 words","2000 words"])
    essay_level = ew3.selectbox("Level", ["Undergraduate (B.Tech)","School (12th)","Master's Level"])
    essay_pts   = st.text_area("Key points to include (optional, one per line)", height=100,
                               placeholder="Definition\nApplications\nEthical concerns\nFuture prospects")
    if st.button("Write 📝", type="primary"):
        if essay_topic.strip():
            with st.spinner("Writing..."):
                try:
                    pts = ""
                    if essay_pts.strip():
                        pl = [p.strip() for p in essay_pts.splitlines() if p.strip()]
                        pts = "Cover these points:\n" + "\n".join(f"- {p}" for p in pl)
                    result = gemini_generate(f"""Write a complete {essay_type} ({essay_words}) for a {essay_level} student.
Topic: {essay_topic}\n{pts}
Structure: Title → Abstract/Introduction → Main Body (3-5 sections) → Conclusion → References (APA).
Formal academic English. Use ## and ### headings.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download", data=result, file_name=f"essay_{essay_topic[:20]}.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a topic.")

# ==============================
# TAB 22: PRESENTATION OUTLINE
# ==============================
with tab22:
    section_header("📌", "Presentation Outline", "Generate a full slide-by-slide outline with talking points and visual suggestions.")
    pres_topic = st.text_input("Presentation topic", placeholder="Machine Learning, Blockchain, IoT in Healthcare...")
    pp1, pp2, pp3 = st.columns(3)
    pres_slides   = pp1.number_input("Slides", 5, 30, 10)
    pres_duration = pp2.selectbox("Duration", ["5 min","10 min","15 min","20 min","30 min"])
    pres_audience = pp3.selectbox("Audience", ["College Students","Professors","Industry","School","General Public"])
    pres_purpose  = st.radio("Purpose", ["Academic / Project","Seminar / Conference","Interview / Viva","Workshop"], horizontal=True)
    if st.button("Generate Outline 📌", type="primary"):
        if pres_topic.strip():
            with st.spinner("Building outline..."):
                try:
                    result = gemini_generate(f"""Create a detailed {pres_slides}-slide presentation outline.
Topic: {pres_topic} | Duration: {pres_duration} | Audience: {pres_audience} | Purpose: {pres_purpose}
For EACH slide:
## Slide N: [Title]
**Key Points:** bullets
**Talking Points:** 2-4 sentences to say
**Visual:** what image/chart to use
---
Include title slide, conclusion, Q&A slide. End with 3 presentation tips.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download", data=result, file_name=f"slides_{pres_topic[:20]}.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a topic.")

# ==============================
# TAB 23: POMODORO TIMER
# ==============================
with tab23:
    section_header("⏱️", "Pomodoro Timer", "Stay focused with the Pomodoro technique — customizable focus & break cycles.")
    pt1, pt2, pt3 = st.columns(3)
    focus_min   = pt1.number_input("Focus (min)",      5,  90, 25, 5)
    short_brk   = pt2.number_input("Short break (min)", 1,  30,  5, 1)
    long_brk_af = pt3.number_input("Long break after", 2,   8,  4, 1)
    pom_topic   = st.text_input("Studying:", placeholder="Data Structures – Linked Lists")

    st.components.v1.html(f"""
    <div style="text-align:center;padding:24px;background:#1e293b;border-radius:16px;border:1px solid #334155;font-family:Inter,sans-serif;">
        <div id="timer" style="font-size:80px;font-weight:800;color:#f1f5f9;line-height:1;margin-bottom:8px;">{focus_min:02d}:00</div>
        <div id="lbl"   style="font-size:16px;color:#818cf8;font-weight:600;margin-bottom:16px;">🎯 Focus Session</div>
        <div>
            <button onclick="go()" style="background:#4f46e5;color:white;border:none;padding:12px 28px;border-radius:8px;font-size:15px;cursor:pointer;margin:4px;font-weight:600;">▶️ Start</button>
            <button onclick="pa()" style="background:#f59e0b;color:white;border:none;padding:12px 28px;border-radius:8px;font-size:15px;cursor:pointer;margin:4px;font-weight:600;">⏸️ Pause</button>
            <button onclick="rs()" style="background:#ef4444;color:white;border:none;padding:12px 28px;border-radius:8px;font-size:15px;cursor:pointer;margin:4px;font-weight:600;">🔄 Reset</button>
        </div>
        <div id="cnt" style="font-size:13px;color:#64748b;margin-top:12px;">Sessions: 0</div>
        <div style="background:#334155;border-radius:8px;height:10px;width:100%;margin-top:12px;">
            <div id="pb" style="background:#4f46e5;border-radius:8px;height:10px;width:0%;transition:width 0.8s;"></div>
        </div>
    </div>
    <script>
    const FS={focus_min*60},SS={short_brk*60},LA={long_brk_af},LS={long_brk_af*5*60};
    let total=FS,rem=FS,iv=null,run=false,cnt=0,focus=true;
    const p=n=>String(n).padStart(2,'0');
    function upd(){{
        document.getElementById('timer').innerText=p(Math.floor(rem/60))+':'+p(rem%60);
        document.getElementById('pb').style.width=((total-rem)/total*100)+'%';
    }}
    function go(){{
        if(run)return;run=true;
        iv=setInterval(()=>{{
            if(rem<=0){{clearInterval(iv);run=false;
                try{{new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAA==').play();}}catch(e){{}}
                if(focus){{cnt++;document.getElementById('cnt').innerText='Sessions: '+cnt;
                    if(cnt%LA===0){{focus=false;total=LS;rem=LS;document.getElementById('lbl').innerText='☕ Long Break';document.getElementById('pb').style.background='#10b981';}}
                    else{{focus=false;total=SS;rem=SS;document.getElementById('lbl').innerText='😌 Short Break';document.getElementById('pb').style.background='#f59e0b';}}
                }}else{{focus=true;total=FS;rem=FS;document.getElementById('lbl').innerText='🎯 Focus Session';document.getElementById('pb').style.background='#4f46e5';}}
                upd();return;
            }}
            rem--;upd();
        }},1000);
    }}
    function pa(){{clearInterval(iv);run=false;}}
    function rs(){{clearInterval(iv);run=false;focus=true;total=FS;rem=FS;cnt=0;
        document.getElementById('lbl').innerText='🎯 Focus Session';
        document.getElementById('cnt').innerText='Sessions: 0';
        document.getElementById('pb').style.background='#4f46e5';upd();}}
    upd();
    </script>""", height=320)

# ==============================
# TAB 24: STICKY NOTES
# ==============================
with tab24:
    section_header("🗒️", "Sticky Notes", "Save notes, AI responses, and reminders with color-coded tags.")
    if "sticky_notes" not in st.session_state:
        st.session_state.sticky_notes = []
    sn1, sn2 = st.columns([3, 1])
    new_note   = sn1.text_area("New note", height=100, placeholder="Type a note or paste an AI response...")
    note_color = sn2.selectbox("Color", ["🟡 Yellow","🟢 Green","🔵 Blue","🔴 Red","🟣 Purple"])
    note_tag   = sn2.text_input("Tag", placeholder="Math, Code, Todo...")
    if st.button("📌 Save Note", type="primary"):
        if new_note.strip():
            st.session_state.sticky_notes.append({"text": new_note.strip(), "color": note_color, "tag": note_tag.strip() or "General"})
            st.success("✅ Saved!"); st.rerun()
        else:
            st.warning("Write something first.")
    if st.session_state.sticky_notes:
        tags = sorted(set(n["tag"] for n in st.session_state.sticky_notes))
        ft = st.selectbox("Filter by tag", ["All"] + tags)
        shown = st.session_state.sticky_notes if ft == "All" else [n for n in st.session_state.sticky_notes if n["tag"] == ft]
        cmap = {"🟡 Yellow":"#fef08a","🟢 Green":"#bbf7d0","🔵 Blue":"#bfdbfe","🔴 Red":"#fecaca","🟣 Purple":"#e9d5ff"}
        bmap = {"🟡 Yellow":"#eab308","🟢 Green":"#22c55e","🔵 Blue":"#3b82f6","🔴 Red":"#ef4444","🟣 Purple":"#a855f7"}
        st.markdown(f"**{len(shown)} note(s)**")
        rows = [shown[i:i+2] for i in range(0, len(shown), 2)]
        for row in rows:
            cols = st.columns(2)
            for ci, note in enumerate(row):
                idx = st.session_state.sticky_notes.index(note)
                bg = cmap.get(note["color"],"#fef08a"); bd = bmap.get(note["color"],"#eab308")
                with cols[ci]:
                    st.markdown(f'<div style="background:{bg};border-left:4px solid {bd};padding:12px;border-radius:8px;margin-bottom:8px;"><small style="color:#374151;">🏷️ {note["tag"]}</small><p style="margin:4px 0 0;color:#111827;white-space:pre-wrap;font-size:13px;">{note["text"]}</p></div>', unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"dn_{idx}"):
                        st.session_state.sticky_notes.pop(idx); st.rerun()
        sc1, sc2 = st.columns(2)
        if sc1.button("⬇️ Export All Notes"):
            txt = "\n\n".join(f"[{n['tag']}]\n{n['text']}" for n in st.session_state.sticky_notes)
            st.download_button("Download (.txt)", data=txt, file_name="notes.txt", mime="text/plain")
        if sc2.button("🗑️ Clear All"):
            st.session_state.sticky_notes = []; st.rerun()
    else:
        st.info("No notes yet. Write your first note above!")

# ==============================
# TAB 25: PROGRESS DASHBOARD
# ==============================
with tab25:
    section_header("📈", "Progress Dashboard", "Track your session activity and get personalized AI study tips.")
    chat_c  = len(st.session_state.get("messages", []))
    pdf_c   = len(st.session_state.get("pdf_qa_history", []))
    note_c  = len(st.session_state.get("sticky_notes", []))
    pdf_l   = 1 if st.session_state.get("pdf_text") else 0
    usage   = {"Chat Messages": chat_c, "PDF Questions": pdf_c, "Sticky Notes": note_c, "PDFs Loaded": pdf_l}
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💬 Chat Messages", chat_c)
    m2.metric("📄 PDF Questions", pdf_c)
    m3.metric("🗒️ Sticky Notes",  note_c)
    m4.metric("📄 PDFs Loaded",   pdf_l)
    st.markdown("---")
    active = {k: v for k, v in usage.items() if v > 0}
    if active:
        df_d = pd.DataFrame({"Activity": list(active.keys()), "Count": list(active.values())})
        fig_d = px.bar(df_d, x="Activity", y="Count", title="Session Activity", color="Activity",
                       template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Set3)
        fig_d.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig_d, use_container_width=True)
    else:
        st.info("Use app features and your activity will appear here!")
    st.markdown("---")
    st.markdown("### 💡 Personalized Tips")
    if chat_c > 0 or note_c > 0:
        try:
            tips = gemini_generate(f"""Student used AI Study Buddy: {', '.join(f'{k}:{v}' for k,v in active.items())}.
Give 3 short personalized encouraging study tips. Number them. 1-2 sentences each.""")
            st.markdown(tips)
        except Exception:
            st.info("Keep exploring the app to unlock personalized tips!")
    else:
        st.info("Start using the features and return here for personalized tips!")
    if st.button("🔄 Refresh"): st.rerun()

# ==============================
# TAB 26: GRAMMAR CHECKER ✏️
# ==============================
with tab26:
    section_header("✏️", "Grammar & Writing Checker", "Check grammar, improve writing style, and get rewrite suggestions.")
    grammar_text = st.text_area("Paste your text", height=200, placeholder="Paste essay, assignment, email, or any text to check...")
    gc1, gc2 = st.columns(2)
    check_mode  = gc1.selectbox("Check mode", ["Full grammar + style", "Grammar only", "Style & clarity only", "Academic writing", "Simplify writing"])
    formality   = gc2.selectbox("Target tone", ["Formal/Academic", "Professional", "Casual/Conversational", "Technical"])
    if st.button("Check & Improve ✏️", type="primary"):
        if grammar_text.strip():
            with st.spinner("Analyzing..."):
                try:
                    result = gemini_generate(f"""You are an expert writing editor. Analyze this text.
Mode: {check_mode} | Target tone: {formality}
Text:\n{grammar_text}

Provide:
1. **Grammar Issues** — List each error with correction
2. **Style Suggestions** — Clarity, flow, word choice improvements
3. **Rewritten Version** — Improved version of the full text
4. **Score** — Rate original: Grammar /10, Clarity /10, Style /10

Use markdown.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Report", data=result, file_name="grammar_report.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Paste text to check.")

# ==============================
# TAB 27: INTERVIEW PREP 🎓
# ==============================
with tab27:
    section_header("🎓", "Interview Prep", "Practice mock interview Q&A for technical and HR rounds.")
    ip1, ip2, ip3 = st.columns(3)
    int_role    = ip1.text_input("Role / Position", placeholder="Software Engineer, Data Scientist, ML Engineer...")
    int_subject = ip2.text_input("Topic / Subject", placeholder="DSA, DBMS, ML, OS, System Design...")
    int_round   = ip3.selectbox("Interview round", ["Technical Round 1","Technical Round 2","HR Round","System Design","Viva / Oral Exam"])
    int_level   = st.radio("Experience level", ["Fresher (0-1 yr)","Junior (1-3 yrs)","Mid (3-5 yrs)"], horizontal=True)
    int_count   = st.slider("Number of questions", 5, 20, 10)
    if st.button("Start Mock Interview 🎓", type="primary"):
        if int_role.strip() or int_subject.strip():
            with st.spinner("Preparing questions..."):
                try:
                    result = gemini_generate(f"""Create a mock {int_round} for a {int_level} {int_role}.
Subject: {int_subject or 'General'}. Generate {int_count} interview questions.
For each question:
### Q[N]: [Question]
**Type:** Technical / Conceptual / Scenario / HR
**Expected Answer:**
- Key points the interviewer wants to hear
- Example if needed
**Follow-up question:** One follow-up the interviewer might ask
---
End with 5 **Interview Tips** specific to this role/round.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Q&A", data=result, file_name="interview_prep.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter role or subject.")

# ==============================
# TAB 28: MATH SOLVER 🔢
# ==============================
with tab28:
    section_header("🔢", "Math Problem Solver", "Paste any math problem and get a complete step-by-step solution.")
    math_problem = st.text_area("Enter your math problem", height=150,
                                placeholder="Example: Solve x² + 5x + 6 = 0\nOr: Integrate x²·sin(x) dx\nOr: Find the eigenvalues of [[2,1],[1,2]]")
    ms1, ms2 = st.columns(2)
    math_level  = ms1.selectbox("Level", ["Class 10-12","Engineering Year 1-2","Engineering Year 3-4","Competitive Exam"])
    show_verify = ms2.checkbox("Verify answer numerically", value=True)
    if st.button("Solve 🔢", type="primary"):
        if math_problem.strip():
            with st.spinner("Solving step by step..."):
                try:
                    verify = "After solving, verify the answer by substituting back or numerically checking." if show_verify else ""
                    result = gemini_generate(f"""You are an expert math tutor. Solve this problem completely for a {math_level} student.
Problem:\n{math_problem}
Provide:
1. **Problem Type** — Identify what type of problem this is
2. **Step-by-Step Solution** — Every step clearly explained with working
3. **Final Answer** — Clearly boxed/highlighted
4. **Verification** — {verify if show_verify else 'Skip verification.'}
5. **Key Formula Used** — Formula applied with name
Use LaTeX notation in plain text (e.g. x^2, sqrt(x), integral). Use markdown.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a math problem.")
    st.markdown("**Examples:** `Solve 2x² - 3x + 1 = 0` | `Differentiate sin(x²)` | `Find inverse of matrix [[1,2],[3,4]]`")

# ==============================
# TAB 29: DICTIONARY & THESAURUS 📖
# ==============================
with tab29:
    section_header("📖", "Dictionary & Thesaurus", "Look up definitions, synonyms, antonyms, etymology, and usage examples.")
    dict_word = st.text_input("Enter a word or phrase", placeholder="photosynthesis, algorithm, serendipity...")
    dw1, dw2 = st.columns(2)
    dict_mode   = dw1.selectbox("Lookup type", ["Full definition + thesaurus","Definition only","Synonyms & antonyms","Etymology & origin","Usage examples","Technical meaning (CS/Engineering)"])
    dict_simple = dw2.checkbox("Explain simply (ELI5 style)", value=False)
    if st.button("Look Up 📖", type="primary"):
        if dict_word.strip():
            with st.spinner("Looking up..."):
                try:
                    simple = "Also explain it in the simplest possible way (ELI5)." if dict_simple else ""
                    result = gemini_generate(f"""You are an expert dictionary and thesaurus. Look up: "{dict_word}"
Mode: {dict_mode}
{simple}
Provide structured information with:
- **Definition(s)** (with part of speech)
- **Pronunciation** (phonetic)
- **Synonyms** (5-8)
- **Antonyms** (3-5 if applicable)
- **Example sentences** (3 real-world uses)
- **Etymology** (word origin briefly)
- **Related forms** (noun/verb/adjective variants)
Use markdown formatting.""")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a word to look up.")

# ==============================
# TAB 30: RESUME / CV BUILDER 📑
# ==============================
with tab30:
    section_header("📑", "Resume / CV Builder", "Generate a professional resume or CV from your details.")
    st.info("Fill in your details below and AI will generate a professional, ATS-friendly resume.")
    rb1, rb2 = st.columns(2)
    res_name   = rb1.text_input("Full Name", placeholder="Karan Dewangan")
    res_email  = rb2.text_input("Email", placeholder="karan@email.com")
    rb3, rb4   = st.columns(2)
    res_phone  = rb3.text_input("Phone", placeholder="+91 9876543210")
    res_loc    = rb4.text_input("Location", placeholder="Bilaspur, Chhattisgarh")
    res_obj    = st.text_area("Career objective / Summary", height=80,
                              placeholder="Ambitious B.Tech CS student specializing in AI/ML, seeking internship opportunities...")
    res_edu    = st.text_area("Education (one per line)", height=80,
                              placeholder="B.Tech CS (AIML) | Chouksey Engineering College | 2022-2026 | CGPA 8.5")
    res_skills = st.text_input("Key skills (comma separated)", placeholder="Python, Machine Learning, Deep Learning, SQL, Git")
    res_exp    = st.text_area("Experience / Internships (one per line)", height=80,
                              placeholder="Lenovo Leap Internship | AI Developer | June 2024 | Built AI Study Buddy app")
    res_proj   = st.text_area("Projects (one per line)", height=80,
                              placeholder="AI Study Buddy — Streamlit app with 35 AI features using Gemini & HF")
    res_cert   = st.text_input("Certifications (comma separated)", placeholder="Google ML Certificate, AWS Cloud Practitioner")
    res_format = st.radio("Format", ["Chronological","Functional / Skills-based","Hybrid"], horizontal=True)
    if st.button("Generate Resume 📑", type="primary"):
        if res_name.strip():
            with st.spinner("Building resume..."):
                try:
                    result = gemini_generate(f"""Create a professional ATS-friendly {res_format} resume in markdown.
Name: {res_name} | Email: {res_email} | Phone: {res_phone} | Location: {res_loc}
Objective: {res_obj}
Education: {res_edu}
Skills: {res_skills}
Experience: {res_exp}
Projects: {res_proj}
Certifications: {res_cert}
Make it professional, well-structured, and impactful. Use action verbs. Quantify achievements where possible.
Format with clear section headings (##), bullet points for responsibilities.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Resume (.txt)", data=result, file_name="resume.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter at least your name.")

# ==============================
# TAB 31: TIMETABLE GENERATOR 🗓️
# ==============================
with tab31:
    section_header("🗓️", "Weekly Timetable Generator", "Generate a balanced weekly timetable for college or personal study.")
    tt1, tt2 = st.columns(2)
    tt_subjects = tt1.text_area("Subjects / Activities (one per line)", height=150,
                                placeholder="Data Structures\nDBMS\nMachine Learning\nPhysics\nMaths\nSoft Skills\nProject Work\nExercise")
    with tt2:
        tt_days      = st.multiselect("Active days", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                                      default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"])
        tt_start     = st.time_input("Day start time", value=None)
        tt_end       = st.time_input("Day end time",   value=None)
        tt_breaks    = st.checkbox("Include lunch/tea breaks", value=True)
        tt_sports    = st.checkbox("Include sports/exercise slot", value=True)
    if st.button("Generate Timetable 🗓️", type="primary"):
        if tt_subjects.strip():
            with st.spinner("Building timetable..."):
                try:
                    subs = [s.strip() for s in tt_subjects.splitlines() if s.strip()]
                    result = gemini_generate(f"""Create a balanced weekly timetable for a college student.
Subjects: {', '.join(subs)}
Active days: {', '.join(tt_days) if tt_days else 'Mon-Sat'}
{'Include lunch break (1-1:30pm) and tea breaks (11am, 4pm).' if tt_breaks else ''}
{'Include a 45-min sports/exercise slot daily.' if tt_sports else ''}
Format as a markdown table with days as columns and time slots as rows.
Distribute subjects evenly. Include self-study, revision, and project time.
Add a note on weekly hours per subject at the end.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Timetable", data=result, file_name="timetable.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter at least one subject.")

# ==============================
# TAB 32: MOTIVATION & QUOTES 💡
# ==============================
with tab32:
    section_header("💡", "Motivation & Quotes", "Get personalized motivation, quotes, and study mindset tips.")
    mq1, mq2 = st.columns(2)
    mot_category = mq1.selectbox("Category", ["General Motivation","Study & Learning","Overcoming Failure","Exam Stress","Career Goals","Consistency & Discipline","Success Mindset","Engineering Student Life"])
    mot_style    = mq2.selectbox("Style", ["Inspirational quotes","Motivational speech","Daily affirmations","Practical action steps","Funny but motivational","Short poem"])
    mot_mood     = st.radio("Your current mood", ["😴 Feeling lazy", "😰 Stressed about exams", "😤 Frustrated", "😊 Doing well, need push", "😢 Feeling like giving up"], horizontal=True)
    if st.button("Get Motivation 💡", type="primary"):
        with st.spinner("Generating..."):
            try:
                result = gemini_generate(f"""Generate {mot_style} for an engineering student.
Category: {mot_category} | Mood: {mot_mood}
Make it genuinely helpful, heartfelt, and specific to an engineering student's life.
Include 5-7 items. Format nicely with emojis and markdown.""")
                st.markdown(result)
            except Exception as e:
                st.error(f"⚠️ {e}")
    # Quick quote button
    if st.button("⚡ Random Quote Now"):
        with st.spinner("..."):
            try:
                q = gemini_generate("Give ONE powerful motivational quote for an engineering student. Just the quote and author. No extra text.")
                st.markdown(f'<div style="background:#1e293b;border-left:4px solid #4f46e5;padding:16px 20px;border-radius:8px;font-size:16px;font-style:italic;color:#e2e8f0;">{q}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"⚠️ {e}")

# ==============================
# TAB 33: RESEARCH FINDER 🔍
# ==============================
with tab33:
    section_header("🔍", "Research Paper Finder", "Get AI-summarized research directions, key papers, and study resources on any topic.")
    res_topic = st.text_input("Research topic", placeholder="Transformer architecture, Quantum Computing, CRISPR gene editing...")
    rf1, rf2  = st.columns(2)
    res_field = rf1.selectbox("Field", ["Computer Science","AI / Machine Learning","Electronics","Mechanical","Civil","Biotechnology","Physics","Chemistry","Economics","General Science"])
    res_depth = rf2.selectbox("Detail level", ["Overview (5 min read)","Detailed (10 min read)","Deep dive (research level)"])
    if st.button("Find Research 🔍", type="primary"):
        if res_topic.strip():
            with st.spinner("Researching..."):
                try:
                    result = gemini_generate(f"""You are an academic research assistant. Provide a {res_depth} on: {res_topic} in {res_field}.
Include:
1. **Topic Overview** — What is it and why important
2. **Key Concepts** — 5-7 fundamental ideas
3. **Important Research Papers** — 5 landmark papers (title, authors, year, 2-line summary each)
4. **Current State of the Art** — What's the latest development
5. **Open Problems** — What's still unsolved
6. **Learning Resources** — Books, courses, YouTube channels, websites
7. **Keywords for further search** — 10 search terms for Google Scholar
Use markdown with clear headings.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Report", data=result, file_name=f"research_{res_topic[:20]}.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a research topic.")

# ==============================
# TAB 34: PLAGIARISM ADVISOR 📃
# ==============================
with tab34:
    section_header("📃", "Plagiarism & Originality Advisor", "Get suggestions to make your writing more original and avoid plagiarism issues.")
    plag_text = st.text_area("Paste your text", height=200,
                             placeholder="Paste your essay, report, or assignment text here...")
    pa1, pa2 = st.columns(2)
    plag_mode = pa1.selectbox("Mode", ["Check originality & suggest rewrites","Paraphrase the text","Cite sources properly","Make text more unique"])
    plag_ref  = pa2.selectbox("Citation style", ["APA 7th","MLA 9th","IEEE","Chicago","Harvard"])
    st.info("⚠️ Note: This tool gives AI suggestions for originality — it is NOT a live plagiarism detection tool. Always use Turnitin or similar for official checks.")
    if st.button("Analyze & Improve 📃", type="primary"):
        if plag_text.strip():
            with st.spinner("Analyzing..."):
                try:
                    result = gemini_generate(f"""You are an academic writing advisor. Analyze this text for originality.
Mode: {plag_mode} | Citation style: {plag_ref}
Text:\n{plag_text}
Provide:
1. **Originality Assessment** — Identify generic/commonly used phrases
2. **High-risk phrases** — Phrases that might match common sources
3. **Rewritten version** — More original version of the text
4. **How to cite** — Example citations in {plag_ref} style
5. **Tips** — 5 tips to maintain academic integrity
Use markdown.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Report", data=result, file_name="originality_report.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Paste your text.")

# ==============================
# TAB 35: TOPIC LEARNING PATH 🧬
# ==============================
with tab35:
    section_header("🧬", "Topic Learning Path", "Get a complete step-by-step learning roadmap for mastering any topic or skill.")
    lp_topic = st.text_input("What do you want to learn?", placeholder="Machine Learning, Web Development, DSA, Competitive Programming...")
    lp1, lp2, lp3 = st.columns(3)
    lp_level    = lp1.selectbox("Current level", ["Complete beginner","Know the basics","Intermediate","Advanced"])
    lp_goal     = lp2.selectbox("Your goal", ["Get a job","Clear an exam","Academic project","Personal interest","Competitive coding","Research"])
    lp_duration = lp3.selectbox("Time available", ["2 weeks","1 month","3 months","6 months","1 year"])
    lp_hrs      = st.slider("Hours per day", 1, 8, 2)
    if st.button("Generate Roadmap 🧬", type="primary"):
        if lp_topic.strip():
            with st.spinner("Building your learning path..."):
                try:
                    result = gemini_generate(f"""Create a complete learning roadmap for: {lp_topic}
Current level: {lp_level} | Goal: {lp_goal} | Time: {lp_duration} | Hours/day: {lp_hrs}

Include:
## Phase 1: Foundations [Week/Month range]
- Topics to cover (ordered)
- Resources (books, free courses, YouTube, websites)
- Mini projects to build
- Checkpoint: how to know you're ready for next phase

## Phase 2: Core Concepts ...
## Phase 3: Advanced / Applied ...
## Phase 4: Real Projects ...

Also include:
- **Recommended resources table** (Resource | Type | Cost | Link description)
- **Common mistakes** to avoid
- **Daily schedule** suggestion ({lp_hrs} hrs/day breakdown)
- **Milestone checklist** ✅

Use markdown with clear ## headings.""")
                    st.markdown(result)
                    st.download_button("⬇️ Download Roadmap", data=result, file_name=f"roadmap_{lp_topic[:20]}.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"⚠️ {e}")
        else:
            st.warning("Enter a topic to learn.")

# ==========================================
# PROFESSIONAL FOOTER
# ==========================================

st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:16px 0; color:#475569; font-size:12px; line-height:1.8;">
    <div style="margin-bottom:6px;">
        <span class="badge badge-blue">35 AI Features</span> &nbsp;
        <span class="badge badge-green">Gemini 2.5 Flash</span> &nbsp;
        <span class="badge badge-orange">FLUX.1 Images</span> &nbsp;
        <span class="badge badge-red">Free on HF Spaces</span>
    </div>
    Built with ❤️ by <b style="color:#94a3b8;">Karan Dewangan</b> &nbsp;·&nbsp;
    B.Tech CS (AIML) &nbsp;·&nbsp; Chouksey Engineering College, Bilaspur &nbsp;·&nbsp;
    Minor Project Phase 1 — Lenovo Leap BharatCares Internship
</div>
""", unsafe_allow_html=True)
