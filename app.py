import streamlit as st
import os
import urllib.parse
import requests
from openai import OpenAI

# 1. Page Configuration with Custom Favicon
st.set_page_config(
    page_title="FRIDAY SYSTEM HUD",
    page_icon="friday.jpg",
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
        box-shadow: 0 0 15px rgba(0, 240, 255,
