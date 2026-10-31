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
