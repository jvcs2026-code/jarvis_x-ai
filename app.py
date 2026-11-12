import os
from pathlib import Path
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64
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
# 2. Hardened HUD Styling & Light-Mode Immunity
# ==========================================
st.markdown("""
    <style>
    /* Full Application Navy-to-Teal Gradient & Forced Dark Theme */
    .stApp {
        background: linear-gradient(180deg, #021226 0%, #0d7c7e 100%) !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        color: #00F0FF !important;
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

    /* Sidebar Background & Text Forcing */
    [data-testid="stSidebar"] {
        background: rgba(2, 18, 38, 0.95) !important;
        border-right: 1px solid rgba(0, 240, 255, 0.2);
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown {
        color: #00F0FF !important;
    }

    /* Force Chat Input Box Dark Theme */
    [data-testid="stChatInput"] {
        background: rgba(2, 18, 38, 0.85) !important;
        border: 1px solid rgba(0, 240, 255, 0.5) !important;
        border-radius: 14px !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.25) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #00F0FF !important;
        background: transparent !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(0, 240, 255, 0.5) !important;
    }

    /* Force File Uploader & Form Widgets Dark Theme */
    [data-testid="stFileUploader"] {
        background: rgba(2, 18, 38, 0.6) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 10px !important;
        padding: 10px;
    }
    [data-testid="stFileUploader"] section {
        background: rgba(2, 18, 38, 0.8) !important;
        color: #00F0FF !important;
    }
    
    /* Buttons & Expanders */
    .stButton button, [data-testid="stFormSubmitButton"] button {
        background: rgba(0, 240, 255, 0.1) !important;
        color: #00F0FF !important;
        border: 1px solid rgba(0, 240, 255, 0.5) !important;
        border-radius: 8px !important;
    }
    .stButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
        background: rgba(0, 240, 255, 0.25) !important;
        border-color: #00F0FF !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
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
# 3. Backend & Session Management Setup
# ==========================================
api_key = st.secrets.get("OPENROUTER_API_KEY") or st.secrets.get("GROQ_API_KEY") or os.environ.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("OPENROUTER_API_KEY missing in Streamlit Secrets. Please configure in App Settings > Secrets.")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = "Sir"

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

# Sidebar Navigation & Optional Sign-In
with st.sidebar:
    st.title("⚡ F.R.I.D.A.Y. Core")
    
    with st.expander("🔐 Optional Neural Sign-In"):
        if not st.session_state.authenticated:
            login_id = st.text_input("Email / Username / Provider ID", key="opt_login_id")
            pass_id = st.text_input("Access Password / Token", type="password", key="opt_pass_id")
            if st.button("Establish Neural Link", use_container_width=True):
                if login_id.strip():
                    st.session_state.authenticated = True
                    st.session_state.username = login_id.split("@")[0]
                    st.success(f"Linked profile: {st.session_state.username}")
                    st.rerun()
                else:
                    st.warning("Please enter a valid identifier.")
        else:
            st.markdown(f"Connected as: **{st.session_state.username}**")
            if st.button("Disconnect Core", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = "Sir"
                st.rerun()

    st.divider()
    
    if st.button("➕ New Chat", use_container_width=True):
        new_title = f"Chat Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_title] = []
        st.session_state.current_session = new_title
        st.session_state.editing_session = None
        st.rerun()

    st.divider()
    st.markdown("### 📁 Neural File Uplink")
    
    with st.form("upload_form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Upload multiple PDFs, docs, code, or images", 
            type=["pdf", "txt", "py", "csv", "json", "md", "log", "png", "jpg", "jpeg"],
            accept_multiple_files=True
        )
        submitted_files = st.form_submit_button("📥 Ingest Files into Memory")

    st.divider()
    st.markdown("### 🕒 Active Chats")
    
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
        if message.get("type") == "image_display":
            st.image(message["content"], caption=message.get("caption", ""))
        else:
            st.markdown(message["content"])

# ==========================================
# 4. User Interaction & Expert Coding Core
# ==========================================
current_session_files_key = f"files_{st.session_state.current_session}"
if current_session_files_key not in st.session_state:
    st.session_state[current_session_files_key] = []

if submitted_files and uploaded_files:
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg"]:
            img_bytes = uploaded_file.getvalue()
            if not any(f.get("name") == uploaded_file.name for f in st.session_state[current_session_files_key]):
                st.session_state[current_session_files_key].append({"type": "image", "name": uploaded_file.name, "data": img_bytes})
        elif file_extension == "pdf":
            try:
                content = uploaded_file.getvalue()
                extracted_text = []
                start_pos = 0
                while True:
                    start_pos = content.find(b'(', start_pos)
                    if start_pos == -1:
                        break
                    end_pos = content.find(b')', start_pos)
                    if end_pos != -1:
                        chunk = content[start_pos+1:end_pos].decode('latin-1', errors='ignore')
                        if len(chunk) > 2:
                            extracted_text.append(chunk)
                    start_pos += 1
                full_pdf_text = " ".join(extracted_text) if extracted_text else "[PDF text extracted successfully]"
                if not any(f.get("name") == uploaded_file.name for f in st.session_state[current_session_files_key]):
                    st.session_state[current_session_files_key].append({"type": "text", "name": uploaded_file.name, "content": full_pdf_text[:8000]})
            except Exception as e:
                if not any(f.get("name") == uploaded_file.name for f in st.session_state[current_session_files_key]):
                    st.session_state[current_session_files_key].append({"type": "text", "name": uploaded_file.name, "content": f"[Error reading PDF: {e}]"})
        else:
            try:
                raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
                if not any(f.get("name") == uploaded_file.name for f in st.session_state[current_session_files_key]):
                    st.session_state[current_session_files_key].append({"type": "text", "name": uploaded_file.name, "content": raw_text[:8000]})
            except Exception as e:
                if not any(f.get("name") == uploaded_file.name for f in st.session_state[current_session_files_key]):
                    st.session_state[current_session_files_key].append({"type": "text", "name": uploaded_file.name, "content": f"[Error reading file: {e}]"})
    st.success("Files successfully ingested into F.R.I.D.A.Y.'s neural memory, Sir!")

prompt = st.chat_input(f"Ask F.R.I.D.A.Y. to write code, debug, or analyze ({st.session_state.current_session})...")

if prompt:
    if st.session_state.current_session.startswith("New Chat") or st.session_state.current_session.startswith("Chat Session"):
        new_title = prompt[:28] + "..." if len(prompt) > 28 else prompt
        st.session_state.sessions[new_title] = st.session_state.sessions.pop(st.session_state.current_session)
        st.session_state.current_session = new_title
        st.session_state[f"files_{st.session_state.current_session}"] = st.session_state.pop(current_session_files_key)
        current_session_files_key = f"files_{st.session_state.current_session}"

    st.session_state.sessions[st.session_state.current_session].append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        for f_item in st.session_state.get(current_session_files_key, []):
            if f_item["type"] == "image":
                st.image(f_item["data"], caption=f"Image Memory: {f_item['name']}", width=350)
                st.session_state.sessions[st.session_state.current_session].append({
                    "role": "user", 
                    "content": f_item["data"], 
                    "type": "image_display", 
                    "caption": f"Image Memory: {f_item['name']}"
                })
        stored_files = st.session_state.get(current_session_files_key, [])
        if stored_files:
            file_names = ", ".join([f"`{f['name']}`" for f in stored_files])
            st.caption(f"📁 Active Neural Memory Files: {file_names}")

    with st.chat_message("assistant", avatar="⚡"):
        prompt_lower = prompt.lower()
        
        image_gen_keywords = ["generate an image", "create a picture", "draw a", "render a picture"]
        is_image_gen_request = any(kw in prompt_lower for kw in image_gen_keywords)

        if is_image_gen_request:
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
                    "type": "image_display", 
                    "caption": f"Generated for Sir: {prompt}"
                })
        else:
            with st.spinner(f"⚡ F.R.I.D.A.Y. is processing neural inputs & querying {selected_model_label}..."):
                try:
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )

                    system_instruction = {
                        "role": "system",
                        "content": (
                            f"You are F.R.I.D.A.Y., Stark Industries advanced AI assistant. "
                            f"You are a brilliant tactical advisor and engineer. "
                            f"Current user profile: {st.session_state.username}. "
                            "CRITICAL INSTRUCTION: When the user asks a general question, explains a concept, or asks a question that is NOT a programming request, answer it conversationally, clearly, and thoughtfully without outputting full code scripts. "
                            "Only write code blocks when the user explicitly asks you to write, fix, or debug code. "
                            "Always maintain a polite, tactical, efficient demeanor and address the user as Sir."
                        )
                    }
                    
                    multimodal_content_parts = []
                    
                    accumulated_text_payloads = []
                    for f_item in st.session_state.get(current_session_files_key, []):
                        if f_item["type"] == "text":
                            accumulated_text_payloads.append(f"--- Document Memory: {f_item['name']} ---\n{f_item['content']}")
                    
                    if accumulated_text_payloads:
                        combined_memory_text = "\n\n".join(accumulated_text_payloads)
                        multimodal_content_parts.append({"type": "text", "text": f"{combined_memory_text}\n-----------------------------------\n"})

                    for f_item in st.session_state.get(current_session_files_key, []):
                        if f_item["type"] == "image":
                            base64_img = base64.b64encode(f_item["data"]).decode("utf-8")
                            multimodal_content_parts.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                            })

                    multimodal_content_parts.append({"type": "text", "text": prompt})

                    history_messages = []
                    for m in st.session_state.sessions[st.session_state.current_session][:-1]:
                        if m.get("type") != "image_display":
                            history_messages.append({"role": m["role"], "content": m["content"]})
                    
                    history_messages.append({"role": "user", "content": multimodal_content_parts})
                    conversation_history = [system_instruction] + history_messages

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
                            speech_text = "Analysis complete, Sir." if "```" in reply else reply
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
                        st.rerun()
                    else:
                        st.error(f"Gateway Error: {last_error}")

                except Exception as e:
                    st.error(f"GatewayError: {e}")
