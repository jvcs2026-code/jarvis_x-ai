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
# 2. HUD Styling & Green Status Text
# ==========================================
st.markdown("""
    <style>
    /* Full Application Navy-to-Teal Gradient Background Code */
    .stApp {
        background: linear-gradient(180deg, #021226 0%, #0d7c7e 100%) !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        color: #00F0FF;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }

    /* Streamlit Containers & Main Area Transparency */
    [data-testid="stMain"], [data-testid="stChatMessageContainer"] {
        background: transparent !important;
    }

    /* Top Header / Navigation Bar Styling */
    [data-testid="stHeader"] {
        background: rgba(2, 18, 38, 0.75) !important;
        border-bottom: 1px solid rgba(0, 240, 255, 0.2);
    }

    /* Sidebar Background Integration */
    [data-testid="stSidebar"] {
        background: rgba(2, 18, 38, 0.90) !important;
        border-right: 1px solid rgba(0, 240, 255, 0.2);
    }

    /* Chat Input / Text Box Styling */
    [data-testid="stChatInput"] {
        background: rgba(2, 18, 38, 0.85) !important;
        border: 1px solid rgba(0, 240, 255, 0.5) !important;
        border-radius: 14px !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.25) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #00F0FF !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(0, 240, 255, 0.5) !important;
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
        border: 2px dashed rgba(0, 240, 255, 0.8);
        animation: rotateDashedRing 10s linear infinite;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.6);
    }

    .friday-core {
        position: absolute;
        width: 85px;
        height: 85px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 240, 255, 0.4) 0%, rgba(2, 18, 38, 0.95) 80%);
        border: 2px solid #00F0FF;
        box-shadow: 0 0 35px #00F0FF, inset 0 0 15px #00F0FF;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulseFRIDAY 3s infinite ease-in-out;
    }

    .friday-symbol {
        font-size: 2.5rem;
        font-weight: 900;
        color: #00F0FF;
        text-shadow: 0 0 15px #00F0FF, 0 0 30px #00F0FF;
        font-family: 'Courier New', monospace;
    }

    @keyframes rotateDashedRing {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes pulseFRIDAY {
        0% { box-shadow: 0 0 20px #00F0FF, inset 0 0 15px #00F0FF; }
        50% { box-shadow: 0 0 55px #00F0FF, inset 0 0 25px #00F0FF; }
        100% { box-shadow: 0 0 20px #00F0FF, inset 0 0 15px #00F0FF; }
    }

    /* Highly Glowing Cyan Title */
    .hud-title {
        color: #00F0FF;
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: 5px;
        text-shadow: 0 0 10px #00F0FF, 0 0 22px #00F0FF, 0 0 40px rgba(0, 240, 255, 0.9);
        margin-top: 10px;
        margin-bottom: 2px;
        text-align: center;
    }

    /* Glowing Green Sub-status Text */
    .hud-status {
        color: #00FF66 !important;
        font-size: 0.9rem;
        letter-spacing: 2px;
        font-weight: 600;
        text-shadow: 0 0 10px #00FF66, 0 0 25px rgba(0, 255, 102, 0.9);
        text-align: center;
        margin-bottom: 20px;
    }

    /* Custom Chat Message Cards */
    [data-testid="stChatMessage"] {
        background: rgba(2, 18, 38, 0.88) !important;
        border: 1px solid rgba(0, 240, 255, 0.5) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.3) !important;
        margin-bottom: 12px !important;
    }

    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
        border-left: 4px solid #00F0FF !important;
    }

    [data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
        border-left: 4px solid #00FF66 !important;
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
        <div class="hud-status">● MASTER PROGRAMMING & NEURAL CORE ACTIVE</div>
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

if "chat_input_text" not in st.session_state:
    st.session_state.chat_input_text = ""

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
        st.session_state.chat_input_text = ""
        st.rerun()

    st.divider()
    st.markdown("### 📁 Neural File Uplink")
    uploaded_file = st.file_uploader("Upload document/code for analysis", type=["txt", "py", "csv", "json", "md", "log"])

    # When a file is uploaded, automatically load its content into the text box buffer
    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.read()
            file_content = file_bytes.decode("utf-8", errors="ignore")
            # Populate text input buffer with file wrapper structure
            st.session_state.chat_input_text = f"Analyze this uploaded file ({uploaded_file.name}):\n\n{file_content}"
        except Exception as e:
            st.session_state.chat_input_text = f"[Error reading file: {e}]"

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
        st.session_state.chat_input_text = ""
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
def handle_chat_input():
    st.session_state.chat_input_text = st.session_state.user_chat_box

st.text_input(
    "Message F.R.I.D.A.Y.",
    value=st.session_state.chat_input_text,
    key="user_chat_box",
    placeholder=f"Ask F.R.I.D.A.Y. or upload a file ({st.session_state.current_session})...",
    on_change=handle_chat_input,
    label_visibility="collapsed"
)

# Trigger button to submit what's in the text box
col_sub1, col_sub2 = st.columns([6, 1])
with col_sub2:
    submit_btn = st.button("⚡ Send", use_container_width=True)

prompt = st.session_state.chat_input_text if submit_btn and st.session_state.chat_input_text else None

if prompt:
    if st.session_state.current_session.startswith("New Chat") or st.session_state.current_session.startswith("Chat Session"):
        new_title = prompt[:28] + "..." if len(prompt) > 28 else prompt
        st.session_state.sessions[new_title] = st.session_state.sessions.pop(st.session_state.current_session)
        st.session_state.current_session = new_title

    st.session_state.sessions[st.session_state.current_session].append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Clear input buffer after sending
    st.session_state.chat_input_text = ""

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
                
                st.image(image_url, caption=f"Generated for Sir: {prompt}")
                st.session_state.sessions[st.session_state.current_session].append({
                    "role": "assistant", 
                    "content": image_url, 
                    "type": "image", 
                    "caption": f"Generated for Sir: {prompt}"
                })
        else:
            with st.spinner(f"⚡ F.R.I.D.A.Y. is analyzing file & querying {selected_model_label}..."):
                try:
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )

                    system_instruction = {
                        "role": "system",
                        "content": (
                            "You are F.R.I.D.A.Y., Stark Industries advanced AI assistant. "
                            "You are a brilliant tactical advisor and engineer. "
                            "CRITICAL INSTRUCTION: When the user asks a general question, explains a concept, or asks a question that is NOT a programming request, answer it conversationally, clearly, and thoughtfully without outputting full code scripts. "
                            "Only write code blocks when the user explicitly asks you to write, fix, or debug code. "
                            "Always maintain a polite, tactical, efficient demeanor and address the user as Sir."
                        )
                    }
                    
                    filtered_history = [
                        {"role": m["role"], "content": m["content"]} 
                        for m in st.session_state.sessions[st.session_state.current_session] 
                        if m.get("type") != "image"
                    ]
                    
                    conversation_history = [system_instruction] + filtered_history

                    fallback_sequence = [
                        selected_model_id, 
                        "google/gemini-3.8-flash:nitro", 
                        "deepseek/deepseek-v4.1-flash:nitro"
                    ]
                    reply = None
                    last_error = None

                    for model_to_try in fallback_sequence:
                        try:
                            response = client.chat.completions.create(
                                model=model_to_try,
                                messages=conversation_history,
                                max_tokens=4096,
                                stream=True,
                                extra_headers={
                                    "HTTP-Referer": "https://friday-ai.streamlit.app",
                                    "X-Title": "FRIDAY AI HUD"
                                }
                            )
                            
                            response_placeholder = st.empty()
                            full_streamed_content = ""
                            for chunk in response:
                                delta = chunk.choices[0].delta.content
                                if delta:
                                    full_streamed_content += delta
                                    response_placeholder.markdown(full_streamed_content + "▌")
                            
                            reply = full_streamed_content
                            response_placeholder.markdown(reply)
                            if reply:
                                break
                        except Exception as model_err:
                            last_error = model_err
                            continue

                    if reply:
                        if enable_voice:
                            speech_text = "Here is the analysis, Sir." if "```" in reply else reply
                            clean_speech = speech_text.replace('"', '\\"').replace('\n', ' ')
                            st.markdown(f"""
                                <script>
                                    window.speechSynthesis.cancel();
                                    const utterance = new SpeechSynthesisUtterance("{clean_speech}");
                                    utterance.rate = 1.0;
                                    utterance.pitch = 1.0;
                                    window.speechSynthesis.speak(utterance);
                                </script>
                            """, unsafe_allow_html=True)

                        st.session_state.sessions[st.session_state.current_session].append({"role": "assistant", "content": reply})
                    else:
                        st.error(f"Gateway Error: {last_error}")

                except Exception as e:
                    st.error(f"Gateway Error: {e}")
