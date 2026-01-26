from abc import ABC, abstractmethod
import uuid

class BaseAgent(ABC):
    def __init__(self, user_id):
        self.user_id = user_id
        # Required for Observability: unique ID to track each session
        self.trace_id = str(uuid.uuid4())

    @abstractmethod
    def process_request(self, message: str):
        """
        This is a placeholder method.
        All specialized agents (like ShoppingAgent) MUST implement this.
        """
        pass