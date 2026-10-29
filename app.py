import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="My Personal AI", layout="wide")
st.title("My Personal AI Assistant")
st.write("A public AI assistant powered by Streamlit Cloud.")

# Get API key from Streamlit Secrets or Environment
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not api_key:
    api_key = st.text_input("Enter your Groq API Key (or set in Streamlit Secrets):", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask me anything...")

if prompt:
    if not api_key:
        st.error("Please provide an API Key to continue.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key,
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            
            reply = response.choices[0].message.content
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Error: {e}")