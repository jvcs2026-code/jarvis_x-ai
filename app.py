import streamlit as st
import os
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(
    page_title="FRIDAY SYSTEM HUD",
    page_icon="⚡",
    layout="wide"
)

# 2. Inject Custom FRIDAY Blue Geometric HUD Styling
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
        margin-top: 15px;
        margin-bottom: 20px;
    }

    /* Shared Wrapper to Perfectly Center Dotted Ring Around Core */
    .friday-reactor-wrapper {
        position: relative;
        width: 150px;
        height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Revolving Dotted Outer Ring */
    .friday-ring-outer {
        position: absolute;
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 2px dashed rgba(0, 240, 255, 0.7);
        animation: rotateDashedRing 10s linear infinite;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
    }

    /* Core Pulsing Blue Geometric 'F' */
    .friday-core {
        position: absolute;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 240, 255, 0.3) 0%, rgba(1, 4, 9, 0.95) 80%);
        border: 2px solid #00F0FF;
        box-shadow: 0 0 30px #00F0FF, inset 0 0 15px #00F0FF;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulseFRIDAY 3s infinite ease-in-out;
    }

    /* Central Symbol - The Geometric 'F' */
    .friday-symbol {
        font-size: 3rem;
        font-weight: 900;
        color: #00F0FF;
        text-shadow: 0 0 20px #00F0FF;
        font-family: 'Courier New', monospace;
    }

    /* CSS Keyframe Animations */
    @keyframes rotateDashedRing {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes pulseFRIDAY {
        0% { box-shadow: 0 0 20px #00F0FF, inset 0 0 15px #00F0FF; }
        50% { box-shadow: 0 0 50px #00F0FF, inset 0 0 25px #00F0FF; }
        100% { box-shadow: 0 0 20px #00F0FF, inset 0 0 15px #00F0FF; }
    }

    /* Glow Header Text */
    .hud-title {
        color: #00F0FF;
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: 5px;
        text-shadow: 0 0 20px rgba(0, 240, 255, 1);
        margin-top: 15px;
        margin-bottom: 2px;
        text-align: center;
    }

    .hud-status {
        color: #10B981;
        font-size: 1.0rem;
        letter-spacing: 2px;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.8);
        text-align: center;
        margin-bottom: 30px;
    }

    /* Custom FRIDAY Chat Cards */
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

# 3. Render FRIDAY Header HUD Component
st.markdown("""
    <div class="friday-logo-container">
        <div class="friday-reactor-wrapper">
            <div class="friday-ring-outer"></div>
            <div class="friday-core">
                <span class="friday-symbol">F</span>
            </div>
        </div>
        <div class="hud-title">F.R.I.D.A.Y.</div>
        <div class="hud-status">● MULTI-MODEL NEURAL CORE & VISION ACTIVE</div>
    </div>
""", unsafe_allow_html=True)

# 4. OpenRouter API Key Fetch
api_key = st.secrets.get("OPENROUTER_API_KEY") or st.secrets.get("GROQ_API_KEY") or os.environ.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("OPENROUTER_API_KEY missing in Streamlit Secrets. Please configure in App Settings > Secrets.")
    st.stop()

# 5. Session State Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Model Registry with the correct OpenRouter slug for Flux 1 Schnell
MODEL_OPTIONS = {
    "Flux 1 Schnell (Fast Image Generation)": "black-forest-labs/flux-1-schnell",
    "Claude 3.5 Sonnet (Advanced Intelligence)": "anthropic/claude-3.5-sonnet",
    "GPT-4o (OpenAI)": "openai/gpt-4o",
    "Gemini Flash 1.5 (Google)": "google/gemini-flash-1.5",
    "Llama 3.3 70B Instruct (Meta)": "meta-llama/llama-3.3-70b-instruct"
}

# 6. Sidebar System Control & Interactive Model Selector
with st.sidebar:
    st.title("⚙️ System Control")
    st.markdown("● **Status:** Gateway Online")
    
    selected_model_label = st.selectbox(
        "🧠 Neural Model Core",
        options=list(MODEL_OPTIONS.keys()),
        index=0  
    )
    
    selected_model_id = MODEL_OPTIONS[selected_model_label]
    st.caption(f"Active Provider ID:\n`{selected_model_id}`")
    st.divider()

    if st.button("🗑️ Purge Consciousness Log", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 7. Render Messages with "⚡" Avatar
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "⚡"
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", ""))
        else:
            st.markdown(message["content"])

# 8. Chat Input Prompt
prompt = st.chat_input("Boss, what do you need me to analyze or generate?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner(f"⚡ F.R.I.D.A.Y. is executing via {selected_model_label.split(' ')[0]}..."):
            try:
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                )

                system_instruction = {
                    "role": "system",
                    "content": "You are F.R.I.D.A.Y., a highly articulate, intelligent, polite, and efficient AI assistant developed by Stark Industries. Address the user respectfully as 'Boss' or 'Sir', maintaining a calm, sophisticated, tactical demeanor."
                }
                
                conversation_history = [system_instruction] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m.get("type") != "image"
                ]

                response = client.chat.completions.create(
                    model=selected_model_id,
                    messages=conversation_history,
                    extra_headers={
                        "HTTP-Referer": "https://friday-ai.streamlit.app",
                        "X-Title": "FRIDAY AI HUD"
                    }
                )
                
                reply = response.choices[0].message.content
                
                if reply:
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    st.error("Execution Error: Empty response received.")

            except Exception as e:
                st.error(f"Gateway Error: {e}")
