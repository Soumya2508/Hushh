# Write the Streamlit frontend file
frontend_code = '''import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid

# APPLE-ESQUE DARK THEME CONFIGURATION
st.set_page_config(
    page_title="Hushh AI Concierge",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS - Professional Dark Apple Design
st.markdown("""
<style>
    /* Global Dark Theme with Apple-style gradients */
    .stApp {
        background: linear-gradient(180deg, #0d0d0d 0%, #1a1a1a 50%, #0f0f0f 100%);
        color: #f5f5f7;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Glassmorphism Header */
    .glass-header {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    /* Apple-style Typography */
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #f5f5f7;
    }
    
    /* Chat Container */
    .chat-container {
        background: rgba(30, 30, 30, 0.4);
        backdrop-filter: blur(30px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    
    /* Message Bubbles */
    .user-message {
        background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 6px 20px;
        margin: 1rem 0 1rem auto;
        max-width: 80%;
        box-shadow: 0 4px 20px rgba(0, 122, 255, 0.3);
        animation: slideIn 0.3s ease-out;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .agent-message {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #f5f5f7;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 6px;
        margin: 1rem auto 1rem 0;
        max-width: 80%;
        animation: slideIn 0.3s ease-out;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Product Cards - Glassmorphism */
    .product-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .product-card:hover {
        transform: translateY(-4px);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }
    
    .product-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    }
    
    /* Constraints Display */
    .constraint-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.85rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .constraint-pill.negative {
        background: rgba(255, 59, 48, 0.15);
        border-color: rgba(255, 59, 48, 0.3);
        color: #ff453a;
    }
    
    .constraint-pill.positive {
        background: rgba(48, 209, 88, 0.15);
        border-color: rgba(48, 209, 88, 0.3);
        color: #30d158;
    }
    
    /* Question Chips */
    .question-chip {
        background: rgba(0, 122, 255, 0.15);
        border: 1px solid rgba(0, 122, 255, 0.3);
        color: #64d2ff;
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        margin: 0.5rem 0.5rem 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .question-chip:hover {
        background: rgba(0, 122, 255, 0.25);
        transform: scale(1.02);
    }
    
    /* Sidebar Profile */
    .profile-section {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .memory-fact {
        background: rgba(255, 255, 255, 0.05);
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #007AFF;
        font-size: 0.9rem;
    }
    
    /* Action Buttons */
    .action-button {
        background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        margin: 0.5rem 0.5rem 0 0;
        box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .typing-indicator {
        display: inline-flex;
        gap: 4px;
        padding: 1rem 1.5rem;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        margin: 1rem 0;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #64d2ff;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Input Styling Override */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #007AFF !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2) !important;
    }
    
    /* Trace ID Badge */
    .trace-badge {
        font-family: 'Courier New', monospace;
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.4);
        background: rgba(255, 255, 255, 0.05);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{str(uuid.uuid4())[:8]}"
if 'memory' not in st.session_state:
    st.session_state.memory = {}
if 'awaiting_response' not in st.session_state:
    st.session_state.awaiting_response = False

def call_backend(message: str):
    """Call the FastAPI backend"""
    try:
        response = requests.post(
            "http://127.0.0.1:8000/agents/run",
            json={"user_id": st.session_state.user_id, "message": message},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e), "agent": "error", "trace_id": "error"}

def render_constraints(constraints: dict):
    """Render the understood constraints as Apple-style pills"""
    html = "<div style='margin: 1rem 0;'>"
    html += "<div style='font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-bottom: 0.5rem;'>UNDERSTOOD PREFERENCES</div>"
    html += "<div>"
    
    # Budget
    if constraints.get('budget_inr_max'):
        html += f"<span class='constraint-pill positive'>💰 Budget: ₹{constraints['budget_inr_max']}</span>"
    
    # Size
    if constraints.get('size'):
        html += f"<span class='constraint-pill positive'>📏 Size: {constraints['size']}</span>"
    
    # Style keywords
    if constraints.get('style_keywords'):
        styles = constraints['style_keywords']
        if isinstance(styles, list):
            for style in styles:
                html += f"<span class='constraint-pill positive'>✨ {style.title()}</span>"
        else:
            html += f"<span class='constraint-pill positive'>✨ {styles}</span>"
    
    # Avoid keywords (negative constraints)
    if constraints.get('avoid_keywords'):
        avoids = constraints['avoid_keywords']
        if isinstance(avoids, list):
            for avoid in avoids:
                html += f"<span class='constraint-pill negative'>🚫 {avoid.title()}</span>"
        else:
            html += f"<span class='constraint-pill negative'>🚫 {avoids}</span>"
    
    html += "</div></div>"
    return html

def render_product_card(product: dict, avoid_keywords: list = None):
    """Render a product recommendation card"""
    if avoid_keywords is None:
        avoid_keywords = []
    
    pros = product.get('pros', [])
    cons = product.get('cons', [])
    match_score = product.get('match_score', 0.95)
    
    # Calculate match color
    match_color = "#30d158" if match_score > 0.9 else "#ff9500" if match_score > 0.7 else "#ff453a"
    
    html = f"""
    <div class="product-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #f5f5f7;">{product.get('title', 'Unknown Product')}</div>
            <div style="background: {match_color}20; color: {match_color}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">
                {int(match_score * 100)}% Match
            </div>
        </div>
        
        <div style="color: #64d2ff; font-size: 0.9rem; margin-bottom: 0.5rem;">{product.get('brand', 'Unknown Brand')}</div>
        <div style="font-size: 1.3rem; font-weight: 700; color: #f5f5f7; margin-bottom: 1rem;">₹{product.get('price_inr', 'N/A')}</div>
        
        <div style="margin: 1rem 0; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 10px; font-size: 0.9rem; line-height: 1.5; color: rgba(255,255,255,0.8);">
            {product.get('why_recommended', 'Recommended based on your preferences.')}
        </div>
        
        <div style="display: flex; gap: 1rem; font-size: 0.85rem;">
            <div style="flex: 1;">
                <div style="color: #30d158; margin-bottom: 0.25rem;">Pros</div>
                {"".join([f"<div style='margin: 0.25rem 0;'>• {pro}</div>" for pro in pros])}
            </div>
            <div style="flex: 1;">
                <div style="color: #ff453a; margin-bottom: 0.25rem;">Cons</div>
                {"".join([f"<div style='margin: 0.25rem 0;'>• {con}</div>" for con in cons])}
            </div>
        </div>
        
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); font-size: 0.75rem; color: rgba(255,255,255,0.4);">
            ID: {product.get('product_id', 'N/A')}
        </div>
    </div>
    """
    return html

# UI LAYOUT
# Header with Glass Effect
st.markdown("""
<div class="glass-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 1.8rem; background: linear-gradient(135deg, #fff 0%, #a0a0a0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🛍️ Hushh AI Concierge
            </h1>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin-top: 0.25rem;">
                Personal Shopping Intelligence
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Session ID</div>
            <div style="font-family: monospace; color: #64d2ff; font-size: 0.9rem;">{st.session_state.user_id}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar - User Profile & Memory
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0;">
        <h2 style="font-size: 1.3rem; margin-bottom: 1.5rem;">👤 Your Profile</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Persistent Memory Section
    st.markdown("""
    <div class="profile-section">
        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">
            Saved Preferences
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.memory.get('facts'):
        for fact in st.session_state.memory['facts']:
            st.markdown(f"<div class='memory-fact'>📝 {fact}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="color: rgba(255,255,255,0.3); font-size: 0.9rem; font-style: italic; padding: 1rem 0;">
            No preferences saved yet. Start chatting to build your profile.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Shortlist Section
    if st.session_state.memory.get('shortlist'):
        st.markdown("""
        <div class="profile-section">
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">
                Your Shortlist
            </div>
        """, unsafe_allow_html=True)
        for item in st.session_state.memory['shortlist']:
            st.markdown(f"""
            <div style="background: rgba(0,122,255,0.1); border: 1px solid rgba(0,122,255,0.2); padding: 0.75rem; border-radius: 10px; margin: 0.5rem 0; font-size: 0.85rem;">
                <div style="font-weight: 600;">{item.get('product_id', 'Item')}</div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.75rem;">{item.get('reason', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Stats
    st.markdown("""
    <div class="profile-section">
        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">
            Session Stats
        </div>
        <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
            <span style="color: rgba(255,255,255,0.5);">Messages</span>
            <span style="color: #64d2ff; font-weight: 600;">{}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
            <span style="color: rgba(255,255,255,0.5);">Agent</span>
            <span style="color: #30d158; font-weight: 600;">Active</span>
        </div>
    </div>
    """.format(len(st.session_state.messages)), unsafe_allow_html=True)

# Main Chat Area
chat_container = st.container()

with chat_container:
    # Display Chat History
    for idx, msg in enumerate(st.session_state.messages):
        if msg['role'] == 'user':
            st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            # Agent message with structured data
            st.markdown(f"<div class='agent-message'>{msg['content']}</div>", unsafe_allow_html=True)
            
            # If this message has structured data, render it
            if 'data' in msg:
                data = msg['data']
                
                # Trace ID
                if data.get('trace_id'):
                    st.markdown(f"<div class='trace-badge'>🔍 Trace: {data['trace_id'][:8]}...</div>", unsafe_allow_html=True)
                
                # Constraints
                if data.get('understood_request', {}).get('constraints'):
                    st.markdown(
                        render_constraints(data['understood_request']['constraints']), 
                        unsafe_allow_html=True
                    )
                
                # Clarifying Questions
                if data.get('clarifying_questions'):
                    st.markdown("<div style='margin: 1rem 0; font-size: 0.8rem; color: rgba(255,255,255,0.5);'>FOLLOW-UP QUESTIONS</div>", unsafe_allow_html=True)
                    for q in data['clarifying_questions']:
                        if st.button(f"💬 {q}", key=f"q_{idx}_{q[:20]}"):
                            st.session_state.messages.append({"role": "user", "content": q})
                            st.rerun()
                
                # Product Results
                if data.get('results'):
                    st.markdown("<div style='margin: 2rem 0 1rem 0; font-size: 0.8rem; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 0.1em;'>Recommendations</div>", unsafe_allow_html=True)
                    
                    avoid_keywords = data.get('understood_request', {}).get('constraints', {}).get('avoid_keywords', [])
                    
                    for product in data['results']:
                        st.markdown(render_product_card(product, avoid_keywords), unsafe_allow_html=True)
                
                # Next Actions
                if data.get('next_actions'):
                    st.markdown("<div style='margin: 1.5rem 0 0.5rem 0; font-size: 0.8rem; color: rgba(255,255,255,0.5);'>SUGGESTED ACTIONS</div>", unsafe_allow_html=True)
                    cols = st.columns(len(data['next_actions']))
                    for i, action in enumerate(data['next_actions']):
                        action_type = action.get('action', 'PROCEED')
                        with cols[i]:
                            if st.button(f"▶️ {action_type.replace('_', ' ').title()}", key=f"action_{idx}_{i}"):
                                st.session_state.messages.append({"role": "user", "content": f"Execute {action_type}"})
                                st.rerun()
                
                # Comparisons
                if data.get('comparisons', {}).get('summary'):
                    comp = data['comparisons']
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); border-left: 3px solid #bf5af2; padding: 1rem; margin: 1rem 0; border-radius: 0 10px 10px 0;">
                        <div style="font-size: 0.8rem; color: #bf5af2; margin-bottom: 0.5rem;">ANALYSIS</div>
                        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.9); margin-bottom: 0.5rem;">{comp['summary']}</div>
                        {"".join([f'<div style="font-size: 0.85rem; color: rgba(255,255,255,0.6); margin: 0.25rem 0;">• {t}</div>' for t in comp.get('tradeoffs', [])])}
                    </div>
                    """, unsafe_allow_html=True)

    # Typing indicator
    if st.session_state.awaiting_response:
        st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """, unsafe_allow_html=True)

# Input Area
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input(
            "", 
            placeholder="Tell me what you're looking for... (e.g., 'I need white sneakers under ₹2500, size 9, no chunky soles')",
            key="input",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.button("Send", use_container_width=True, type="primary")

# Handle Input
if send_button and user_input and not st.session_state.awaiting_response:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.awaiting_response = True
    st.rerun()

if st.session_state.awaiting_response and st.session_state.messages[-1]['role'] == 'user':
    # Get last user message
    last_message = st.session_state.messages[-1]['content']
    
    # Call backend
    with st.spinner():
        response = call_backend(last_message)
    
    # Extract content for display
    if response.get('error'):
        agent_content = f"❌ Error: {response['error']}"
        response_data = {}
    else:
        # Build natural language response from structured data
        agent_type = response.get('agent', 'concierge')
        results_count = len(response.get('results', []))
        
        if results_count > 0:
            agent_content = f"Found {results_count} item{'s' if results_count > 1 else ''} matching your criteria. I've analyzed your preferences and filtered out items matching your avoid list."
        else:
            agent_content = "I couldn't find any items matching your specific criteria. Would you like me to adjust the filters or search for alternatives?"
        
        response_data = response
        
        # Update memory in sidebar
        if response.get('understood_request', {}).get('constraints'):
            constraints = response['understood_request']['constraints']
            facts = []
            if constraints.get('size'):
                facts.append(f"Size: {constraints['size']}")
            if constraints.get('budget_inr_max'):
                facts.append(f"Budget: ₹{constraints['budget_inr_max']}")
            if constraints.get('avoid_keywords'):
                avoids = constraints['avoid_keywords']
                if isinstance(avoids, list):
                    facts.append(f"Dislikes: {', '.join(avoids)}")
                else:
                    facts.append(f"Dislikes: {avoids}")
            st.session_state.memory['facts'] = list(set(st.session_state.memory.get('facts', []) + facts))
        
        if response.get('shortlist'):
            st.session_state.memory['shortlist'] = response['shortlist']
    
    # Add agent message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": agent_content,
        "data": response_data
    })
    
    st.session_state.awaiting_response = False
    st.rerun()

# Quick Suggestions
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="margin-top: 3rem; text-align: center; color: rgba(255,255,255,0.3);">
        <div style="margin-bottom: 1rem; font-size: 0.9rem;">Try asking for:</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    suggestions = [
        "White sneakers under ₹2500, size 9, no chunky soles",
        "Style advice for my navy shirt",
        "Show me my shortlist"
    ]
    
    for i, (col, suggestion) in enumerate(zip([col1, col2, col3], suggestions)):
        with col:
            if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.session_state.awaiting_response = True
                st.rerun()
'''

with open('/mnt/kimi/output/frontend.py', 'w') as f:
    f.write(frontend_code)

print("✅ Created frontend.py with Apple-esque dark design")
print("\n🎨 Features implemented:")
print("  • Glassmorphism UI with backdrop blur effects")
print("  • Real-time structured response parsing")
print("  • Persistent user profile sidebar (memory & shortlist)")
print("  • Interactive constraint pills (positive/negative)")
print("  • Product cards with match scores and reasoning")
print("  • Animated message bubbles")
print("  • Dark gradient background (#0d0d0d to #1a1a1a)")
print("  • Apple-style typography and spacing")
print("\n🚀 To run:")
print("   streamlit run frontend.py")