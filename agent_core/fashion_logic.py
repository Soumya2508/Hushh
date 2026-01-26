import os
import json
from agent_core.base import BaseAgent

class FashionStylistAgent(BaseAgent):
    def _load_closet(self):
        """Helper to load the user's current wardrobe."""
        path = os.path.join("data", "closet.json")
        if not os.path.exists(path):
            return []
        with open(path, "r") as f:
            data = json.load(f)
            # Accessing based on user_id passed during init
            return data.get(self.user_id, [])

    async def process_request(self, message: str):
        """
        Async implementation to match the ShoppingAgent signature.
        This allows the main router to 'await' the response.
        """
        # 1. Fetch user's existing clothes
        closet = self._load_closet()
        closet_summary = ", ".join([f"{i['color']} {i['type']}" for i in closet])
        
        print(f"[TRACE {self.trace_id}] Analyzing style with closet: {closet_summary}")

        # 2. Reasoning: Match the request with owned items
        # Currently uses static logic; future integration can use LLM reasoning
        advice = f"Based on your closet ({closet_summary}), those white sneakers are a perfect match for your dark indigo jeans."
        
        return {
            "agent": "fashion_stylist_agent",
            "trace_id": self.trace_id,
            "understood_request": {"intent": "styling_advice"},
            "results": [{"advice": advice, "owned_items_referenced": closet}],
            "next_actions": [{"action": "VIEW_STYLING_GUIDE"}]
        }