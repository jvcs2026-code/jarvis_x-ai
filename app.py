import streamlit as st
import os
from openai import OpenAI

# Page Configuration
st.set_page_config(
    page_title="JARVIS AI",
    page_icon="🤖",
    layout="wide"
)

# Custom High-Tech/Futuristic Theme Styling
st.markdown("""
    <style>
    /* Dark Futuristic Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #c9d1d9;
    }
    
    /* Title Styling with Cyan Glow */
    .jarvis-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #00f2fe;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        letter-spacing: 3px;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);
        margin-bottom: 0px;
    }
    
    /* Subtitle Styling */
    .jarvis-subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 1.1rem;
        font-weight: 400;
        letter-spacing: 1.5px;
        margin-bottom: 25px;
    }

    /* Custom Chat Message Containers */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* User Message Styling */
    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
        background-color: #1f242d;
        border-left: 4px solid #00f2fe;
    }

    /* JARVIS Assistant Message Styling */
    [data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
        background-color: #161b22;
        border-left: 4px solid #38ef7d;
    }
    </style>
""", unsafe_allow_html=True)

# App Headers
st.markdown('<h1 class="jarvis-title">⚡ J.A.R.V.I.S.</h1>', unsafe_allow_html=True)
st.markdown('<p class="jarvis-subtitle">JUST A RATHER VERY INTELLIGENT SYSTEM</p>', unsafe_allow_html=True)

# Retrieve secret key
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY missing in Streamlit Secrets. Please configure in App Settings > Secrets.")
    st.stop()

# Initialize session messages and system persona
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input
prompt = st.chat_input("At your service, sir. What can I do for you today?")

if prompt:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    try:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )

        # System prompt giving it the true JARVIS persona
        system_instruction = {
            "role": "system",
            "content": "You are JARVIS, a highly intelligent, polite, efficient, and sophisticated AI assistant. Respond helpfully, clearly, and with a touch of polite refinement."
        }
        
        conversation_history = [system_instruction] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]

        # Active Groq models
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
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.error(f"Execution error: {last_error}")

    except Exception as e:
        st.error(f"Error: {e}")
