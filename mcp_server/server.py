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
def search_products(query: str, budget_max: int = 2500, avoid_keywords: any = None, category: str = None):
    """
    Core search tool with category filtering and robust negative filtering for excluded attributes.
    
    Args:
        query: Search query (e.g., "white sneakers")
        budget_max: Maximum budget in INR
        avoid_keywords: Keywords to exclude from results (checks title AND style_keywords)
        category: Optional category filter ("footwear", "apparel", "accessories")
    """
    products = _safe_load("catalog.json")
    
    # 1. STANDARDIZE EXCLUSION LIST
    # Ensures the input is always a flat list of lowercase individual words.
    if isinstance(avoid_keywords, str):
        avoid_list = avoid_keywords.lower().split()
    elif isinstance(avoid_keywords, list):
        avoid_list = " ".join([str(i) for i in avoid_keywords]).lower().split()
    else:
        avoid_list = []

    # 2. FILTER OUT OVERLY GENERIC WORDS that would exclude too much
    # But keep style-specific words like "chunky", "flashy", "bold" etc.
    generic_words = ["soles", "shoes", "style", "designs", "design"]
    avoid_list = [w for w in avoid_list if w not in generic_words]
    
    # Debug logging
    print(f"[SEARCH] Query: {query}, Category: {category}, Avoid: {avoid_list}, Budget: {budget_max}", file=sys.stderr)
    
    query_words = query.lower().split()
    results = []

    for p in products:
        title = p.get('title', "").lower()
        keywords = [k.lower() for k in p.get('style_keywords', [])]
        price = p.get('price_inr', 0)
        product_category = p.get('category', "").lower()
        product_sub_category = p.get('sub_category', "").lower()
        
        # 3. CATEGORY FILTER (NEW!)
        # If category is specified, ONLY show products from that category
        if category:
            category_lower = category.lower()
            # Map common query terms to categories
            category_mappings = {
                "sneakers": "footwear",
                "sneaker": "footwear",
                "shoes": "footwear",
                "shoe": "footwear",
                "runners": "footwear",
                "running": "footwear",
                "footwear": "footwear",
                "shirts": "apparel",
                "shirt": "apparel",
                "t-shirts": "apparel",
                "t-shirt": "apparel",
                "tee": "apparel",
                "tees": "apparel",
                "tops": "apparel",
                "pants": "apparel",
                "jeans": "apparel",
                "apparel": "apparel",
                "clothing": "apparel",
                "clothes": "apparel",
                "accessories": "accessories",
                "belts": "accessories",
                "sunglasses": "accessories"
            }
            
            # Get the normalized category
            normalized_category = category_mappings.get(category_lower, category_lower)
            
            # Skip if product doesn't match the category
            if product_category != normalized_category:
                continue
        
        # 4. EXCLUSION CHECK - Check BOTH title AND style_keywords
        # Skip this item if ANY forbidden word appears in title OR in style_keywords
        is_excluded = False
        for word in avoid_list:
            # Check if word appears in title
            if word in title:
                is_excluded = True
                break
            # Check if word matches ANY style keyword (exact or partial match)
            for kw in keywords:
                if word in kw or kw in word:
                    is_excluded = True
                    break
            if is_excluded:
                break
                
        if is_excluded:
            print(f"[SEARCH] Excluded: {p.get('title')} (matched avoid word)", file=sys.stderr)
            continue

        # 5. INCLUSION CHECK (Positive Matching)
        # Match if ANY query word appears in title, style_keywords, or sub_category
        matches_text = False
        for word in query_words:
            if word in title:
                matches_text = True
                break
            if word in product_sub_category:
                matches_text = True
                break
            for kw in keywords:
                if word in kw:
                    matches_text = True
                    break
            if matches_text:
                break
        
        # 6. BUDGET FILTER
        if matches_text and price <= int(budget_max):
            results.append(p)
    
    # Sort results by price for the UI
    sorted_results = sorted(results, key=lambda x: x.get('price_inr', 0))
    
    print(f"[SEARCH] Found {len(sorted_results)} products", file=sys.stderr)
    
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