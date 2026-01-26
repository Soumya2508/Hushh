Hushh Power Agent MVP
This is a multi-agent system built for the Hushh.AI assignment. It features a Personal Shopping Concierge that can find products, remember what you like, and even give you styling advice based on what is already in your closet.

How it Works
The system uses a main router that looks at your message and decides which agent to talk to.


Shopping Agent: Handles product searches, filters by budget and size, and avoids things you don't like.


Stylist Agent: Looks at your existing clothes to see if a new purchase would match your style.


MCP Server: This is the tool layer that actually talks to the data files to search for products or save your preferences.

Key Features
Real Memory: If you tell the agent you hate chunky soles, it saves that as a "fact." The next time you ask for shoes, it will automatically filter those out without you asking again.


Fuzzy Search: The search tool is smart enough to find "white sneakers" even if the title is slightly different.


Structured Output: Everything comes back in a clean JSON format so it can be easily used by a website or app interface.

Resilience: If the product catalog file is missing or broken, the agent won't crash. It will just give you a polite message saying the data is currently offline.

How to Add a New Agent in under 30 Minutes
The code is modular, so adding a new specialized agent is easy:

Put a new JSON data file in the data folder.

Add a new tool in server.py to search that specific file.

Create a new agent class in the logic folder that inherits from the BaseAgent.

Update the router in main.py to recognize when a user wants to use this new agent.

Setup and Running
Install the requirements: pip install -r requirements.txt

Add your API key to the .env file.

Start the server: python main.py

Send a request using curl:
curl -X POST http://127.0.0.1:8000/agents/run -H "Content-Type: application/json" -d '{"user_id": "user1", "message": "I need white sneakers under 2500"}'