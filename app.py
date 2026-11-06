import os
from pathlib import Path
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import random

# ==========================================
# 1. Page Configuration & Dynamic Favicon
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
favicon = None

for name in ("friday_favicon.png", "friday_favicon.ico", "friday_favicon", "friday.png", "friday.jpg"):
    candidate = BASE_DIR / name
    try:
        if candidate.is_file():
            with Image.open(candidate) as image:
                favicon = image.copy()
            break
    except (OSError, ValueError):
        pass

st.set_page_config(
    page_title="F.R.I.D.A.Y. AI",
    page_icon=favicon if favicon is not None else "⚡",
    layout="wide"
)

# ==========================================
# 2. Iron Man Theme Styling (Red, Black, & Gold)
# ==========================================
st.markdown("""
    <style>
    /* Full Application Iron Man Gradient Background Code (Black, Crimson Red, and Gold) */
    .stApp {
        background: linear-gradient(135deg, #0d090a 0%, #2b0c10 40%, #781c1c 75%, #d4af37 100%) !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        color: #FFD700;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }

    /* Streamlit Containers & Main Area Transparency */
    [data-testid="stMain"], [data-testid="stChatMessageContainer"] {
        background: transparent !important;
    }

    /* Top Header / Navigation Bar Styling */
    [data-testid="stHeader"] {
        background: rgba(13, 9, 10, 0.85) !important;
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    }

    /* Sidebar Background Integration */
    [data-testid="stSidebar"] {
        background: rgba(13, 9, 10, 0.92) !important;
        border-right: 1px solid rgba(212, 175, 55, 0.3);
    }

    /* Chat Input / Text Box Styling */
    [data-testid="stChatInput"] {
        background: rgba(13, 9, 10, 0.85) !important;
        border: 1px solid rgba(212, 175, 55, 0.6) !important;
        border-radius: 14px !important;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.25) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #FFD700 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(255, 215, 0, 0.5) !important;
    }

    /* Centered F.R.I.D.A.Y. Logo Container */
    .friday-logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .friday-reactor-wrapper {
        position: relative;
        width: 130px;
        height: 130px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .friday-ring-outer {
        position: absolute;
        width: 130px;
        height: 130px;
        border-radius: 50%;
        border: 2px dashed rgba(212, 175, 55, 0.8);
        animation: rotateDashedRing 10s linear infinite;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
    }

    .friday-core {
        position: absolute;
        width: 85px;
        height: 85px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, rgba(43, 12, 16, 0.95) 80%);
        border: 2px solid #FFD700;
        box-shadow: 0 0 30px #FF4500, inset 0 0 15px #FFD700;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulseFRIDAY 3s infinite ease-in-out;
    }

    .friday-symbol {
        font-size: 2.5rem;
        font-weight: 900;
        color: #FFD700;
        text-shadow: 0 0 20px #FF4500;
        font-family: 'Courier New', monospace;
    }

    @keyframes rotateDashedRing {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes pulseFRIDAY {
        0% { box-shadow: 0 0 20px #FF4500, inset 0 0 15px #FFD700; }
        50% { box-shadow: 0 0 50px #FFD700, inset 0 0 25px #FF4500; }
        100% { box-shadow: 0 0 20px #FF4500, inset 0 0 15px #FFD700; }
    }

    .hud-title {
        color: #FFD700;
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: 5px;
        text-shadow: 0 0 20px rgba(255, 69, 0, 0.9);
        margin-top: 10px;
        margin-bottom: 2px;
        text-align: center;
    }

    .hud-status {
        color: #00FF66;
        font-size: 0.9rem;
        letter-spacing: 2px;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(0, 255, 102, 0.8);
        text-align: center;
        margin-bottom: 20px;
    }

    /* Custom Chat Message Cards */
    [data-testid="stChatMessage"] {
        background: rgba(13, 9, 10, 0.88) !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(255, 69, 0, 0.15) !important;
        margin-bottom: 12px !important;
        color: #FFD700 !important;
    }

    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
        border-left: 4px solid #FFD700 !important;
    }

    [data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
        border-left: 4px solid #FF2400 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header HUD
st.markdown("""
    <div class="friday-logo-container">
        <div class="friday-reactor-wrapper">
            <div class="friday-ring-outer"></div>
            <div class="friday-core">
                <span class="friday-symbol">F</span>
            </div>
        </div>
        <div class="hud-title">F.R.I.D.A.Y.</div>
        <div class="hud-status">● MARK L5 ARMOR SUITE ONLINE</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. Backend & Multi-Session History Setup
# ==========================================
api_key = st.secrets.get("OPENROUTER_API_KEY") or st.secrets.get("GROQ_API_KEY") or os.environ.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("OPENROUTER_API_KEY missing in Streamlit Secrets. Please configure in App Settings > Secrets.")
    st.stop()

if "sessions" not in st.session_state:
    st.session_state.sessions = {"New Chat": []}

if "current_session" not in st.session_state:
    st.session_state.current_session = "New Chat"

if "editing_session" not in st.session_state:
    st.session_state.editing_session = None

MODEL_OPTIONS = {
    "Claude Opus 5.5 (Advanced Reasoning)": "anthropic/claude-opus-5.5:nitro",
    "GPT-6 Luna (High-Speed Core)": "openai/gpt-6-luna:nitro",
    "Gemini 3.8 Flash (Ultra-Fast)": "google/gemini-3.8-flash:nitro",
    "DeepSeek V4.1 Flash (Code Specialist)": "deepseek/deepseek-v4.1-flash:nitro",
    "GLM 5.3 Flash (Efficiency)": "z-ai/glm-5.3-flash:nitro"
}

# Sidebar Navigation & Session Management
with st.sidebar:
    st.title("⚡ F.R.I.D.A.Y. Core")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_title = f"Chat Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_title] = []
        st.session_state.current_session = new_title
        st.session_state.editing_session = None
        st.rerun()

    st.divider()
    st.markdown("### 🕒 Recent Chats")
    
    session_names = list(st.session_state.sessions.keys())
    for s_name in reversed(session_names):
        if st.session_state.editing_session == s_name:
            new_name_input = st.text_input(
                "Rename Chat:",
                value=s_name,
                key=f"input_edit_{s_name}",
                label_visibility="collapsed"
            )
            col_save, col_cancel = st.columns([1, 1])
            with col_save:
                if st.button("✅", key=f"save_{s_name}", help="Save Name"):
                    trimmed_name = new_name_input.strip()
                    if trimmed_name and trimmed_name != s_name:
                        st.session_state.sessions[trimmed_name] = st.session_state.sessions.pop(s_name)
                        if st.session_state.current_session == s_name:
                            st.session_state.current_session = trimmed_name
                    st.session_state.editing_session = None
                    st.rerun()
            with col_cancel:
                if st.button("❌", key=f"cancel_{s_name}", help="Cancel Edit"):
                    st.session_state.editing_session = None
                    st.rerun()
        else:
            col_select, col_edit, col_del = st.columns([3, 1, 1])
            with col_select:
                if st.button(s_name, use_container_width=True, key=f"sel_{s_name}"):
                    st.session_state.current_session = s_name
                    st.rerun()
            with col_edit:
                if st.button("✏️", key=f"edit_{s_name}", help=f"Rename {s_name}"):
                    st.session_state.editing_session = s_name
                    st.rerun()
            with col_del:
                if len(st.session_state.sessions) > 1:
                    if st.button("🗑️", key=f"del_{s_name}", help=f"Delete {s_name}"):
                        del st.session_state.sessions[s_name]
                        if st.session_state.current_session == s_name:
                            st.session_state.current_session = list(st.session_state.sessions.keys())[-1]
                        st.rerun()
                else:
                    st.button("🔒", disabled=True, key=f"lock_{s_name}", help="Cannot delete last session")

    st.divider()
    st.markdown("⚙️ **System Settings**")
    
    selected_model_label = st.selectbox(
        "🧠 Active Model Core",
        options=list(MODEL_OPTIONS.keys()),
        index=2
    )
    
    selected_model_id = MODEL_OPTIONS[selected_model_label]
    enable_voice = st.toggle("🔊 Speak Answers Aloud (TTS)", value=True)
    st.divider()

    if st.button("🗑️ Purge All Logs", use_container_width=True):
        st.session_state.sessions = {"New Chat": []}
        st.session_state.current_session = "New Chat"
        st.session_state.editing_session = None
        st.rerun()

if st.session_state.current_session not in st.session_state.sessions:
    st.session_state.current_session = list(st.session_state.sessions.keys())[0]

current_messages = st.session_state.sessions[st.session_state.current_session]

# Render Chat History for Active Session
for message in current_messages:
    avatar = "👤" if message["role"] == "user" else "⚡"
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", ""))
        else:
            st.markdown(message["content"])

# ==========================================
# 4. User Interaction & Expert Coding Core
# ==========================================
prompt = st.chat_input(f"Ask F.R.I.D.A.Y. to write code, debug, or analyze ({st.session_state.current_session})...")

if prompt:
    if st.session_state.current_session.startswith("New Chat") or st.session_state.current_session.startswith("Chat Session"):
        new_title = prompt[:28] + "..." if len(prompt) > 28 else prompt
        st.session_state.sessions[new_title] = st.session_state.sessions.pop(st.session_state.current_session)
        st.session_state.current_session = new_title

    st.session_state.sessions[st.session_state.current_session].append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        prompt_lower = prompt.lower()
        
        image_keywords = ["image", "picture", "photo", "draw", "render", "generate", "create", "make", "painting", "art", "sketch"]
        is_image_request = any(kw in prompt_lower for kw in image_keywords)

        if is_image_request:
            with st.spinner("⚡ F.R.I.D.A.Y. is synthesizing high-precision visual assets..."):
                img_prompt = prompt
                for prefix in ["generate an image of", "generate a image of", "generate", "create an image of", "create a picture of", "create", "draw a", "draw an", "draw", "render a", "render", "make an image of", "make a picture of", "make"]:
                    if prompt_lower.startswith(prefix):
                        img_prompt = prompt[len(prefix):].strip()
                        break
                
                clean_query = img_prompt if img_prompt else prompt
                rand_seed = random.randint(1000, 999999)
                encoded_prompt = urllib.parse.quote(clean_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&seed={rand_seed}&model=turbo&nologo=true&enhance=true"
                
                st.image(image_url, caption=f"Generated for Boss: {prompt}")
                st.session_state.sessions[st.session_state.current_session].append({
                    "role": "assistant", 
                    "content": image_url, 
                    "type": "image", 
                    "caption": f"Generated for Boss: {prompt}"
                })
        else:
            with st.spinner(f"
