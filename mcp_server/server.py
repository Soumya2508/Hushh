import sys
import json
import os
import traceback
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("ShoppingTools")

# Absolute path calculation
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data"))

def _safe_load(filename, default=[]):
    """Safely loads JSON data for Test 4 (Graceful Failure) compliance."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def _safe_save(filename, data):
    """Safely persists JSON data."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

@mcp.tool()
def search_products(query: str, budget_max: int = 2500):
    """
    Core search tool for Test 1. 
    Improved fuzzy matching to ensure results are found.
    """
    print(f"\n[MCP] Tool: search_products(query='{query}', budget={budget_max})", file=sys.stderr)
    try:
        products = _safe_load("catalog.json")
        budget_max = int(budget_max)
        
        # Split query into words
        query_words = query.lower().split()
        
        results = []
        for p in products:
            title = p.get('title', "").lower()
            keywords = [k.lower() for k in p.get('style_keywords', [])]
            price = p.get('price_inr', 0)
            
            # OR-logic: Match if ANY query word appears in the title or keywords
            matches_text = any(any(word in title or word in kw for kw in keywords) for word in query_words)
            
            if matches_text and price <= budget_max:
                results.append(p)
        
        # Requirement: Sort by price to show best value
        results = sorted(results, key=lambda x: x.get('price_inr', 0))

        print(f"[MCP] Search successful. Found {len(results)} items.", file=sys.stderr)
        return {"products": results} if results else {"message": "No products found matching criteria"}

    except Exception as e:
        print(f"[MCP CRITICAL ERROR]\n{traceback.format_exc()}", file=sys.stderr)
        return {"error": str(e)}

@mcp.tool()
def get_product_details(product_id: str):
    """Fetches full metadata for the PSC loop."""
    products = _safe_load("catalog.json")
    product = next((p for p in products if str(p.get("product_id")) == str(product_id)), None)
    return product if product else {"error": "Product not found"}

@mcp.tool()
def save_shortlist(user_id: str, items: list):
    """Saves user shortlist."""
    shortlists = _safe_load("shortlists.json", default={})
    shortlists[user_id] = items
    _safe_save("shortlists.json", shortlists)
    return {"status": "success", "message": f"Saved {len(items)} items to shortlist"}

@mcp.tool()
def get_shortlist(user_id: str):
    """Retrieves saved shortlist."""
    shortlists = _safe_load("shortlists.json", default={})
    return shortlists.get(user_id, [])

@mcp.tool()
def write_memory(user_id: str, facts: list):
    """Updates user preferences for Test 3."""
    memories = _safe_load("memory.json", default=[])
    user_mem = next((m for m in memories if m.get("user_id") == user_id), {"user_id": user_id, "facts": []})
    
    user_mem["facts"] = list(set(user_mem["facts"] + facts))
    
    memories = [m for m in memories if m.get("user_id") != user_id]
    memories.append(user_mem)
    _safe_save("memory.json", memories)
    return {"status": "success", "facts_count": len(user_mem["facts"])}

@mcp.tool()
def read_memory(user_id: str):
    """Fetches stored preferences."""
    memories = _safe_load("memory.json", default=[])
    return next((m for m in memories if m.get("user_id") == user_id), {"user_id": user_id, "facts": []})

if __name__ == "__main__":
    mcp.run(transport="stdio")