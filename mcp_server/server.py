import sys
import json
import os
import traceback
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("ShoppingTools")

# Absolute path calculation to ensure data files are always found regardless of execution context
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data"))

def _safe_load(filename, default=[]):
    """Safely loads JSON data from the data directory."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def _safe_save(filename, data):
    """Safely persists JSON data with proper formatting."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

@mcp.tool()
def search_products(query: str, budget_max: int = 2500, avoid_keywords: any = None):
    """
    Core search tool with robust negative filtering for excluded attributes.
    """
    products = _safe_load("catalog.json") #
    
    # 1. STANDARDIZE EXCLUSION LIST
    # Ensures the input is always a flat list of lowercase individual words.
    if isinstance(avoid_keywords, str):
        avoid_list = avoid_keywords.lower().split()
    elif isinstance(avoid_keywords, list):
        avoid_list = " ".join([str(i) for i in avoid_keywords]).lower().split()
    else:
        avoid_list = []

    # 2. FILTER OUT GENERIC WORDS
    # Prevents "soles" or "sneaker" from filtering out the entire catalog.
    avoid_list = [w for w in avoid_list if w not in ["soles", "shoes", "style", "sneaker", "sneakers"]]
    
    query_words = query.lower().split()
    results = []

    for p in products:
        title = p.get('title', "").lower()
        keywords = [k.lower() for k in p.get('style_keywords', [])]
        price = p.get('price_inr', 0)
        
        # 3. EXCLUSION CHECK (Negative Matching)
        # Skip this item if ANY forbidden word appears in the title or the metadata keywords.
        is_excluded = any(word in title or any(word in kw for kw in keywords) for word in avoid_list)
        if is_excluded:
            continue

        # 4. INCLUSION CHECK (Positive Matching)
        # Match if ANY query word (e.g., 'white') appears in the title or tags.
        matches_text = any(any(word in title or word in kw for kw in keywords) for word in query_words)
        
        # 5. BUDGET FILTER
        if matches_text and price <= int(budget_max):
            results.append(p)
    
    # Sort results by price for the UI
    sorted_results = sorted(results, key=lambda x: x.get('price_inr', 0))
    
    if not sorted_results:
        return {"message": "No products found matching your current preferences and budget."}
    
    return {"products": sorted_results}

@mcp.tool()
def get_product_details(product_id: str):
    """Fetches full metadata for a specific product ID."""
    products = _safe_load("catalog.json")
    product = next((p for p in products if str(p.get("product_id")) == str(product_id)), None)
    return product if product else {"error": "Product not found"}

@mcp.tool()
def save_shortlist(user_id: str, items: list):
    """Saves a user's shortlisted items to disk."""
    shortlists = _safe_load("shortlists.json", default={})
    shortlists[user_id] = items
    _safe_save("shortlists.json", shortlists)
    return {"status": "success", "message": f"Saved {len(items)} items to shortlist"}

@mcp.tool()
def get_shortlist(user_id: str):
    """Retrieves a user's previously saved shortlist."""
    shortlists = _safe_load("shortlists.json", default={})
    return shortlists.get(user_id, [])

@mcp.tool()
def write_memory(user_id: str, facts: list):
    """Updates user preferences (facts) in long-term memory."""
    memories = _safe_load("memory.json", default=[])
    user_mem = next((m for m in memories if m.get("user_id") == user_id), {"user_id": user_id, "facts": []})
    
    # Merge new facts into the set of unique existing facts
    user_mem["facts"] = list(set(user_mem["facts"] + facts))
    
    memories = [m for m in memories if m.get("user_id") != user_id]
    memories.append(user_mem)
    _safe_save("memory.json", memories)
    return {"status": "success", "facts_count": len(user_mem["facts"])}

@mcp.tool()
def read_memory(user_id: str):
    """Fetches stored preferences/facts for a specific user."""
    memories = _safe_load("memory.json", default=[])
    return next((m for m in memories if m.get("user_id") == user_id), {"user_id": user_id, "facts": []})

if __name__ == "__main__":
    # Start the FastMCP server with stdio transport
    mcp.run(transport="stdio")