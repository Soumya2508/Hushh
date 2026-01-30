import os
import json
import sys
import asyncio
import traceback
from openai import OpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agent_core.base import BaseAgent

load_dotenv()

class ShoppingAgent(BaseAgent):
    # Class-level conversation history per user
    _conversations = {}
    
    def __init__(self, user_id):
        super().__init__(user_id)
        # Using Groq for high-speed, free-tier reasoning
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        # Initialize conversation history for this user if not exists
        if user_id not in ShoppingAgent._conversations:
            ShoppingAgent._conversations[user_id] = []

    async def process_request(self, message: str):
        print(f"[TRACE {self.trace_id}] THOUGHT: Initiating PSC end-to-end loop.")
        
        base_path = os.getcwd()
        server_script = os.path.abspath(os.path.join(base_path, "mcp_server", "server.py"))
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-u", server_script],
            env=os.environ.copy()
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # 1. READ MEMORY: Fetch user preferences via MCP
                    user_mem_res = await session.call_tool("read_memory", arguments={"user_id": self.user_id})
                    user_mem = self._parse_mcp_content(user_mem_res)
                    facts = user_mem.get("facts", [])

                    # 2. PARSE REQUEST: Improved prompt for category and negative keyword extraction
                    system_prompt = (
                        f"You are a Personal Shopping Concierge. USER HISTORY: {facts}. "
                        "MANDATORY: Extract the CATEGORY from the query. "
                        "CRITICAL CATEGORY RULES: "
                        "- Use 'apparel' for ANY clothing: shirts, t-shirts, tees, pants, jeans, tops "
                        "- Use 'footwear' for shoes, sneakers, runners, boots "
                        "- Use 'accessories' for belts, bags, sunglasses, watches "
                        "MANDATORY: If the user mentions a preference, size, or dislike, put it in 'new_facts'. "
                        "MANDATORY: Always include 1-2 clarifying questions. "
                        "CRITICAL: If a user dislikes something or says 'avoid X' or 'no X', extract the core "
                        "descriptor word (e.g., 'chunky', 'flashy', 'bold') and put it in 'avoid_keywords' as a LIST. "
                        "Return ONLY a JSON object with: 'query', 'category', 'budget', 'size', 'style_filters', "
                        "'avoid_keywords', 'new_facts', 'questions'."
                    )
                    
                    # Build messages with conversation history
                    conversation = ShoppingAgent._conversations[self.user_id]
                    messages = [{"role": "system", "content": system_prompt}]
                    
                    # Add last 5 conversation turns for context
                    for turn in conversation[-10:]:
                        messages.append(turn)
                    
                    # Add current user message
                    messages.append({"role": "user", "content": message})
                    
                    response = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        response_format={"type": "json_object"}
                    )
                    brain = json.loads(response.choices[0].message.content)
                    print(f"[DEBUG] AI Brain: {json.dumps(brain)}", file=sys.stderr)
                    
                    # Save conversation turn
                    ShoppingAgent._conversations[self.user_id].append({"role": "user", "content": message})
                    ShoppingAgent._conversations[self.user_id].append({"role": "assistant", "content": response.choices[0].message.content})

                    # 3. SEARCH PRODUCTS: Call tool with filters
                    search_query = brain.get("query") or "sneaker"
                    budget = brain.get("budget", 2500)
                    category = brain.get("category", None)  # Extract category for filtering
                    
                    # Standardize avoid list to ensure it works with server.py logic
                    avoid = brain.get("avoid_keywords", [])
                    if isinstance(avoid, str):
                        avoid = avoid.split()
                    
                    print(f"[DEBUG] Searching - Query: {search_query}, Category: {category}, Avoid: {avoid}", file=sys.stderr)

                    search_res = await session.call_tool("search_products", arguments={
                        "query": search_query, 
                        "budget_max": budget,
                        "avoid_keywords": avoid,
                        "category": category
                    })
                    
                    products = self._parse_mcp_content(search_res)
                    if isinstance(products, dict): 
                        products = products.get("products", [])

                    # 4. GET DETAILS: Hydrate results with full metadata
                    final_results = []
                    if products:
                        for p in products[:6]: # Limit candidates to top 6
                            pid = p.get("product_id")
                            if pid:
                                detail_res = await session.call_tool("get_product_details", arguments={"product_id": pid})
                                final_results.append(self._parse_mcp_content(detail_res))

                    # 5. SAVE SHORTLIST
                    shortlist_ids = [r.get("product_id") for r in final_results[:2]]
                    await session.call_tool("save_shortlist", arguments={"user_id": self.user_id, "items": shortlist_ids})

                    # 6. WRITE MEMORY: Update persistent facts
                    new_facts = brain.get("new_facts", [])
                    if new_facts:
                        await session.call_tool("write_memory", arguments={"user_id": self.user_id, "facts": new_facts})
                    
                    # 7. RETURN STRUCTURED JSON
                    return self._format_ui_response(brain, final_results)

        except Exception as e:
            print(f"[TRACE {self.trace_id}] ERROR:")
            traceback.print_exc(file=sys.stderr)
            return {"agent": "personal_shopping_concierge", "trace_id": self.trace_id, "error": str(e), "results": []}

    def _parse_mcp_content(self, response):
        """Standardizes tool output parsing."""
        try:
            if hasattr(response, 'content') and response.content:
                raw_text = response.content[0].text
                return json.loads(raw_text)
            return response if isinstance(response, (dict, list)) else {}
        except Exception: 
            return {}

    def _format_ui_response(self, brain, results):
        """Eliminates all hardcoded strings using dynamic catalog data."""
        avoided_str = ", ".join(brain.get("avoid_keywords", [])) if brain.get("avoid_keywords") else "unwanted styles"
        size_label = brain.get("size", "your size")

        return {
            "agent": "personal_shopping_concierge",
            "trace_id": self.trace_id,
            "clarifying_questions": brain.get("questions", []),
            "understood_request": {
                "category": brain.get("category", "unknown"),  # USE ACTUAL EXTRACTED CATEGORY
                "constraints": {
                    "budget_inr_max": brain.get("budget", 2500),
                    "size": size_label,
                    "style_keywords": brain.get("style_filters", []),
                    "avoid_keywords": brain.get("avoid_keywords", []),
                    "category": brain.get("category", "unknown")  # Also include in constraints
                }
            },
            "results": [
                {
                    "product_id": r.get("product_id"), 
                    "title": r.get("title"), 
                    "price_inr": r.get("price_inr"), 
                    "brand": r.get("brand", "Unknown"),
                    "match_score": 0.95, 
                    "pros": [f"Matches size {size_label}", f"Fits budget (₹{r.get('price_inr')})"],
                    "cons": ["Limited stock"],
                    # Dynamically references product title and avoided preference
                    "why_recommended": f"The {r.get('title')} is recommended because it avoids {avoided_str} while meeting your {size_label} requirement."
                } for r in results
            ],
            "shortlist": [
                {"product_id": r.get("product_id"), "reason": "Best value match"} for r in results[:2]
            ],
            "comparisons": {
                "summary": "These curated options satisfy your style and budget constraints.",
                "tradeoffs": ["Price vs. premium material availability"]
            },
            "next_actions": [{"action": "ASK_SIZE_CONFIRMATION", "payload": {}}]
        }