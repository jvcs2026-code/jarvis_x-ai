import streamlit as st
import os
from openai import OpenAI
import time

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
        margin-top: 20px;
        margin-bottom: 25px;
        position: relative;
    }

    /* Core Pulsing Blue Geometric 'F' */
    .friday-core {
        position: relative;
        width: 130px;
        height: 130px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 240, 255, 0.25) 0%, rgba(0,0,0,1) 80%);
        border: 2px solid #00F0FF;
        box-shadow: 0 0 35px #00F0FF, inset 0 0 20px #00F0FF;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulseFRIDAY 3s infinite ease-in-out;
    }

    /* Rotational Blue Geometric Outer Rings */
    .friday-ring-wrapper {
        position: absolute;
        width: 170px;
        height: 170px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .friday-ring-outer {
        position: absolute;
        width: 170px;
        height: 170px;
        border-radius: 50%;
        border: 2px dashed rgba(0, 240, 255, 0.6);
        animation: rotateDashedRing 12s linear infinite;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
    }

    /* Central Symbol - The Geometric 'F' */
    .friday-symbol {
        font-size: 3.5rem;
        font-weight: 900;
        color: #00F0FF;
        text-shadow: 0 0 20px #00F0FF;
        font-family: 'Courier New', monospace; /* More geometric/tech feel */
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
        color: #10B981; /* Green status */
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

    /* User Chat Card */
    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
        border-left: 4px solid #00F0FF !important;
    }

    /* FRIDAY Assistant Chat Card */
    [data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
        border-left: 4px solid #10B981 !important; /* Matches green status */
    }
    </style>
""", unsafe_allow_html=True)

# 3. Render FRIDAY Blue Geometric HUD Component
st.markdown("""
    <div class="friday-logo-container">
        <div class="friday-ring-wrapper">
            <div class="friday-ring-outer"></div>
        </div>
        <div class="friday-core">
            <span class="friday-symbol">F</span>
        </div>
        <div class="hud-title">F.R.I.D.A.Y.</div>
        <div class="hud-status">● NEURAL PATHWAYS ONLINE | SYSTEM OPERATIONAL</div>
    </div>
""", unsafe_allow_html=True)

# 4. Groq Secret Retrieval
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY missing in Streamlit Secrets. Please configure in App Settings > Secrets.")
    st.stop()

# 5. Session State Management
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls
with st.sidebar:
    st.title("⚙️ System Control")
    st.write("● **Status:** Normal Operational Parameters")
    st.write("● **Model:** Groq Llama 3 High-Speed")
    if st.button("🗑️ Purge Consciousness Log", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Display Chat History
for message in st.session_state.messages:
    # Set icons matching the new HUD look
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 7. Chat Input
prompt = st.chat_input("Boss, what do you need me to analyze?")

if prompt:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # thinking/stream spinner
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("⚡ F.R.I.D.A.Y. is processing neural pathways..."):
            try:
                client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=api_key,
                )

                # high tech system instruction specifying the F.R.I.D.A.Y. persona
                system_instruction = {
                    "role": "system",
                    "content": "You are F.R.I.D.A.Y., a highly articulate, intelligent, polite, and efficient AI assistant developed by Stark Industries. Address the user respectfully as 'Boss' or 'Sir', maintaining a calm, sophisticated, tactical demeanor. Your answers should be technically precise, clear, and proactive."
                }
                
                conversation_history = [system_instruction] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]

                # models
                available_models = ["openai/gpt-oss-120b", "llama-3.1-8b-instant", "openai/gpt-oss-20b"]
                reply = None
                last_error = None

                for model_name in available_models:
                    try:
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=conversation_history
                        )
                        reply = response.choices[0].message.content
                        if reply:
                            break
                    except Exception as model_err:
                        last_error = model_err
                        continue

                if reply:
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    st.error(f"Execution Error: {last_error}")

            except Exception as e:
                st.error(f"Error: {e}")
