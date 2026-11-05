import os
from pathlib import Path
import urllib.parse
import requests
import streamlit as st
from openai import OpenAI
from PIL import Image

# Page Config & Title
st.set_page_config(
    page_title="F.R.I.D.A.Y. AI Assistant",
    page_icon="⚡",
    layout="wide"
)

# Initialize OpenAI Client (Uses environment variable or fallback input)
api_key = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=api_key) if api_key else None

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "F.R.I.D.A.Y. systems online, Boss. How can I assist you today?"}
    ]

# Sidebar Configuration
with st.sidebar:
    st.title("⚡ F.R.I.D.A.Y. Core")
    
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "F.R.I.D.A.Y. systems online, Boss. How can I assist you today?"}
        ]
        st.rerun()

    st.markdown("---")
    st.subheader("⚙️ System Settings")
    
    # Model Selection
    selected_model = st.selectbox(
        "Select Active Engine:",
        ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "deepseek-chat"],
        index=0
    )
    
    tts_enabled = st.toggle("🔊 Speak Answers Aloud (TTS)", value=False)

    st.markdown("---")
    if st.button("🗑️ Purge All Logs", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display Chat History
st.title("F.R.I.D.A.Y. Interface")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Handling
if prompt := st.chat_input("Command F.R.I.D.A.Y..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response with streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            if client:
                # High-speed streaming response via OpenAI SDK client
                stream = client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                    temperature=0.3
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            else:
                # Fallback API request if OpenAI client key is not configured
                payload = {
                    "messages": st.session_state.messages,
                    "model": selected_model,
                    "stream": True,
                    "temperature": 0.3
                }
                response = requests.post("https://text.pollinations.ai/", json=payload, stream=True, timeout=30)
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=64, decode_unicode=True):
                        if chunk:
                            full_response += chunk
                            response_placeholder.markdown(full_response + "▌")
                    response_placeholder.markdown(full_response)
                else:
                    full_response = f"⚠️ Server Error ({response.status_code}): Check API Configuration."
                    response_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ Error: {str(e)}"
            response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
