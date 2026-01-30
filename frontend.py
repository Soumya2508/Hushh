import streamlit as st
import requests
import json
import os
import time
import re
from datetime import datetime

# Configuration & Theming
st.set_page_config(
    page_title="Hushh | Personal Concierge",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apple Design System CSS
APPLE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    :root {
        --ios-blue: #007AFF;
        --ios-indigo: #5856D6;
        --ios-purple: #AF52DE;
        --ios-red: #FF3B30;
        --ios-orange: #FF9500;
        --ios-green: #34C759;
        --ios-gray: #8E8E93;
        --glass-bg: rgba(255, 255, 255, 0.75);
        --glass-border: rgba(255, 255, 255, 0.4);
    }
    
    * { font-family: 'Inter', -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    
    .glass-panel {
        background: var(--glass-bg);
        backdrop-filter: saturate(180%) blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.04);
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .profile-avatar {
        width: 80px; height: 80px; border-radius: 50%;
        background: linear-gradient(135deg, var(--ios-blue) 0%, var(--ios-purple) 100%);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 32px; font-weight: 600;
        margin: 0 auto 16px;
        box-shadow: 0 4px 20px rgba(0,122,255,0.3);
    }
    
    .chip-container { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .memory-chip {
        display: inline-flex; align-items: center; padding: 6px 14px;
        border-radius: 100px; font-size: 0.8rem; font-weight: 500;
        transition: transform 0.2s ease; cursor: default;
    }
    .memory-chip:hover { transform: scale(1.05); }
    .chip-pref { background: rgba(0,122,255,0.1); color: var(--ios-blue); border: 1px solid rgba(0,122,255,0.2); }
    .chip-avoid { background: rgba(255,59,48,0.08); color: var(--ios-red); border: 1px solid rgba(255,59,48,0.15); }
    .chip-brand { background: rgba(175,82,222,0.08); color: var(--ios-purple); border: 1px solid rgba(175,82,222,0.15); }
    .chip-product { background: rgba(52,199,89,0.1); color: var(--ios-green); border: 1px solid rgba(52,199,89,0.2); }
    
    .chat-container {
        background: white; border-radius: 24px; padding: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.04);
        min-height: 500px;
    }
    
    .message-bubble {
        max-width: 75%; padding: 14px 20px; margin: 8px 0;
        font-size: 0.95rem; line-height: 1.4;
        animation: messageSlide 0.3s ease;
    }
    .msg-user {
        background: var(--ios-blue); color: white;
        border-radius: 20px 20px 4px 20px; margin-left: auto;
        box-shadow: 0 4px 12px rgba(0,122,255,0.25);
    }
    .msg-agent {
        background: #F2F2F7; color: #1C1C1E;
        border-radius: 20px 20px 20px 4px; margin-right: auto;
    }
    
    @keyframes messageSlide {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .question-card {
        background: linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(88,86,214,0.05) 100%);
        border: 2px solid var(--ios-blue);
        border-radius: 20px; padding: 24px;
        margin: 16px 0;
        text-align: center;
    }
    
    .question-text {
        font-size: 1.1rem; font-weight: 600; color: #1C1C1E;
        margin-bottom: 16px;
    }
    
    .answer-btn {
        background: white; border: 1px solid var(--ios-blue); color: var(--ios-blue);
        padding: 10px 20px; border-radius: 20px; margin: 6px;
        cursor: pointer; transition: all 0.2s; font-weight: 500;
    }
    .answer-btn:hover { background: var(--ios-blue); color: white; transform: scale(1.05); }
    
    .product-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 20px; margin-top: 20px;
    }
    .product-card {
        background: white; border-radius: 20px; overflow: hidden;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease; position: relative;
    }
    .product-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.12); }
    .product-image-placeholder {
        width: 100%; height: 160px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        display: flex; align-items: center; justify-content: center; font-size: 48px;
    }
    .match-score {
        position: absolute; top: 12px; right: 12px;
        background: rgba(0,0,0,0.75); color: white;
        padding: 6px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; backdrop-filter: blur(10px);
    }
    .product-info { padding: 20px; }
    
    .status-bar { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
    .status-pill {
        padding: 8px 16px; border-radius: 100px; font-size: 0.85rem;
        background: rgba(120,120,128,0.08); border: 1px solid rgba(120,120,128,0.15);
        display: flex; align-items: center; gap: 8px;
    }
    .status-pill.filled { background: rgba(52,199,89,0.1); border-color: rgba(52,199,89,0.3); color: var(--ios-green); }
    .status-pill.pending { background: rgba(255,149,0,0.1); border-color: rgba(255,149,0,0.3); color: var(--ios-orange); }
    
    .sneaker-thumb {
        display: flex; align-items: center; padding: 8px;
        background: rgba(120,120,128,0.05); border-radius: 12px;
        margin-bottom: 8px; border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    .sneaker-thumb:hover { background: rgba(120,120,128,0.1); transform: translateX(4px); }
    .sneaker-img {
        width: 40px; height: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px; margin-right: 12px; display: flex; align-items: center; justify-content: center;
        color: white; font-size: 20px;
    }
    
    .bento-grid {
        display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 16px;
    }
    .stat-box {
        background: rgba(120,120,128,0.06); border-radius: 16px;
        padding: 16px; text-align: center; border: 1px solid rgba(120,120,128,0.1);
    }
    .stat-number { font-size: 1.8rem; font-weight: 700; color: var(--ios-blue); }
    .stat-label { font-size: 0.75rem; color: var(--ios-gray); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
</style>
"""

st.markdown(APPLE_CSS, unsafe_allow_html=True)

API_BASE_URL = os.getenv("BACKEND_URL", "https://hushh-backend-uc5w.onrender.com")
API_URL = f"{API_BASE_URL}/agents/run"

# CRITICAL FIELDS - Only these trigger cross-questioning
REQUIRED_FIELDS = ["size", "budget"]

CATALOG = [
  {
    "product_id": "snkr-001",
    "title": "Minimalist White Sneaker",
    "price_inr": 2200,
    "brand": "StepClean",
    "style_keywords": ["minimal", "white", "sleek"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-002",
    "title": "Chunky White Max",
    "price_inr": 2400,
    "brand": "UrbanCloud",
    "style_keywords": ["chunky", "white", "bold"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-003",
    "title": "Classic Court White",
    "price_inr": 1800,
    "brand": "Heritage",
    "style_keywords": ["minimal", "white", "classic"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-004",
    "title": "Urban Low Trainer",
    "price_inr": 2100,
    "brand": "StreetVibe",
    "style_keywords": ["minimal", "white", "urban"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-005",
    "title": "Pro Leather White",
    "price_inr": 2450,
    "brand": "Classics",
    "style_keywords": ["minimal", "white", "leather"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-006",
    "title": "Lite Walk Breathable",
    "price_inr": 1500,
    "brand": "SummerBreeze",
    "style_keywords": ["minimal", "white", "breathable"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-007",
    "title": "Essential Daily Sneaker",
    "price_inr": 1950,
    "brand": "StepClean",
    "style_keywords": ["minimal", "white", "everyday"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-008",
    "title": "Cloud Walk Soft",
    "price_inr": 2250,
    "brand": "UrbanCloud",
    "style_keywords": ["minimal", "white", "soft"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-009",
    "title": "Premium White High",
    "price_inr": 3200,
    "brand": "Heritage",
    "style_keywords": ["minimal", "white", "premium"],
    "category": "footwear",
    "size": "9"
  },
  {
    "product_id": "snkr-010",
    "title": "Retro White Sole",
    "price_inr": 2300,
    "brand": "Classics",
    "style_keywords": ["minimal", "white", "retro"],
    "category": "footwear",
    "size": "8"
  }
]

def load_user_profile():
    return {
        "user_id": "ankit_01", "name": "Ankit",
        "memory": {
            "preferences": ["organic cotton", "minimalist", "size 9"],
            "avoid_keywords": ["neon", "polyester", "slim-fit", "chunky"],
            "brand_affinity": ["StepClean", "Heritage", "SummerBreeze"]
        },
        "closet": [
            {"name": "Dark Indigo Jeans", "category": "bottom"},
            {"name": "White Oxford Shirt", "category": "top"}
        ],
        "stats": {"items_owned": 12, "searches_made": 48, "saved_items": 5}
    }

def extract_entities(text):
    """Extract critical attributes from user message"""
    entities = {}
    text_lower = text.lower()
    
    # Size extraction
    size_patterns = [r'\bsize\s*(\d+|s|m|l|xl)\b', r'\b(us|uk)\s*(\d+)\b', r'\b(\d{1,2})\b']
    for pattern in size_patterns:
        match = re.search(pattern, text_lower)
        if match:
            entities["size"] = match.group(1) if match.group(1) else match.group(2)
            break
    
    # Budget extraction
    budget_patterns = [
        r'(?:under|below|max|up to|₹|rs\.?|inr)?\s*(\d{3,5})',
        r'(\d{3,5})\s*(?:₹|rs\.?|inr)?',
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, text_lower)
        if match:
            val = int(match.group(1))
            if val > 500:  # Likely a price, not a size
                entities["budget"] = val
                break
    
    # Color extraction
    colors = ["white", "black", "blue", "red", "brown", "beige", "navy", "grey", "pink"]
    for color in colors:
        if color in text_lower:
            entities["color"] = color
            break
    
    # Occasion extraction
    occasions = ["casual", "formal", "party", "office", "sports", "running", "daily"]
    for occasion in occasions:
        if occasion in text_lower:
            entities["occasion"] = occasion
            break
            
    return entities

def get_missing_fields(collected):
    return [field for field in REQUIRED_FIELDS if field not in collected]

def generate_question(field):
    questions = {
        "size": "What size do you wear?",
        "budget": "What's your budget? (e.g., under 2000, 3000)",
        "color": "Any color preference?",
        "occasion": "What's the occasion?"
    }
    return questions.get(field, f"Please specify {field}")

def get_quick_options(field):
    options = {
        "size": ["6", "7", "8", "9", "10", "11"],
        "budget": ["Under ₹1500", "₹1500-₹2500", "₹2500-₹3500", "Any price"],
        "color": ["White", "Black", "Blue", "Beige"],
        "occasion": ["Casual", "Formal", "Sports"]
    }
    return options.get(field, [])

def filter_catalog(collected):
    """Local fallback filter if API fails"""
    filtered = CATALOG.copy()
    
    if "size" in collected:
        size = str(collected["size"])
        filtered = [p for p in filtered if str(p.get("size")) == size or p.get("size") == "9"]  # Default to 9 if no match
    
    if "budget" in collected:
        budget = collected["budget"]
        if isinstance(budget, str):
            budget = 10000 if "any" in budget.lower() else int(re.findall(r'\d+', budget)[0])
        filtered = [p for p in filtered if p.get("price_inr", 99999) <= budget]
    
    if "color" in collected:
        color = collected["color"].lower()
        filtered = [p for p in filtered if color in [k.lower() for k in p.get("style_keywords", [])]]
    
    return filtered

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "collected_attrs" not in st.session_state:
    st.session_state.collected_attrs = {}
if "current_question_field" not in st.session_state:
    st.session_state.current_question_field = None
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "products" not in st.session_state:
    st.session_state.products = []
if "api_error" not in st.session_state:
    st.session_state.api_error = None

# --- SIDEBAR ---
with st.sidebar:
    user = load_user_profile()
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 24px;">
        <div class="profile-avatar">{user['name'][0]}</div>
        <h2 style="margin: 8px 0 4px; font-weight: 600; color: #1C1C1E;">{user['name']}</h2>
        <p style="color: #8E8E93; font-size: 0.9rem;">@{user['user_id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status Panel
    st.markdown('<div class="glass-panel" style="padding: 16px;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; font-size:0.9rem; color:#8E8E93;'>REQUIRED INFO</h4>", unsafe_allow_html=True)
    
    for field in REQUIRED_FIELDS:
        status = "filled" if field in st.session_state.collected_attrs else "pending"
        icon = "✓" if status == "filled" else "○"
        value = st.session_state.collected_attrs.get(field, "Needed")
        if status == "filled":
            st.markdown(f'<div class="status-pill filled">{icon} <b>{field.title()}:</b> {value}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-pill pending">{icon} <b>{field.title()}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CATALOG PREVIEW - Shows all sneakers from your catalog.json
    with st.expander("👟 Available Sneakers (Catalog)", expanded=True):
        for sneaker in CATALOG[:6]:  # Show first 6
            st.markdown(f"""
            <div class="sneaker-thumb">
                <div class="sneaker-img">👟</div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 600; color: #1C1C1E; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {sneaker['title']}
                    </div>
                    <div style="color: #8E8E93; font-size: 0.75rem;">₹{sneaker['price_inr']} • {sneaker['brand']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        if len(CATALOG) > 6:
            st.caption(f"+{len(CATALOG)-6} more sneakers")
    
    # Permanent Memory
    with st.expander("🧠 Your Profile"):
        st.markdown('<div class="chip-container">', unsafe_allow_html=True)
        for pref in user['memory']['preferences']:
            st.markdown(f'<span class="memory-chip chip-pref">✓ {pref}</span>', unsafe_allow_html=True)
        for brand in user['memory']['brand_affinity']:
            st.markdown(f'<span class="memory-chip chip-brand">★ {brand}</span>', unsafe_allow_html=True)
        for avoid in user['memory']['avoid_keywords']:
            st.markdown(f'<span class="memory-chip chip-avoid">✕ {avoid}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN INTERFACE ---
st.markdown("""
<div style="text-align: center; margin-bottom: 32px;">
    <h1 style="font-weight: 700; letter-spacing: -0.02em; color: #1C1C1E; margin-bottom: 8px;">
        Personal Shopping Concierge
    </h1>
    <p style="color: #8E8E93; font-size: 1.1rem; margin: 0;">
        2 questions. Then instant results.
    </p>
</div>
""", unsafe_allow_html=True)

chat_col, trace_col = st.columns([2, 1])

with chat_col:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display conversation history
    for msg in st.session_state.messages:
        bubble_class = "msg-user" if msg["role"] == "user" else "msg-agent"
        st.markdown(f'<div class="message-bubble {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Show current understanding
    if st.session_state.collected_attrs and not st.session_state.show_results:
        attrs_text = " • ".join([f"{k}={v}" for k, v in st.session_state.collected_attrs.items()])
        st.markdown(f"""
        <div style="background: rgba(0,122,255,0.05); border-radius: 12px; padding: 10px 16px; 
                    margin: 12px 0; border-left: 3px solid var(--ios-blue); font-size: 0.85rem; color: #555;">
            <b>Understood:</b> {attrs_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Show SINGLE question if pending
    if st.session_state.current_question_field and not st.session_state.show_results:
        field = st.session_state.current_question_field
        question = generate_question(field)
        quick_opts = get_quick_options(field)
        
        st.markdown(f"""
        <div class="question-card">
            <div class="question-text">🤔 {question}</div>
            <div style="color: #8E8E93; font-size: 0.8rem; margin-bottom: 12px;">
                Question {REQUIRED_FIELDS.index(field) + 1} of {len(REQUIRED_FIELDS)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(min(len(quick_opts), 3))
        for idx, opt in enumerate(quick_opts):
            with cols[idx % 3]:
                if st.button(opt, key=f"opt_{field}_{opt}", use_container_width=True):
                    # Parse value
                    if field == "budget":
                        if "Under" in opt:
                            val = 1500
                        elif "Any" in opt:
                            val = 10000
                        else:
                            val = int(opt.replace("₹", "").split("-")[0])
                        st.session_state.collected_attrs[field] = val
                    else:
                        st.session_state.collected_attrs[field] = opt.lower()
                    
                    st.session_state.messages.append({"role": "user", "content": opt})
                    st.session_state.current_question_field = None
                    st.rerun()
    
    # Show RESULTS
    if st.session_state.show_results:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(52,199,89,0.1) 0%, rgba(52,199,89,0.05) 100%); 
                    border: 2px solid rgba(52,199,89,0.3); border-radius: 16px; padding: 16px; margin: 20px 0;">
            <h3 style="margin: 0; color: var(--ios-green); font-weight: 600;">✓ Found {len(st.session_state.products)} matches</h3>
            <p style="margin: 4px 0 0 0; color: #666; font-size: 0.85rem;">
                Size: {st.session_state.collected_attrs.get('size', 'Any')} • 
                Budget: Under ₹{st.session_state.collected_attrs.get('budget', 'Any')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.products:
            st.markdown('<div class="product-grid">', unsafe_allow_html=True)
            for item in st.session_state.products[:6]:
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-image-placeholder">👟</div>
                    <div class="match-score">{int(item.get('match_score', 0.95)*100)}% Match</div>
                    <div class="product-info">
                        <h4 style="margin: 0 0 4px; font-weight: 600; color: #1C1C1E; font-size: 0.95rem;">{item['title']}</h4>
                        <p style="margin: 0; color: var(--ios-blue); font-weight: 600; font-size: 1.1rem;">₹{item['price_inr']}</p>
                        <p style="margin: 4px 0 0; color: #8E8E93; font-size: 0.8rem;">{item['brand']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No exact matches in catalog. Try adjusting size or budget.")
        
        if st.button("🔄 New Search", use_container_width=True):
            st.session_state.collected_attrs = {}
            st.session_state.current_question_field = None
            st.session_state.show_results = False
            st.session_state.products = []
            st.session_state.messages = []
            st.rerun()
    
    # API Error display
    if st.session_state.api_error:
        st.error(f"API Error: {st.session_state.api_error}")
        st.info("Showing local catalog results instead...")
        if st.button("Use Local Data"):
            st.session_state.products = filter_catalog(st.session_state.collected_attrs)
            st.session_state.show_results = True
            st.session_state.api_error = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input
    if not st.session_state.show_results:
        if prompt := st.chat_input("I want white sneakers..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Extract entities
            extracted = extract_entities(prompt)
            st.session_state.collected_attrs.update(extracted)
            
            # Check missing
            missing = get_missing_fields(st.session_state.collected_attrs)
            
            if missing:
                st.session_state.current_question_field = missing[0]
            else:
                # All fields ready - fetch results
                with st.spinner("Finding sneakers..."):
                    try:
                        response = requests.post(API_URL, json={
                            "user_id": "ankit_01",
                            "message": prompt
                        }, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.products = data.get("results", [])
                            if not st.session_state.products:
                                # Fallback to local filter if API returns empty
                                st.session_state.products = filter_catalog(st.session_state.collected_attrs)
                        else:
                            st.session_state.api_error = f"Server error {response.status_code}"
                            st.session_state.products = filter_catalog(st.session_state.collected_attrs)
                            
                    except Exception as e:
                        st.session_state.api_error = str(e)
                        # CRITICAL: Use local catalog so user always sees sneakers
                        st.session_state.products = filter_catalog(st.session_state.collected_attrs)
                    
                    st.session_state.show_results = True
            
            st.rerun()

with trace_col:
    st.markdown('<div class="glass-panel" style="height: 600px; overflow-y: auto;">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-weight: 600;'>System Trace</h3>", unsafe_allow_html=True)
    
    if st.session_state.show_results:
        st.markdown(f"""
        <div style="padding: 12px; background: rgba(52,199,89,0.1); border-radius: 12px; margin-bottom: 12px;">
            <strong style="color: var(--ios-green);">● Search Complete</strong><br/>
            <span style="font-size: 0.8rem; color: #666;">
            Attributes collected: {len(st.session_state.collected_attrs)}<br/>
            Products found: {len(st.session_state.products)}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.collected_attrs:
        st.markdown("<h4 style='font-size: 0.9rem; color: #8E8E93; margin-top: 16px;'>COLLECTED ATTRIBUTES</h4>", unsafe_allow_html=True)
        for k, v in st.session_state.collected_attrs.items():
            st.markdown(f'<div class="sneaker-thumb"><span style="font-weight: 600; color: var(--ios-blue);">{k}:</span> {v}</div>', unsafe_allow_html=True)
    
    if st.session_state.api_error:
        st.markdown(f"""
        <div style="padding: 12px; background: rgba(255,59,48,0.1); border-radius: 12px; margin-top: 12px;">
            <strong style="color: var(--ios-red);">⚠ API Issue</strong><br/>
            <span style="font-size: 0.8rem;">{st.session_state.api_error}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-top: 40px; color: #8E8E93; font-size: 0.8rem;">
    <p>Showing {total} sneakers from catalog • Filtered by availability</p>
</div>
""".format(total=len(CATALOG)), unsafe_allow_html=True)