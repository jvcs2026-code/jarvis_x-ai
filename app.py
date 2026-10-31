import streamlit as st
import os
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(
    page_title="JARVIS System HUD",
    page_icon="⚡",
    layout="wide"
)

# 2. Inject Futuristic Arc Reactor & Revolving Dotted Ring CSS
st.markdown("""
    <style>
    /* Dark Sci-Fi Background */
    .stApp {
        background: radial-gradient(circle at center, #0B192C 0%, #030712 100%);
        color: #00F0FF;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }

    /* Arc Reactor Container */
    .arc-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 15px;
        margin-bottom: 20px;
        position: relative;
    }

    /* Wrapper to center the revolving ring perfectly over the core */
    .reactor-wrapper {
        position: relative;
        width: 140px;
        height: 140px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Revolving Dotted Ring */
    .arc-ring {
        position: absolute;
        width: 140px;
        height: 140px;
        border-radius: 50%;
        border: 2px dashed #00F0FF;
        animation: rotateRing 10s linear infinite;
        opacity: 0.7;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
    }

    /* Glowing Core */
    .arc-reactor {
        position: absolute;
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 240, 255, 0.3) 0%, rgba(3, 7, 18, 0.9) 70%);
        border: 2px solid #00F0FF;
        box-shadow: 0 0 25px #00F0FF, inset 0 0 15px #00F0FF;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulseCore 2.5s infinite ease-in-out;
    }

    .arc-symbol {
        font-size: 2.2rem;
        text-shadow: 0 0 12px #00F0FF;
    }

    @keyframes rotateRing {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes pulseCore {
        0% { box-shadow: 0 0 15px #00F0FF, inset 0 0 10px #00F0FF; }
        50% { box-shadow: 0 0 35px #00F0FF, inset 0 0 20px #00F0FF; }
        100% { box-shadow: 0 0 15px #00F0FF, inset 0 0 10px #00F0FF; }
    }

    /* Glow Header Text */
    .hud-title {
        color: #00F0FF;
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: 4px;
        text-shadow: 0 0 15px rgba(0, 240, 255, 0.8);
        margin-top: 15px;
        margin-bottom: 2px;
        text-align: center;
    }

    .hud-sub {
        color: #10B981;
        font-size: 0.95rem;
        letter-spacing: 2px;
        font-weight: 600;
        text-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
        text-align: center;
        margin-bottom: 25px;
    }

    /* Custom Chat Message Cards */
    [data-testid="stChatMessage"] {
        background: rgba(11, 25, 44, 0.75) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.1) !important;
        margin-bottom: 12px !important;
        color: #E2E8F0 !important;
    }

    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
        border-left: 4px solid #00F0FF !important;
    }

    [data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
        border-left: 4px solid #10B981 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Centered Header Component with Revolving Dotted Ring & Core
st.markdown("""
    <div class="arc-container">
        <div class="reactor-wrapper">
            <div class="arc-ring"></div>
            <div class="arc-reactor">
                <span class="arc-symbol">⚡</span>
            </div>
        </div>
        <div class="hud-title">J.A.R.V.I.S.</div>
        <div class="hud-sub">● SYSTEM ONLINE | NEURAL CORE ACTIVE</div>
    </div>
""", unsafe_allow_html=True)

# 4. Secret API Key Fetch
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY missing in Streamlit Secrets. Please set it under App Settings > Secrets.")
    st.stop()

# 5. Session State Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls
with st.sidebar:
    st.title("⚙️ System Control")
    st.write("● **Status:** Fully Operational")
    st.write("● **Model:** Groq Llama 3 High-Speed")
    if st.button("🗑️ Clear Consciousness Log", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Render Messages
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 7. Chat Input
prompt = st.chat_input("At your service, sir. What can I calculate for you today?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("⚡ J.A.R.V.I.S. is processing neural pathways..."):
            try:
                client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=api_key,
                )

                system_instruction = {
                    "role": "system",
                    "content": "You are JARVIS, a highly sophisticated, articulate, helpful, and polite AI assistant. Address the user respectfully with occasional subtle refinement (e.g., 'Right away, sir', 'At your service'). Keep answers clear, technical, and precise."
                }
                
                conversation_history = [system_instruction] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]

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
                    st.error(f"System error: {last_error}")

            except Exception as e:
                st.error(f"Execution Error: {e}")
