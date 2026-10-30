import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="My Personal AI", layout="wide")
st.title("My Personal AI Assistant")
st.write("Powered by Groq Cloud — Fast & Free!")

# Secret retrieved securely behind the scenes
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is missing in Streamlit Secrets. Please set it in App Settings > Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask me anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )
        
        # Try active Groq models in order
        available_models = ["openai/gpt-oss-120b", "llama-3.1-8b-instant", "openai/gpt-oss-20b"]
        reply = None
        last_error = None

        for model_name in available_models:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )
                reply = response.choices[0].message.content
                if reply:
                    break
            except Exception as model_err:
                last_error = model_err
                continue

        if reply:
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.error(f"Error calling model: {last_error}")

    except Exception as e:
        st.error(f"Error: {e}")
