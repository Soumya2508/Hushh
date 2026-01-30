import streamlit as st
import requests
import json
import os
import time
import re
import uuid
from datetime import datetime

# Configuration & Theming
st.set_page_config(
    page_title="Hushh | AI Concierge",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium UI CSS with Enhanced Design
PREMIUM_CSS = """
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #050508;
        --bg-secondary: #0d0d14;
        --bg-card: #12121c;
        --bg-card-hover: #1a1a28;
        --bg-elevated: #181824;
        
        /* Vibrant accent colors */
        --accent-primary: #00d4ff;
        --accent-secondary: #a855f7;
        --accent-tertiary: #f472b6;
        --accent-success: #10b981;
        --accent-warning: #f59e0b;
        --accent-danger: #ef4444;
        --accent-gold: #fbbf24;
        
        /* Gradient combinations */
        --gradient-primary: linear-gradient(135deg, #00d4ff 0%, #a855f7 50%, #f472b6 100%);
        --gradient-glow: linear-gradient(135deg, rgba(0,212,255,0.4) 0%, rgba(168,85,247,0.4) 100%);
        --gradient-card: linear-gradient(145deg, rgba(18,18,28,0.95) 0%, rgba(13,13,20,0.95) 100%);
        --gradient-glass: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.02) 100%);
        
        /* Text colors */
        --text-primary: #ffffff;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --text-accent: #00d4ff;
        
        /* Borders */
        --border-subtle: rgba(255,255,255,0.06);
        --border-default: rgba(255,255,255,0.1);
        --border-hover: rgba(0,212,255,0.3);
        --border-active: rgba(168,85,247,0.5);
        
        /* Shadows */
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 20px rgba(0,0,0,0.4);
        --shadow-lg: 0 8px 40px rgba(0,0,0,0.5);
        --shadow-glow: 0 0 40px rgba(0,212,255,0.15);
        --shadow-purple-glow: 0 0 40px rgba(168,85,247,0.15);
    }
    
    /* Base styles */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    
    [data-testid="stSidebarContent"] {
        background: transparent !important;
        padding: 1rem;
    }
    
    /* Main container */
    .main .block-container {
        background: transparent !important;
        padding: 2rem 3rem;
        max-width: 1600px;
    }
    
    /* Premium Glassmorphism Panel */
    .glass-panel {
        background: var(--gradient-card);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-default);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: var(--gradient-glass);
    }
    
    .glass-panel:hover {
        border-color: var(--border-hover);
        box-shadow: var(--shadow-glow);
        transform: translateY(-2px);
    }
    
    /* Animated Profile Avatar */
    .profile-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: var(--gradient-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000;
        font-size: 32px;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        margin: 0 auto 20px;
        position: relative;
        animation: float 4s ease-in-out infinite;
    }
    
    .profile-avatar::before {
        content: '';
        position: absolute;
        inset: -3px;
        border-radius: 50%;
        background: var(--gradient-primary);
        z-index: -1;
        animation: rotateGlow 3s linear infinite;
    }
    
    .profile-avatar::after {
        content: '';
        position: absolute;
        inset: -8px;
        border-radius: 50%;
        background: var(--gradient-primary);
        z-index: -2;
        opacity: 0.3;
        filter: blur(15px);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    @keyframes rotateGlow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
    }
    
    /* Enhanced Avoid Badge */
    .avoid-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        background: rgba(239,68,68,0.1);
        color: var(--accent-danger);
        border: 1px solid rgba(239,68,68,0.25);
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .avoid-badge::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(239,68,68,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .avoid-badge:hover {
        background: rgba(239,68,68,0.2);
        transform: translateX(2px);
        box-shadow: 0 4px 15px rgba(239,68,68,0.2);
    }
    
    .avoid-badge:hover::before {
        left: 100%;
    }
    
    /* Memory Chips */
    .memory-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        background: rgba(0,212,255,0.08);
        color: var(--accent-primary);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 4px;
        transition: all 0.3s ease;
    }
    
    .memory-chip:hover {
        background: rgba(0,212,255,0.15);
        box-shadow: 0 0 20px rgba(0,212,255,0.2);
    }
    
    .chip-brand {
        background: rgba(168,85,247,0.08);
        color: var(--accent-secondary);
        border-color: rgba(168,85,247,0.2);
    }
    
    .chip-brand:hover {
        background: rgba(168,85,247,0.15);
        box-shadow: 0 0 20px rgba(168,85,247,0.2);
    }
    
    /* Premium Chat Container */
    .chat-container {
        background: var(--bg-secondary);
        border-radius: 24px;
        border: 1px solid var(--border-subtle);
        min-height: 550px;
        padding: 28px;
        position: relative;
        overflow: hidden;
    }
    
    .chat-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 100px;
        background: linear-gradient(180deg, var(--bg-card) 0%, transparent 100%);
        pointer-events: none;
        z-index: 1;
        opacity: 0.5;
    }
    
    /* Enhanced Message Bubbles */
    .message-bubble {
        max-width: 75%;
        padding: 16px 22px;
        margin: 16px 0;
        font-size: 0.95rem;
        line-height: 1.6;
        position: relative;
        animation: messageSlide 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    .msg-user {
        background: var(--gradient-primary);
        color: #000;
        border-radius: 24px 24px 6px 24px;
        margin-left: auto;
        font-weight: 500;
        box-shadow: 0 8px 25px rgba(0,212,255,0.25);
        position: relative;
    }
    
    .msg-user::after {
        content: '👤';
        position: absolute;
        right: -40px;
        bottom: 0;
        font-size: 24px;
    }
    
    .msg-agent {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border-default);
        border-radius: 24px 24px 24px 6px;
        margin-right: auto;
        position: relative;
    }
    
    .msg-agent::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(135deg, rgba(168,85,247,0.3) 0%, transparent 50%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    
    .msg-agent::after {
        content: '✦';
        position: absolute;
        left: -40px;
        bottom: 0;
        font-size: 24px;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    @keyframes messageSlide {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Question Card */
    .question-card {
        background: linear-gradient(145deg, rgba(0,212,255,0.08) 0%, rgba(168,85,247,0.08) 100%);
        border: 1px solid rgba(0,212,255,0.25);
        border-radius: 20px;
        padding: 28px;
        margin: 24px 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .question-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0,212,255,0.1) 0%, transparent 70%);
        animation: rotateGradient 10s linear infinite;
    }
    
    @keyframes rotateGradient {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .question-text {
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 20px;
        color: var(--text-primary);
        position: relative;
        z-index: 1;
    }
    
    .progress-indicator {
        color: var(--accent-primary);
        font-size: 0.8rem;
        margin-bottom: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
    }
    
    /* Results Header */
    .results-header {
        background: linear-gradient(90deg, rgba(16,185,129,0.1) 0%, transparent 100%);
        border-left: 4px solid var(--accent-success);
        padding: 18px 24px;
        border-radius: 0 16px 16px 0;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .results-header h3 {
        margin: 0;
        color: var(--accent-success);
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
    
    /* Premium Product Grid */
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 24px;
        margin-top: 24px;
    }
    
    /* 3D Product Card */
    .product-card {
        background: var(--bg-card);
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid var(--border-subtle);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        transform-style: preserve-3d;
    }
    
    .product-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(135deg, transparent 0%, rgba(0,212,255,0.3) 50%, transparent 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .product-card:hover {
        transform: translateY(-8px) rotateX(2deg);
        border-color: var(--border-hover);
        box-shadow: 
            0 20px 40px rgba(0,0,0,0.4),
            0 0 60px rgba(0,212,255,0.1);
    }
    
    .product-card:hover::before {
        opacity: 1;
    }
    
    /* Product Image with Shimmer */
    .product-image {
        width: 100%;
        height: 200px;
        background: linear-gradient(135deg, var(--bg-elevated) 0%, var(--bg-card) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 72px;
        position: relative;
        border-bottom: 1px solid var(--border-subtle);
        overflow: hidden;
    }
    
    .product-image::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 50%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 200%; }
    }
    
    /* Match Badge */
    .match-badge {
        position: absolute;
        top: 14px;
        right: 14px;
        background: rgba(0,0,0,0.85);
        backdrop-filter: blur(10px);
        color: var(--accent-success);
        padding: 8px 14px;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 700;
        border: 1px solid rgba(16,185,129,0.4);
        box-shadow: 0 4px 15px rgba(16,185,129,0.2);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .match-badge::before {
        content: '✓';
        font-size: 0.7rem;
    }
    
    /* Product Info */
    .product-info {
        padding: 22px;
    }
    
    .product-brand {
        color: var(--accent-secondary);
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .product-brand::before {
        content: '';
        width: 8px;
        height: 8px;
        background: var(--accent-secondary);
        border-radius: 50%;
    }
    
    .product-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 10px;
        line-height: 1.4;
        font-family: 'Outfit', sans-serif;
    }
    
    .product-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }
    
    .tag {
        padding: 5px 12px;
        background: rgba(0,212,255,0.08);
        color: var(--accent-primary);
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid rgba(0,212,255,0.15);
        transition: all 0.3s ease;
    }
    
    .tag:hover {
        background: rgba(0,212,255,0.15);
        transform: translateY(-1px);
    }
    
    .product-price {
        color: var(--accent-primary);
        font-size: 1.5rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        display: flex;
        align-items: baseline;
        gap: 4px;
    }
    
    .product-price::before {
        content: '₹';
        font-size: 1rem;
        opacity: 0.8;
    }
    
    /* Status Pills */
    .status-pill {
        padding: 10px 18px;
        border-radius: 14px;
        font-size: 0.85rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    
    .status-filled {
        border-color: rgba(16,185,129,0.3);
        color: var(--accent-success);
        background: rgba(16,185,129,0.08);
    }
    
    .status-filled::before {
        content: '';
        width: 8px;
        height: 8px;
        background: var(--accent-success);
        border-radius: 50%;
        box-shadow: 0 0 10px var(--accent-success);
    }
    
    .status-pending {
        border-color: rgba(245,158,11,0.3);
        color: var(--accent-warning);
        background: rgba(245,158,11,0.08);
    }
    
    .status-pending::before {
        content: '';
        width: 8px;
        height: 8px;
        background: var(--accent-warning);
        border-radius: 50%;
        animation: blink 1.5s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* Enhanced Thinking Animation */
    .thinking {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 18px 24px;
        background: var(--bg-card);
        border-radius: 20px;
        border: 1px solid var(--border-default);
        width: fit-content;
        margin: 16px 0;
        animation: fadeInUp 0.4s ease;
    }
    
    .thinking-text {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .thinking-dots {
        display: flex;
        gap: 6px;
    }
    
    .dot {
        width: 10px;
        height: 10px;
        background: var(--accent-primary);
        border-radius: 50%;
        animation: wave 1.4s ease-in-out infinite;
    }
    
    .dot:nth-child(2) { animation-delay: 0.2s; background: var(--accent-secondary); }
    .dot:nth-child(3) { animation-delay: 0.4s; background: var(--accent-tertiary); }
    
    @keyframes wave {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-12px); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); border-radius: 4px; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(180deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { opacity: 0.8; }
    
    /* Streamlit Input Overrides */
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: 16px !important;
        padding: 14px 20px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 20px rgba(0,212,255,0.15) !important;
    }
    
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        transition: all 0.3s ease !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(0,212,255,0.3) !important;
    }
    
    /* Hero Title */
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% 200%;
        animation: gradientFlow 4s ease infinite;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
    }
    
    @keyframes gradientFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }
    
    .hero-badge {
        padding: 6px 14px;
        background: rgba(16,185,129,0.1);
        color: var(--accent-success);
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(16,185,129,0.25);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .hero-badge::before {
        content: '';
        width: 6px;
        height: 6px;
        background: var(--accent-success);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    /* Section Headers */
    .section-header {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, var(--border-default) 0%, transparent 100%);
    }
    
    /* Trace Panel */
    .trace-item {
        padding: 14px 16px;
        margin: 8px 0;
        background: var(--bg-card);
        border-radius: 12px;
        border-left: 3px solid;
        transition: all 0.3s ease;
    }
    
    .trace-item:hover {
        transform: translateX(4px);
        background: var(--bg-card-hover);
    }
    
    .trace-item.active { border-color: var(--accent-success); }
    .trace-item.pending { border-color: var(--accent-warning); }
    .trace-item.inactive { border-color: var(--text-muted); }
    
    /* Empty State */
    .empty-state {
        color: var(--text-muted);
        font-style: italic;
        font-size: 0.9rem;
        padding: 20px;
        text-align: center;
        background: rgba(255,255,255,0.02);
        border-radius: 16px;
        border: 1px dashed var(--border-subtle);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 0;
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    
    .footer-badges {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 12px;
    }
    
    .footer-badge {
        padding: 6px 14px;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 100px;
        font-size: 0.75rem;
        color: var(--text-secondary);
    }
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# FIXED API CONFIGURATION - Removed trailing space and added rstrip
API_BASE_URL = os.getenv("BACKEND_URL", "https://hushh-backend-uc5w.onrender.com").strip().rstrip('/')
API_URL = f"{API_BASE_URL}/agents/run"

# --- DATA MANAGEMENT ---
def load_user_memory():
    """Load user memory from data/memory.json"""
    default_memory = {
        "user_id": "ankit_01",
        "name": "Ankit",
        "preferences": [],
        "avoid_keywords": [],
        "brand_affinity": [],
        "closet": []
    }
    
    try:
        if os.path.exists('data/memory.json'):
            with open('data/memory.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for user in data:
                        if user.get("user_id") == "ankit_01":
                            return user
                    return default_memory
                elif isinstance(data, dict):
                    return data
        return default_memory
    except Exception as e:
        st.error(f"Error loading memory: {e}")
        return default_memory

def save_user_memory(memory_data):
    """Save user memory to data/memory.json"""
    try:
        os.makedirs('data', exist_ok=True)
        existing_data = []
        
        if os.path.exists('data/memory.json'):
            with open('data/memory.json', 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except:
                    existing_data = []
        
        user_found = False
        for i, user in enumerate(existing_data):
            if user.get("user_id") == memory_data["user_id"]:
                existing_data[i] = memory_data
                user_found = True
                break
        
        if not user_found:
            existing_data.append(memory_data)
        
        with open('data/memory.json', 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving memory: {e}")

def call_ai_agent(user_message: str):
    """
    Call the FastAPI backend with the ORIGINAL user message.
    Let the AI handle extraction, not local regex.
    """
    try:
        payload = {
            "user_id": "ankit_01",
            "message": user_message  # Send original text, not a dictionary!
        }
        
        # DEBUG: Show what we're sending
        st.session_state.debug_info = f"Connecting to: {API_URL}"
        
        # INCREASED TIMEOUT for Render free tier cold start (60s)
        response = requests.post(
            API_URL,
            json=payload,
            timeout=60,  # Changed from 30 to 60
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        return {"error": "Backend is waking up (Render free tier). Please wait 30s and retry.", "agent": "error"}
    except requests.exceptions.ConnectionError as e:
        return {"error": f"Cannot reach backend. Is it running?", "agent": "error", "details": str(e)}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}", "agent": "error"}

# --- SESSION STATE ---
defaults = {
    "messages": [],
    "collected": {},  # Will be populated from backend response
    "current_question": None,
    "show_results": False,
    "products": [],
    "thinking": False,
    "avoid_keywords": [],  # Will sync with backend
    "last_request": None,
    "last_response": None,
    "debug_info": None
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Load memory on every rerun to get updates
USER_MEMORY = load_user_memory()
# Sync session state with saved memory
if "avoid_keywords" not in st.session_state or not st.session_state.avoid_keywords:
    st.session_state.avoid_keywords = USER_MEMORY.get("avoid_keywords", [])

# --- SIDEBAR ---
with st.sidebar:
    # Profile Section
    st.markdown(f"""
    <div style="text-align: center; padding: 24px 0;">
        <div class="profile-avatar">{USER_MEMORY['name'][0]}</div>
        <h2 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: white; font-family: 'Outfit', sans-serif;">{USER_MEMORY['name']}</h2>
        <p style="color: var(--text-muted); margin: 6px 0 0; font-size: 0.9rem;">@{USER_MEMORY['user_id']}</p>
        <div style="margin-top: 12px;">
            <span class="hero-badge">Premium Member</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CONNECTION TEST PANEL
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header" style="color: var(--accent-warning);">
        🔌 Connection Status
    </div>
    """, unsafe_allow_html=True)
    
    # Show current URL being used
    st.markdown(f"<div style='font-size: 0.75rem; color: var(--text-muted); word-break: break-all; padding: 8px; background: var(--bg-card); border-radius: 8px; margin-bottom: 12px;'>{API_URL}</div>", unsafe_allow_html=True)
    
    if st.button("⚡ Test Backend", use_container_width=True):
        with st.spinner("Checking connection..."):
            try:
                health_url = API_BASE_URL + "/health"
                r = requests.get(health_url, timeout=10)
                if r.status_code == 200:
                    st.success("✅ Backend is awake and ready!")
                else:
                    st.error(f"⚠️ Status: {r.status_code}")
            except Exception as e:
                st.error(f"❌ {str(e)[:40]}...")
    
    if st.session_state.get("debug_info"):
        st.markdown(f"<div style='font-size: 0.7rem; color: var(--text-muted); margin-top: 8px;'>{st.session_state.debug_info}</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # RECENTLY AVOIDED SECTION
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header" style="color: var(--accent-danger);">
        ⛔ Avoided Items
    </div>
    """, unsafe_allow_html=True)
    
    current_avoids = st.session_state.get("avoid_keywords", [])
    
    if current_avoids:
        st.markdown(f"<p style='color: var(--text-muted); font-size: 0.8rem; margin-bottom: 14px;'><strong>{len(current_avoids)}</strong> active filters</p>", unsafe_allow_html=True)
        for avoid in current_avoids:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"<div class='avoid-badge'><span>🚫</span>{avoid}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("✕", key=f"remove_{avoid}"):
                    st.session_state.avoid_keywords.remove(avoid)
                    USER_MEMORY["avoid_keywords"] = st.session_state.avoid_keywords
                    save_user_memory(USER_MEMORY)
                    st.rerun()
    else:
        st.markdown("""
        <div class="empty-state">
            No filters yet. Tell me things like<br/>
            <span style="color: var(--accent-primary);">"no chunky shoes"</span> or 
            <span style="color: var(--accent-primary);">"avoid neon colors"</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SESSION STATUS
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header" style="color: var(--accent-primary);">
        📊 Session Status
    </div>
    """, unsafe_allow_html=True)
    
    constraints = st.session_state.collected.get("constraints", {})
    
    # Category
    if constraints.get("category") or st.session_state.collected.get("category"):
        cat = constraints.get("category") or st.session_state.collected.get("category")
        st.markdown(f'<div class="status-pill status-filled"><b>Category:</b> {cat}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-pill status-pending"><b>Category</b> needed</div>', unsafe_allow_html=True)
    
    # Budget
    if constraints.get("budget_inr_max"):
        st.markdown(f'<div class="status-pill status-filled"><b>Budget:</b> ₹{constraints["budget_inr_max"]}</div>', unsafe_allow_html=True)
    elif st.session_state.collected.get("budget"):
        st.markdown(f'<div class="status-pill status-filled"><b>Budget:</b> ₹{st.session_state.collected["budget"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-pill status-pending"><b>Budget</b> needed</div>', unsafe_allow_html=True)
    
    # Size
    if constraints.get("size"):
        st.markdown(f'<div class="status-pill status-filled"><b>Size:</b> {constraints["size"]}</div>', unsafe_allow_html=True)
    elif st.session_state.collected.get("size"):
        st.markdown(f'<div class="status-pill status-filled"><b>Size:</b> {st.session_state.collected["size"]}</div>', unsafe_allow_html=True)
    
    # Style keywords
    if constraints.get("style_keywords"):
        styles = constraints["style_keywords"]
        if isinstance(styles, list):
            for style in styles:
                st.markdown(f'<div class="status-pill status-filled"><b>Style:</b> {style}</div>', unsafe_allow_html=True)
    
    # Avoid keywords from latest response
    if constraints.get("avoid_keywords"):
        avoids = constraints["avoid_keywords"]
        if isinstance(avoids, list) and avoids:
            st.markdown(f'<div class="status-pill" style="border-color: rgba(239,68,68,0.3); color: var(--accent-danger); background: rgba(239,68,68,0.08);"><b>Avoiding:</b> {", ".join(avoids)}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN INTERFACE ---
st.markdown("""
<div style="text-align: center; margin-bottom: 50px; padding-top: 20px;">
    <div class="hero-title">AI Shopping Concierge</div>
    <div class="hero-subtitle">
        <span>Powered by Groq AI</span>
        <span style="opacity: 0.3;">•</span>
        <span>Smart Memory</span>
        <span style="opacity: 0.3;">•</span>
        <span>Personalized Results</span>
        <span class="hero-badge">AI Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Messages
    for idx, msg in enumerate(st.session_state.messages):
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-agent"
        st.markdown(f'<div class="message-bubble {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        
        # Show clarifying questions if present
        if msg.get("questions"):
            st.markdown("""
            <div style='margin: 12px 0 20px 50px; padding: 18px; background: rgba(0,212,255,0.05); border-radius: 16px; border: 1px solid rgba(0,212,255,0.15);'>
                <div style='color: var(--accent-primary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px;'>Suggested Questions</div>
            """, unsafe_allow_html=True)
            for q in msg["questions"]:
                if st.button(f"💬 {q}", key=f"q_{idx}_{q[:20]}"):
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.session_state.thinking = True
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Show products
        if msg.get("products"):
            st.markdown("""
            <div class="results-header">
                <span style="font-size: 24px;">✨</span>
                <h3>Found Perfect Matches</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="product-grid">', unsafe_allow_html=True)
            for prod in msg["products"]:
                price = prod.get('price_inr', prod.get('price', 'N/A'))
                tags = prod.get("style_keywords", [])
                tags_html = "".join([f'<span class="tag">{kw}</span>' for kw in tags[:3]])
                match_score = prod.get('match_score', 0.95)
                brand = prod.get('brand', 'Premium Brand')
                
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-image">
                        👟
                        <div class="match-badge">{int(match_score*100)}% Match</div>
                    </div>
                    <div class="product-info">
                        <div class="product-brand">{brand}</div>
                        <div class="product-title">{prod.get('title', 'Product')}</div>
                        <div class="product-tags">{tags_html}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:16px;">
                            <div class="product-price">{price}</div>
                            <span style="color: var(--text-muted); font-size:0.8rem;">{prod.get('material', '')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show why recommended
            if msg.get("avoided"):
                st.markdown(f"""
                <div style="margin-top: 24px; padding: 16px 20px; background: rgba(239,68,68,0.08); border-radius: 14px; border: 1px solid rgba(239,68,68,0.2); display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 20px;">🚫</span>
                    <span style="color: var(--accent-danger); font-size: 0.9rem;">
                        Filtered out items with: <strong>{', '.join(msg['avoided'])}</strong>
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    # Thinking indicator
    if st.session_state.thinking:
        st.markdown("""
        <div class="thinking">
            <div class="thinking-text">AI Agent analyzing your request...</div>
            <div class="thinking-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    if not st.session_state.thinking:
        if prompt := st.chat_input("✨ Tell me what you're looking for (e.g., 'white sneakers under 2500, size 9, no chunky style')..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.thinking = True
            st.rerun()
    
    if st.session_state.show_results:
        if st.button("🔄 Start New Search", use_container_width=True):
            for key in defaults:
                st.session_state[key] = defaults[key]
            st.rerun()

with col2:
    st.markdown('<div class="glass-panel" style="height: 600px; overflow-y: auto;">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header" style="color: var(--accent-secondary);">
        🔍 System Trace
    </div>
    """, unsafe_allow_html=True)
    
    steps = [
        ("API Connected", True, API_BASE_URL[:25] + "...", "active"),
        ("AI Agent Active", True, "Groq LLaMA 3", "active"),
        ("Memory Synced", len(st.session_state.avoid_keywords) > 0, f"{len(st.session_state.avoid_keywords)} filters", "active" if st.session_state.avoid_keywords else "pending"),
        ("Last Query", st.session_state.last_request is not None, "Processed" if st.session_state.last_request else "Awaiting", "active" if st.session_state.last_request else "inactive"),
    ]
    
    for label, status, detail, state in steps:
        icon = "✓" if status else "○"
        st.markdown(f"""
        <div class="trace-item {state}">
            <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 4px;">{icon} {label}</div>
            <div style="color: var(--text-muted); font-size: 0.8rem;">{detail}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show raw constraints from backend for debugging
    if st.session_state.collected:
        st.markdown("<div style='margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border-subtle);'>", unsafe_allow_html=True)
        st.markdown("<div style='color: var(--text-muted); font-size: 0.7rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.1em;'>📋 Raw Constraints</div>", unsafe_allow_html=True)
        st.code(json.dumps(st.session_state.collected, indent=2), language="json")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- BACKEND PROCESSING ---
if st.session_state.thinking:
    try:
        # Get the last user message
        last_user_msg = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
        
        if last_user_msg:
            # Track the last request for UI feedback
            st.session_state.last_request = last_user_msg
            
            # Call the AI backend with ORIGINAL user message
            result = call_ai_agent(last_user_msg)
            st.session_state.last_response = result
            
            # Debug: log the full response
            print(f"[DEBUG] Backend response: {json.dumps(result, indent=2)}")
            
            if result:
                agent_type = result.get("agent", "")
                
                if "error" in result:
                    # IMPROVED ERROR MESSAGE for Render backend
                    error_msg = result['error']
                    if "waking up" in error_msg.lower() or "connection" in error_msg.lower():
                        error_msg += " Click 'Test Backend' in sidebar to wake it up."
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ {error_msg}"
                    })
                elif "fashion" in agent_type:
                    # Fashion Stylist Agent response
                    advice = result.get("results", [{}])[0].get("advice", "Here's my styling advice.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": advice,
                        "agent_type": "fashion"
                    })
                else:
                    # Shopping Agent response
                    understood = result.get("understood_request", {})
                    constraints = understood.get("constraints", {})
                    
                    # UPDATE SESSION STATE FROM BACKEND RESPONSE
                    st.session_state.collected = understood
                    
                    # Sync avoid keywords from backend response!
                    backend_avoids = constraints.get("avoid_keywords", [])
                    
                    # Also check for avoid keywords in style_keywords (sometimes LLM puts them there)
                    style_keywords = constraints.get("style_keywords", [])
                    
                    # Combine and deduplicate
                    all_avoids = list(set(backend_avoids))
                    
                    if all_avoids:
                        # Merge with existing, avoiding duplicates
                        existing = st.session_state.get("avoid_keywords", [])
                        combined = list(set(existing + all_avoids))
                        st.session_state.avoid_keywords = combined
                        USER_MEMORY["avoid_keywords"] = combined
                        save_user_memory(USER_MEMORY)
                        st.toast(f"🚫 Now avoiding: {', '.join(all_avoids)}", icon="✅")
                        print(f"[DEBUG] Updated avoid_keywords: {combined}")
                    
                    questions = result.get("clarifying_questions", [])
                    products = result.get("results", [])
                    
                    if questions and not products:
                        # Need more info
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "I need a bit more information to find the perfect match:",
                            "questions": questions
                        })
                    else:
                        # Show results
                        avoid_display = backend_avoids if backend_avoids else st.session_state.avoid_keywords
                        msg_content = f"Found {len(products)} curated matches for you."
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": msg_content,
                            "products": products,
                            "avoided": avoid_display,
                            "trace_id": result.get("trace_id", "")
                        })
                        
                        st.session_state.show_results = True
            else:
                # More descriptive error
                error_msg = "❌ Backend connection failed. "
                if "render.com" in API_URL:
                    error_msg += "Render backend may be sleeping. Click 'Test Backend' in sidebar to wake it up, then try again."
                else:
                    error_msg += "Check if backend is running on port 8000."
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "No message to process."
            })
            
    except Exception as e:
        st.error(f"Processing error: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    finally:
        st.session_state.thinking = False
        st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <p style="margin: 0;">Hushh.AI Power Agent MVP</p>
    <div class="footer-badges">
        <span class="footer-badge">🤖 Multi-Agent System</span>
        <span class="footer-badge">🧠 Smart Memory</span>
        <span class="footer-badge">⚡ MCP Tools</span>
        <span class="footer-badge">🎯 Personalized</span>
    </div>
</div>
""", unsafe_allow_html=True)