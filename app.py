import streamlit as st
from g4f.client import Client
from g4f.Provider import PollinationsAI, DeepInfra

st.set_page_config(page_title="My Personal AI", layout="wide")
st.title("My Personal AI Assistant")
st.write("A 100% free AI assistant running without any API keys!")

# Initialize g4f client
client = Client()

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

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = None
            
            # Try free open providers sequentially without key requirements
            providers_to_try = [
                (PollinationsAI, "mistralai/Mistral-7B-Instruct-v0.3"),
                (PollinationsAI, "openai"),
                (DeepInfra, "meta-llama/Meta-Llama-3.1-70B-Instruct")
            ]

            for provider, model_name in providers_to_try:
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        provider=provider,
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    )
                    reply = response.choices[0].message.content
                    if reply:
                        break
                except Exception:
                    continue

            if reply:
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error("Free providers are busy right now. Please try sending your message again in a moment!")
