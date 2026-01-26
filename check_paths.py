import os

# Check if the 'data' folder and server exist in the right place
base_path = os.getcwd()
data_dir = os.path.join(base_path, "data")
server_script = os.path.join(base_path, "mcp_server", "server.py")

print(f"Current Working Directory: {base_path}")
print(f"Data Directory exists: {os.path.exists(data_dir)}")
print(f"Server script exists: {os.path.exists(server_script)}")