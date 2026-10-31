import os
from pathlib import Path
from io import BytesIO
import urllib.parse

import requests
import streamlit as st
from openai import OpenAI
from PIL import Image

# Find the favicon even if the GitHub filename has no extension.
BASE_DIR = Path(__file__).resolve().parent
favicon = None
for name in ("friday_favicon.png", "friday_favicon.ico", "friday_favicon", "friday.png"):
    candidate = BASE_DIR / name
    try:
        if candidate.is_file():
            with Image.open(candidate) as image:
                favicon = image.copy()
            break
    except (OSError, ValueError):
        pass

# Do not crash the app if the favicon is missing.
st.set_page_config(
    page_title="F.R.I.D.A.Y. AI",
    page_icon=favicon if favicon is not None else "⚡",
    layout="wide",
)

# Futuristic dark HUD styling.
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at center, #010409 0%, #000000 100%);
    color: #00F0FF;
    font-family: 'Segoe UI', Roboto, sans-serif;
}
.friday-logo-container {
    display:flex; flex-direction:column; align-items:center;
    justify-content:center; margin:15px 0 20px;
}
.friday-reactor-wrapper {
    position:relative; width:150px; height:150px;
    display:flex; align-items:center; justify-content:center;
}
.friday-ring-outer {
    position:absolute; width:150px; height:150px; border-radius:50%;
    border:2px dashed rgba(0,240,255,.7);
    animation:rotateDashedRing 10s linear infinite;
    box-shadow:0 0 12px rgba(0,240,255,.4);
}
.friday-core {
    position:absolute; width:100px; height:100px; border-radius:50%;
    background:radial-gradient(circle,rgba(0,240,255,.3),rgba(1,4,9,.95) 80%);
    border:2px solid #00F0FF; box-shadow:0 0 30px #00F0FF,inset 0 0 15px #00F0FF;
    display:flex; align-items:center; justify-content:center;
    animation:pulseFRIDAY 3s infinite ease-in-out;
}
.friday-symbol {
    font-size:3rem; font-weight:900; color:#00F0FF;
    text-shadow:0 0 20px #00F0FF; font-family:'Courier New',monospace;
}
@keyframes rotateDashedRing { from{transform:rotate(0)} to{transform:rotate(360deg)} }
@keyframes pulseFRIDAY {
    0%,100%{box-shadow:0 0 20px #00F0FF,inset 0 0 15px #00F0FF}
    50%{box-shadow:0 0 50px #00F0FF,inset 0 0 25px #00F0FF}
}
.hud-title {
    color:#00F0FF; font-size:2.8rem; font-weight:900; letter-spacing:5px;
    text-shadow:0 0 20px #00F0FF; margin-top:15px; text-align:center;
}
.hud-status {
    color:#10B981; font-size:1rem; letter-spacing:2px; font-weight:600;
    text-shadow:0 0 10px rgba(16,185,129,.8); text-align:center; margin-bottom:30px;
}
[data-testid="stChatMessage"] {
    background:rgba(1,4,9,.8)!important;
    border:1px solid rgba(0,240,255,.4)!important;
    border-radius:12px!important; box-shadow:0 0 15px rgba(0,240,255,.2)!important;
    margin-bottom:12px!important;
}
[data-testid="stSidebar"] { background:rgba(2,8,18,.98); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="friday-logo-container">
  <div class="friday-reactor-wrapper">
    <div class="friday-ring-outer"></div>
    <div class="friday-core"><span class="friday-symbol">F</span></div>
  </div>
  <div class="hud-title">F.R.I.D.A.Y.</div>
  <div class="hud-status">MULTI-MODEL NEURAL CORE &amp; IMAGE SYNTHESIS</div>
</div>
""", unsafe_allow_html=True)

# Read the key from Streamlit Cloud Secrets or environment variables.
try:
    api_key = (
        st.secrets.get("OPENROUTER_API_KEY")
        or st.secrets.get("GROQ_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
    )
except Exception:
    api_key = os.environ.get("OPENROUTER_API_KEY")

if "messages" not in st.session_state:
    st.session_state.messages = []

MODEL_OPTIONS = {
    "Claude 3.5 Sonnet (Anthropic)": "anthropic/claude-3.5-sonnet",
    "GPT-4o (OpenAI)": "openai/gpt-4o",
    "Gemini Flash 1.5 (Google)": "google/gemini-flash-1.5",
    "Llama 3.3 70B Instruct (Meta)": "meta-llama/llama-3.3-70b-instruct",
    "DeepSeek V3 (DeepSeek)": "deepseek/deepseek-chat",
}

with st.sidebar:
    st.title("⚙️ System Control")
    st.markdown("**Status:** " + ("Gateway key detected" if api_key else "API key missing"))
    selected_model_label = st.selectbox(
        "Neural Model Core", list(MODEL_OPTIONS.keys()), index=3
    )
    selected_model_id = MODEL_OPTIONS[selected_model_label]
    st.caption(f"Active Provider ID: `{selected_model_id}`")
    st.divider()
    if st.button("Purge Consciousness Log", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Restore previous text and generated-image messages.
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "⚡"
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", ""))
        else:
            st.markdown(message["content"])

prompt = st.chat_input("What do you need me to analyze or create?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        lower = prompt.lower().strip()
        image_words = ("image", "picture", "photo", "draw", "render",
                       "generate", "create", "make", "painting", "art", "sketch")
        is_image_request = any(word in lower for word in image_words)

        if is_image_request:
            with st.spinner("F.R.I.D.A.Y. is preparing your image..."):
                image_prompt = prompt
                prefixes = (
                    "generate an image of", "generate a image of", "generate image of",
                    "generate", "create an image of", "create a picture of",
                    "create an image", "create", "draw a", "draw an", "draw",
                    "render a", "render", "make an image of", "make a picture of",
                    "make an image", "make",
                )
                for prefix in prefixes:
                    if lower.startswith(prefix):
                        image_prompt = prompt[len(prefix):].strip()
                        break
                if not image_prompt:
                    image_prompt = prompt
                image_url = (
                    "https://pollinations.ai/p/" + urllib.parse.quote(image_prompt)
                    + "?width=1024&height=1024&model=flux&nologo=true"
                )
                try:
                    result = requests.get(image_url, timeout=60)
                    result.raise_for_status()
                    st.image(BytesIO(result.content), caption=f"Generated image: {prompt}")
                    st.session_state.messages.append({
                        "role": "assistant", "content": image_url, "type": "image",
                        "caption": f"Generated image: {prompt}",
                    })
                except Exception as error:
                    st.error("Image generation failed. Please try again.")
                    st.caption(f"Technical detail: {error}")
        elif not api_key:
            st.error("OpenRouter API key is missing. Add OPENROUTER_API_KEY under Streamlit Cloud → App settings → Secrets.")
        else:
            with st.spinner(f"F.R.I.D.A.Y. is querying {selected_model_label}..."):
                try:
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                    system_message = {
                        "role": "system",
                        "content": (
                            "You are F.R.I.D.A.Y., a helpful, polite, technically precise "
                            "AI assistant. Explain steps clearly for beginners when useful. "
                            "Never claim to have performed actions you did not perform."
                        ),
                    }
                    history = [
                        {"role": item["role"], "content": item["content"]}
                        for item in st.session_state.messages if item.get("type") != "image"
                    ]
                    messages = [system_message] + history
                    models = list(dict.fromkeys([
                        selected_model_id,
                        "meta-llama/llama-3.3-70b-instruct",
                        "google/gemini-flash-1.5",
                    ]))
                    reply, last_error = None, None
                    for model_id in models:
                        try:
                            response = client.chat.completions.create(
                                model=model_id,
                                messages=messages,
                                extra_headers={
                                    "HTTP-Referer": "https://friday-ai.streamlit.app",
                                    "X-Title": "FRIDAY AI HUD",
                                },
                            )
                            reply = response.choices[0].message.content
                            if reply:
                                break
                        except Exception as error:
                            last_error = error
                    if reply:
                        st.markdown(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    else:
                        st.error("The AI gateway did not return a response. Check API key, credits, and model access.")
                        if last_error:
                            st.caption(f"Technical detail: {last_error}")
                except Exception as error:
                    st.error("The AI gateway request failed.")
                    st.caption(f"Technical detail: {error}")
