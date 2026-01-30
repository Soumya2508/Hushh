import streamlit as st
import requests
import json
import os
import time
import re
from datetime import datetime

# Dark Theme Configuration
st.set_page_config(
    page_title="Hushh | AI Concierge",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Cyberpunk CSS
DARK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #151520;
        --bg-card: #1a1a2e;
        --accent-cyan: #00d4ff;
        --accent-purple: #bb86fc;
        --accent-pink: #ff006e;
        --accent-green: #00f5d4;
        --accent-orange: #fb5607;
        --accent-red: #e63946;
        --text-primary: #ffffff;
        --text-secondary: #a0a0b0;
        --text-muted: #606070;
        --border: #2a2a3e;
    }
    
    * { 
        font-family: 'Inter', -apple-system, sans-serif; 
        -webkit-font-smoothing: antialiased;
        color: var(--text-primary);
    }
    
    .main { background: var(--bg-primary); }
    .main .block-container { padding-top: 2rem; max-width: 1400px; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Glass Cards */
    .glass-panel {
        background: linear-gradient(145deg, rgba(26,26,46,0.9) 0%, rgba(21,21,32,0.9) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    
    .glass-panel:hover {
        border-color: rgba(0,212,255,0.3);
        box-shadow: 0 8px 40px rgba(0,212,255,0.1);
    }
    
    /* Profile Section */
    .profile-avatar {
        width: 72px; height: 72px; border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
        display: flex; align-items: center; justify-content: center;
        color: #000; font-size: 28px; font-weight: 700;
        margin: 0 auto 16px;
        box-shadow: 0 0 30px rgba(0,212,255,0.4);
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    /* Avoided/Dislikes Section */
    .avoid-badge {
        display: inline-flex; align-items: center; padding: 6px 12px;
        background: rgba(230,57,70,0.15); 
        color: var(--accent-red);
        border: 1px solid rgba(230,57,70,0.3);
        border-radius: 8px; font-size: 0.8rem; font-weight: 500;
        margin: 4px; text-decoration: line-through;
        opacity: 0.8;
    }
    
    .avoid-badge:hover {
        opacity: 1;
        background: rgba(230,57,70,0.25);
    }
    
    /* Memory Chips */
    .memory-chip {
        display: inline-flex; align-items: center; padding: 6px 14px;
        background: rgba(0,212,255,0.1); 
        color: var(--accent-cyan);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 100px; font-size: 0.8rem; font-weight: 500;
        margin: 4px; transition: all 0.2s;
    }
    
    .memory-chip:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,212,255,0.2);
    }
    
    .chip-brand {
        background: rgba(187,134,252,0.1);
        color: var(--accent-purple);
        border-color: rgba(187,134,252,0.2);
    }
    
    /* Chat Interface */
    .chat-container {
        background: var(--bg-secondary);
        border-radius: 24px;
        border: 1px solid var(--border);
        min-height: 600px;
        padding: 24px;
        position: relative;
    }
    
    .message-bubble {
        max-width: 80%; padding: 16px 20px; margin: 12px 0;
        font-size: 0.95rem; line-height: 1.5;
        animation: slideIn 0.3s ease;
        position: relative;
    }
    
    .msg-user {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, #0099cc 100%);
        color: #000;
        border-radius: 20px 20px 4px 20px;
        margin-left: auto;
        font-weight: 500;
        box-shadow: 0 4px 20px rgba(0,212,255,0.3);
    }
    
    .msg-agent {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 20px 20px 20px 4px;
        margin-right: auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Question Card */
    .question-card {
        background: linear-gradient(145deg, rgba(0,212,255,0.05) 0%, rgba(187,134,252,0.05) 100%);
        border: 2px solid var(--accent-cyan);
        border-radius: 20px;
        padding: 28px;
        margin: 20px 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .question-card::before {
        content: '';
        position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px;
        background: linear-gradient(45deg, var(--accent-cyan), var(--accent-purple), var(--accent-cyan));
        border-radius: 20px;
        opacity: 0.3;
        z-index: -1;
    }
    
    .question-text {
        font-size: 1.2rem; font-weight: 600;
        margin-bottom: 20px;
        color: var(--text-primary);
    }
    
    .progress-indicator {
        color: var(--accent-cyan);
        font-size: 0.85rem;
        margin-bottom: 16px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Answer Buttons */
    .answer-btn {
        background: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-primary);
        padding: 12px 24px;
        border-radius: 12px;
        margin: 6px;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
        border: 1px solid transparent;
    }
    
    .answer-btn:hover {
        background: rgba(0,212,255,0.1);
        border-color: var(--accent-cyan);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,212,255,0.2);
    }
    
    /* Product Grid */
    .results-header {
        background: linear-gradient(90deg, rgba(0,245,212,0.1) 0%, transparent 100%);
        border-left: 4px solid var(--accent-green);
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .product-card {
        background: var(--bg-card);
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid var(--border);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0,212,255,0.3);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    
    .product-image {
        width: 100%; height: 200px;
        background: linear-gradient(135deg, #1e1e2d 0%, #2d2d44 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 64px;
        position: relative;
        border-bottom: 1px solid var(--border);
    }
    
    .match-badge {
        position: absolute; top: 12px; right: 12px;
        background: rgba(0,0,0,0.8);
        color: var(--accent-green);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem; font-weight: 700;
        border: 1px solid var(--accent-green);
        backdrop-filter: blur(10px);
    }
    
    .product-info { padding: 20px; }
    
    .product-title {
        font-size: 1.1rem; font-weight: 600;
        margin-bottom: 8px;
        color: var(--text-primary);
    }
    
    .product-meta {
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 12px;
    }
    
    .product-price {
        color: var(--accent-cyan);
        font-size: 1.3rem; font-weight: 700;
    }
    
    .product-brand {
        color: var(--accent-purple);
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .product-tags {
        display: flex; flex-wrap: wrap; gap: 6px;
        margin-top: 12px;
    }
    
    .tag {
        padding: 4px 10px;
        background: rgba(0,212,255,0.1);
        color: var(--accent-cyan);
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Status Pills */
    .status-pill {
        padding: 8px 16px;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 500;
        display: flex; align-items: center; gap: 8px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        margin-bottom: 8px;
    }
    
    .status-filled {
        border-color: var(--accent-green);
        color: var(--accent-green);
        background: rgba(0,245,212,0.1);
    }
    
    .status-pending {
        border-color: var(--accent-orange);
        color: var(--accent-orange);
        background: rgba(251,86,7,0.1);
    }
    
    /* Trace Panel */
    .trace-item {
        padding: 12px 16px;
        margin: 8px 0;
        background: var(--bg-card);
        border-radius: 12px;
        border-left: 3px solid var(--accent-cyan);
        font-family: 'SF Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    .trace-success { border-left-color: var(--accent-green); }
    .trace-wait { border-left-color: var(--accent-orange); }
    .trace-error { border-left-color: var(--accent-red); }
    
    /* Thinking Animation */
    .thinking {
        display: flex; align-items: center; gap: 12px;
        padding: 16px 20px;
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px solid var(--border);
        width: fit-content;
        margin: 12px 0;
    }
    
    .thinking-text {
        color: var(--accent-cyan);
        font-weight: 500;
    }
    
    .dot {
        width: 8px; height: 8px;
        background: var(--accent-cyan);
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .dot:nth-child(2) { animation-delay: -0.16s; }
    .dot:nth-child(3) { animation-delay: -0.32s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #444; }
    
    /* Input styling override */
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        color: white !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }
    
    div[data-testid="stSidebarUserContent"] {
        background: var(--bg-primary);
    }
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

API_BASE_URL = os.getenv("BACKEND_URL", "https://hushh-backend-uc5w.onrender.com")
API_URL = f"{API_BASE_URL}/agents/run"

# UPDATED CATALOG from catalog(2).json
CATALOG = [
    {"product_id": "snkr-001", "title": "Minimalist White Sneaker", "price_inr": 2200, "brand": "StepClean", 
     "style_keywords": ["minimal", "white", "sleek"], "category": "footwear", "sub_category": "sneakers", "size": "9", "material": "Faux Leather"},
    {"product_id": "snkr-002", "title": "Chunky White Max", "price_inr": 2400, "brand": "UrbanCloud", 
     "style_keywords": ["chunky", "white", "bold"], "category": "footwear", "sub_category": "sneakers", "size": "9", "material": "Mesh"},
    {"product_id": "top-013", "title": "Essential Navy Crewneck", "price_inr": 1200, "brand": "DailyBase", 
     "style_keywords": ["minimal", "navy", "casual"], "category": "apparel", "sub_category": "t-shirts", "size": "M", "material": "Cotton"},
    {"product_id": "bot-014", "title": "Relaxed Fit Cargo Pants", "price_inr": 2800, "brand": "StreetVibe", 
     "style_keywords": ["utility", "olive", "loose"], "category": "apparel", "sub_category": "pants", "size": "32", "material": "Cotton Twill"},
    {"product_id": "acc-015", "title": "Classic Leather Belt", "price_inr": 1500, "brand": "Heritage", 
     "style_keywords": ["formal", "brown", "brass"], "category": "accessories", "sub_category": "belts", "size": "Universal", "material": "Full Grain Leather"},
    {"product_id": "snkr-016", "title": "Midnight Runner", "price_inr": 3500, "brand": "UrbanCloud", 
     "style_keywords": ["sporty", "black", "breathable"], "category": "footwear", "sub_category": "running", "size": "10", "material": "Knit"},
    {"product_id": "top-017", "title": "Oxford Button-Down", "price_inr": 2100, "brand": "Classics", 
     "style_keywords": ["smart-casual", "light-blue", "structured"], "category": "apparel", "sub_category": "shirts", "size": "L", "material": "Oxford Cloth"},
    {"product_id": "bot-018", "title": "Dark Indigo Slim Jeans", "price_inr": 2600, "brand": "Heritage", 
     "style_keywords": ["classic", "denim", "indigo"], "category": "apparel", "sub_category": "jeans", "size": "34", "material": "Denim"},
    {"product_id": "acc-019", "title": "Aviator Sunglasses", "price_inr": 1850, "brand": "SummerBreeze", 
     "style_keywords": ["sleek", "gold", "summer"], "category": "accessories", "sub_category": "eyewear", "size": "M", "material": "Metal"},
    {"product_id": "snkr-020", "title": "Eco-Canvas Slip-on", "price_inr": 1600, "brand": "SummerBreeze", 
     "style_keywords": ["eco-friendly", "beige", "simple"], "category": "footwear", "sub_category": "casual", "size": "8", "material": "Hemp Canvas"}
]

# DYNAMIC REQUIRED FIELDS - Only critical for filtering
REQUIRED_FIELDS = ["category", "budget"]  # Category (what they want) and budget (price limit)

def load_user_memory():
    """Load user preferences, avoid keywords, etc."""
    return {
        "user_id": "ankit_01",
        "name": "Ankit",
        "preferences": ["minimalist", "organic cotton", "size 9", "neutral colors"],
        "avoid_keywords": ["chunky", "neon", "flashy", "polyester", "slim-fit"],  # These are important!
        "brand_affinity": ["StepClean", "Heritage", "SummerBreeze"],
        "closet": ["Dark Indigo Jeans", "White Oxford Shirt", "Beige Chinos"]
    }

def extract_entities(text):
    """Smart entity extraction from user query"""
    entities = {}
    text_lower = text.lower()
    
    # Category detection (crucial)
    categories = {
        "footwear": ["shoes", "sneakers", "footwear", "kicks", "runners", "boots"],
        "apparel": ["shirt", "t-shirt", "pants", "jeans", "clothes", "clothing", "top", "bottom"],
        "accessories": ["belt", "sunglasses", "watch", "accessories", "bag", "wallet"]
    }
    for cat, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            entities["category"] = cat
            # Detect subcategory
            if cat == "footwear":
                if "sneaker" in text_lower or "shoe" in text_lower:
                    entities["sub_category"] = "sneakers"
                elif "running" in text_lower:
                    entities["sub_category"] = "running"
            break
    
    # Budget extraction
    budget_patterns = [
        r'(?:under|below|max|up to|less than)\s*(?:₹|rs\.?|inr)?\s*(\d{3,5})',
        r'(?:₹|rs\.?|inr)\s*(\d{3,5})',
        r'(\d{3,5})\s*(?:₹|rs\.?|inr)',
        r'budget\s*(?:of\s*)?(?:₹|rs\.?|inr)?\s*(\d{3,5})'
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, text_lower)
        if match:
            entities["budget"] = int(match.group(1))
            break
    
    # Size extraction
    size_match = re.search(r'\b(?:size\s*)?(\d+|s|m|l|xl)\b', text_lower)
    if size_match:
        entities["size"] = size_match.group(1).upper() if size_match.group(1) in ['s','m','l','xl'] else size_match.group(1)
    
    # Color extraction
    colors = ["white", "black", "blue", "navy", "red", "brown", "beige", "olive", "indigo", "gold"]
    for color in colors:
        if color in text_lower:
            entities["color"] = color
            break
    
    return entities

def get_missing_fields(collected):
    """Check what's still needed"""
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in collected:
            missing.append(field)
    return missing

def generate_question(field):
    """Generate contextual question"""
    questions = {
        "category": "What are you looking for? (sneakers, shirt, pants, accessories...)",
        "budget": "What's your budget range?",
        "size": "What size do you wear?",
        "color": "Any preferred color?"
    }
    return questions.get(field, f"Please specify {field}")

def get_quick_options(field):
    """Contextual quick replies"""
    options = {
        "category": ["Sneakers/Shoes", "Shirts/Tops", "Pants/Jeans", "Accessories"],
        "budget": ["Under ₹1500", "₹1500-₹2500", "₹2500-₹3500", "No limit"],
        "size": ["7", "8", "9", "10", "M", "L", "XL"],
        "color": ["White/Beige", "Black/Navy", "Brown/Olive", "Any color"]
    }
    return options.get(field, [])

def parse_quick_option(field, option):
    """Parse button text to actual value"""
    if field == "budget":
        if "Under" in option:
            return 1500
        elif "No limit" in option:
            return 100000
        else:
            nums = re.findall(r'\d+', option)
            return int(nums[-1]) if nums else 5000
    elif field == "category":
        mapping = {
            "Sneakers/Shoes": "footwear",
            "Shirts/Tops": "apparel", 
            "Pants/Jeans": "apparel",
            "Accessories": "accessories"
        }
        return mapping.get(option, "footwear")
    return option.lower().split("/")[0]

def filter_products(collected, avoid_keywords):
    """Smart filtering with scoring"""
    results = []
    
    for product in CATALOG:
        score = 0
        matches = []
        
        # Category match (required)
        if collected.get("category") and product.get("category") == collected["category"]:
            score += 40
            matches.append("category")
            
            # Subcategory bonus
            if collected.get("sub_category") and product.get("sub_category") == collected["sub_category"]:
                score += 20
        
        # Budget match (required)
        if "budget" in collected:
            if product["price_inr"] <= collected["budget"]:
                score += 30
                matches.append("budget")
            else:
                continue  # Over budget - skip
        
        # Size match
        if collected.get("size"):
            if str(product.get("size")) == str(collected["size"]):
                score += 15
                matches.append("size")
        
        # Color match
        if collected.get("color"):
            if any(collected["color"] in kw for kw in product.get("style_keywords", [])):
                score += 10
                matches.append("color")
        
        # Check avoided keywords (penalty)
        has_avoided = False
        for avoid in avoid_keywords:
            if any(avoid in kw for kw in product.get("style_keywords", [])):
                has_avoided = True
                score -= 50  # Heavy penalty
        
        if not has_avoided and score > 0:
            result = product.copy()
            result["match_score"] = min(score / 100, 0.99)
            result["match_reasons"] = matches
            results.append(result)
    
    # Sort by match score
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:6]  # Top 6

# --- SESSION STATE ---
defaults = {
    "messages": [],
    "collected": {},
    "current_question": None,
    "show_results": False,
    "products": [],
    "thinking": False,
    "api_error": None
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- SIDEBAR ---
with st.sidebar:
    user = load_user_memory()
    
    # Profile
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <div class="profile-avatar">{user['name'][0]}</div>
        <h2 style="margin: 0; font-size: 1.3rem; font-weight: 600;">{user['name']}</h2>
        <p style="color: var(--text-muted); margin: 4px 0 0; font-size: 0.9rem;">@{user['user_id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AVOIDED KEYWORDS SECTION (Prominent)
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("""
    <h4 style="margin-top:0; color: var(--accent-red); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.1em;">
        ⛔ Auto-Filtered Out
    </h4>
    <p style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 12px;">
        Products with these tags are hidden
    </p>
    """, unsafe_allow_html=True)
    
    for avoid in user["avoid_keywords"]:
        st.markdown(f'<span class="avoid-badge">✕ {avoid}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current Session Status
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color: var(--accent-cyan); font-size: 0.9rem;'>SESSION STATUS</h4>", unsafe_allow_html=True)
    
    for field in REQUIRED_FIELDS:
        if field in st.session_state.collected:
            val = st.session_state.collected[field]
            display = f"₹{val}" if field == "budget" else val
            st.markdown(f"""
            <div class="status-pill status-filled">
                <span>✓</span> <b>{field.title()}:</b> {display}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-pill status-pending">
                <span>○</span> <b>{field.title()}</b> (needed)
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # User Preferences
    with st.expander("💎 Your Preferences"):
        for pref in user["preferences"]:
            st.markdown(f'<span class="memory-chip">✓ {pref}</span>', unsafe_allow_html=True)
        for brand in user["brand_affinity"]:
            st.markdown(f'<span class="memory-chip chip-brand">★ {brand}</span>', unsafe_allow_html=True)

# --- MAIN CHAT AREA ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 style="font-weight: 700; font-size: 2rem; margin-bottom: 8px; background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        AI Shopping Concierge
    </h1>
    <p style="color: var(--text-muted); font-size: 1rem; margin: 0;">
        I filter out what you dislike. I ask only what's necessary.
    </p>
</div>
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([3, 1])

with col1:
    # Chat Container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Messages
    for msg in st.session_state.messages:
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-agent"
        st.markdown(f'<div class="message-bubble {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        
        # If assistant message has products, show them
        if msg.get("products"):
            st.markdown('<div class="results-header"><h3 style="margin:0; color: var(--accent-green);">✓ Found these for you</h3></div>', unsafe_allow_html=True)
            st.markdown('<div class="product-grid">', unsafe_allow_html=True)
            for prod in msg["products"]:
                tags_html = "".join([f'<span class="tag">{kw}</span>' for kw in prod.get("style_keywords", [])[:3]])
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-image">
                        👟
                        <div class="match-badge">{int(prod['match_score']*100)}% MATCH</div>
                    </div>
                    <div class="product-info">
                        <div class="product-brand">{prod['brand']}</div>
                        <div class="product-title">{prod['title']}</div>
                        <div class="product-tags">{tags_html}</div>
                        <div class="product-meta">
                            <span class="product-price">₹{prod['price_inr']}</span>
                            <span style="color: var(--text-muted); font-size: 0.8rem;">{prod.get('material', '')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Thinking indicator
    if st.session_state.thinking:
        st.markdown("""
        <div class="thinking">
            <span class="thinking-text">Curating your selection</span>
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Question Card (Single Question)
    if st.session_state.current_question and not st.session_state.show_results:
        field = st.session_state.current_question
        q_text = generate_question(field)
        options = get_quick_options(field)
        
        progress = len([f for f in REQUIRED_FIELDS if f in st.session_state.collected])
        total = len(REQUIRED_FIELDS)
        
        st.markdown(f"""
        <div class="question-card">
            <div class="progress-indicator">Gathering Context • {progress}/{total}</div>
            <div class="question-text">{q_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(min(len(options), 2))
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if st.button(opt, key=f"btn_{field}_{i}", use_container_width=True):
                    # Parse and store
                    val = parse_quick_option(field, opt)
                    st.session_state.collected[field] = val
                    st.session_state.messages.append({"role": "user", "content": opt})
                    
                    # Check if more questions needed
                    missing = get_missing_fields(st.session_state.collected)
                    if missing:
                        st.session_state.current_question = missing[0]
                    else:
                        st.session_state.current_question = None
                        st.session_state.thinking = True
                    
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input
    if not st.session_state.show_results and not st.session_state.current_question:
        placeholder = "I want white sneakers under 2500..." if not st.session_state.collected else "Tell me more..."
        if prompt := st.chat_input(placeholder):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Extract
            extracted = extract_entities(prompt)
            st.session_state.collected.update(extracted)
            
            # Check missing
            missing = get_missing_fields(st.session_state.collected)
            if missing:
                st.session_state.current_question = missing[0]
            else:
                st.session_state.thinking = True
            
            st.rerun()
    
    # Reset button if showing results
    if st.session_state.show_results:
        if st.button("🔁 Start New Search", use_container_width=True):
            for key in defaults:
                st.session_state[key] = defaults[key]
            st.rerun()

with col2:
    # System Trace / Debug
    st.markdown('<div class="glass-panel" style="height: 600px; overflow-y: auto;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color: var(--accent-cyan);'>SYSTEM TRACE</h4>", unsafe_allow_html=True)
    
    # Show current state
    steps = [
        ("Intent Parsed", "category" in st.session_state.collected, "Extracted category"),
        ("Budget Set", "budget" in st.session_state.collected, "Price filter active"),
        ("Ready", not get_missing_fields(st.session_state.collected), "All requirements met"),
        ("Filtered", st.session_state.show_results, f"{len(st.session_state.products)} items matched")
    ]
    
    for label, status, detail in steps:
        css = "trace-success" if status else "trace-wait"
        icon = "✓" if status else "○"
        st.markdown(f"""
        <div class="trace-item {css}">
            <strong style="color: {'var(--accent-green)' if status else 'var(--text-secondary)'};">{icon} {label}</strong><br/>
            <span style="font-size: 0.8rem; opacity: 0.7;">{detail}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Show avoided filtering in action
    if st.session_state.show_results and st.session_state.products:
        st.markdown("<h5 style='color: var(--accent-red); margin-top: 20px;'>FILTERED OUT</h5>", unsafe_allow_html=True)
        avoided = load_user_memory()["avoid_keywords"]
        st.markdown(f"""
        <p style="font-size: 0.8rem; color: var(--text-muted);">
            Items containing: {', '.join(avoided)}<br/>
            were automatically excluded from results.
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESSING LOGIC ---
if st.session_state.thinking:
    try:
        time.sleep(0.8)  # UX delay
        
        user_memory = load_user_memory()
        
        # Try API first
        try:
            resp = requests.post(API_URL, json={
                "user_id": "ankit_01",
                "message": str(st.session_state.collected),
                "context": st.session_state.collected
            }, timeout=8)
            
            if resp.status_code == 200:
                data = resp.json()
                products = data.get("results", [])
            else:
                products = []
        except:
            products = []
        
        # Fallback to local smart filter
        if not products:
            products = filter_products(
                st.session_state.collected, 
                user_memory["avoid_keywords"]
            )
        
        # Store results as assistant message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Found {len(products)} items matching your criteria. Filtered out products with: {', '.join(user_memory['avoid_keywords'][:3])}...",
            "products": products
        })
        
        st.session_state.products = products
        st.session_state.thinking = False
        st.session_state.show_results = True
        
    except Exception as e:
        st.session_state.thinking = False
        st.error(f"Error: {e}")
    
    st.rerun()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 0.8rem;">
    <p>Smart filtering active • Avoided keywords honored • Minimal questioning</p>
</div>
""", unsafe_allow_html=True)