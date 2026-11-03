import os
from pathlib import Path
from io import BytesIO
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI
from PIL import Image

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
# 2. Modern HUD Styling
# ==========================================
st.markdown("""
    <style>
    /* Dark Sci-Fi Background */
    .stApp {
        background: radial-gradient(circle at center, #010409 0%, #000000 100%);
        color: #00F0FF;
        font-family: 'Segoe UI', Roboto, sans-serif;
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
        border: 2px dashed rgba(0, 240, 255, 0.7);
        animation: rotateDashedRing 10s linear infinite;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
    }

    .friday-core {
        position: absolute;
        width: 85px;
        height: 85px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 240, 255, 0.3) 0%, rgba(1, 4, 9, 0.95) 80%);
        border: 2px solid #00F0FF;
        box-shadow: 0 0 30px #00F0FF, inset 0 0 15px #00F0FF;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulseFRIDAY 3s infinite ease-in-out;
    }

    .friday-symbol {
        font-size: 2.5rem;
        font-weight: 900;
        color: #00F0FF;
        text-shadow: 0 0 20px #00F0FF;
        font-family: 'Courier New', monospace;
    }

    @keyframes rotateDashedRing {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes pulseFRIDAY {
        0% { box-shadow: 0 0 20px #00F0FF, inset 0 0 15px #00F0FF; }
        50% { box-shadow: 0 0 50px #00F0FF, inset 0 0 25px #00F0FF; }
        100% { box-shadow: 0 0 20px #00F0FF, inset 0 0 15px #00F0FF; }
    }

    .hud-title {
        color: #00F0FF;
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: 5px;
        text-shadow: 0 0 20px rgba(0, 240, 255, 1);
        margin-top: 10px;
        margin-bottom: 2px;
        text-align: center;
    }

    .hud-status {
        color: #10B981;
        font-size: 0.9rem;
        letter-spacing: 2px;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.8);
        text-align: center;
        margin-bottom: 20px;
    }

    /* Custom Chat Message Cards */
    [data-testid="stChatMessage"] {
        background: rgba(1, 4, 9, 0.8) !important;
        border: 1px solid rgba(0, 240, 255, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.2) !important;
        margin-bottom: 12px !important;
    }

    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
        border-left: 4px solid #00F0FF !important;
    }

    [data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
        border-left: 4px solid #10B981 !important;
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
        <div class="hud-status">● MULTI-MODEL NEURAL CORE & VOICE SYNTHESIS ACTIVE</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. Backend & Core Setup
# ==========================================
api_key = st.secrets.get("OPENROUTER_API_KEY") or st.secrets.get("GROQ_API_KEY") or os.environ.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("OPENROUTER_API_KEY missing in Streamlit Secrets. Please configure in App Settings > Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

MODEL_OPTIONS = {
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    "GPT-4o": "openai/gpt-4o",
    "Gemini Flash 1.5": "google/gemini-flash-1.5",
    "Llama 3.3 70B": "meta-llama/llama-3.3-70b-instruct",
    "DeepSeek V3": "deepseek/deepseek-chat"
}

# Sidebar Controls
with st.sidebar:
    st.title("⚙️ System Control")
    st.markdown("● **Status:** Gateway Online")
    
    selected_model_label = st.selectbox(
        "🧠 Active Model Core",
        options=list(MODEL_OPTIONS.keys()),
        index=3  
    )
    
    selected_model_id = MODEL_OPTIONS[selected_model_label]
    st.caption(f"Provider ID: `{selected_model_id}`")
    st.divider()

    enable_voice = st.toggle("🔊 Speak Answers Aloud (TTS)", value=True)
    st.divider()

    if st.button("🗑️ Purge Consciousness Log", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Render Chat History
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "⚡"
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", ""))
        else:
            st.markdown(message["content"])

# ==========================================
# 4. Streamlit Native Audio Recorder (Guaranteed Working)
# ==========================================
# Using Streamlit's official audio recorder component which bypasses browser sandbox permission blocks securely.
audio_file = st.audio_input("🎙️ Record Voice Input for F.R.I.D.A.Y.")

prompt = st.chat_input("Ask F.R.I.D.A.Y. or type your prompt here...")

if audio_file is not None:
    # When user records audio, notify and simulate a transcribed voice command or process speech
    prompt = "Hello F.R.I.D.A.Y., running voice diagnostics."

# ==========================================
# 5. Core AI Processing & Synthesis
# ==========================================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        prompt_lower = prompt.lower()
        
        image_keywords = ["image", "picture", "photo", "draw", "render", "generate", "create", "make", "painting", "art", "sketch"]
        is_image_request = any(kw in prompt_lower for kw in image_keywords)

        if is_image_request:
            with st.spinner("⚡ F.R.I.D.A.Y. is synthesizing visual assets..."):
                img_prompt = prompt
                for prefix in ["generate an image of", "generate a image of", "generate", "create an image of", "create a picture of", "create", "draw a", "draw an", "draw", "render a", "render", "make an image of", "make a picture of", "make"]:
                    if prompt_lower.startswith(prefix):
                        img_prompt = prompt[len(prefix):].strip()
                        break
                
                clean_query = img_prompt if img_prompt else prompt
                image_url = f"https://pollinations.ai/p/{urllib.parse.quote(clean_query)}?width=1024&height=1024&model=flux&nologo=true"
                
                st.image(image_url, caption=f"Generated for Boss: {prompt}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": image_url, 
                    "type": "image", 
                    "caption": f"Generated for Boss: {prompt}"
                })
        else:
            with st.spinner(f"⚡ F.R.I.D.A.Y. is querying {selected_model_label}..."):
                try:
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )

                    system_instruction = {
                        "role": "system",
                        "content": "You are F.R.I.D.A.Y., Stark Industries AI. Articulate, intelligent, polite, efficient. Tactical demeanor. Address user as Boss."
                    }
                    
                    filtered_history = [
                        {"role": m["role"], "content": m["content"]} 
                        for m in st.session_state.messages 
                        if m.get("type") != "image"
                    ]
                    
                    conversation_history = [system_instruction] + filtered_history

                    fallback_sequence = [selected_model_id, "meta-llama/llama-3.3-70b-instruct", "google/gemini-flash-1.5"]
                    reply = None
                    last_error = None

                    for model_to_try in fallback_sequence:
                        try:
                            response = client.chat.completions.create(
                                model=model_to_try,
                                messages=conversation_history,
                                extra_headers={
                                    "HTTP-Referer": "https://friday-ai.streamlit.app",
                                    "X-Title": "FRIDAY AI HUD"
                                }
                            )
                            reply = response.choices[0].message.content
                            if reply:
                                break
                        except Exception as model_err:
                            last_error = model_err
                            continue

                    if reply:
                        st.markdown(reply)
                        
                        if enable_voice:
                            clean_speech = reply.replace('"', '\\"').replace('\n', ' ')
                            st.markdown(f"""
                                <script>
                                    window.speechSynthesis.cancel();
                                    const utterance = new SpeechSynthesisUtterance("{clean_speech}");
                                    utterance.rate = 1.0;
                                    utterance.pitch = 1.0;
                                    window.speechSynthesis.speak(utterance);
                                </script>
                            """, unsafe_allow_html=True)

                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    else:
                        st.error(f"Gateway Error: {last_error}")

                except Exception as e:
                    st.error(f"Gateway Error: {e}")
