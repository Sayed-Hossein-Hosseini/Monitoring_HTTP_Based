from flask import Flask, request, jsonify
import threading
import requests

app = Flask(__name__)

# Configuration
AUTHORIZED_AGENTS = {"127.0.0.1"}  # Allowed agent IPs
AGENTS = []  # List to hold information about connected agents


@app.route('/register', methods=['POST'])
def register():
    """Endpoint for registering new agents."""
    data = request.json
    agent_id = data.get("agent_id")
    agent_ip = request.remote_addr

    if agent_ip not in AUTHORIZED_AGENTS:
        return jsonify({"error": "Unauthorized"}), 403

    # Add agent to the list
    AGENTS.append({"id": agent_id, "address": agent_ip})
    print(f"New agent connected: {agent_id} ({agent_ip})")
    print_agents()  # Print the updated list of agents

    return jsonify({"message": "Agent registered successfully"}), 200

@app.route('/status', methods=['POST'])
def status():
    """Endpoint for receiving system status from agents."""
    data = request.json
    agent_id = data.get("agent_id")
    agent_ip = request.remote_addr

    if agent_ip not in AUTHORIZED_AGENTS:
        return jsonify({"error": "Unauthorized"}), 403

    # Update or add agent information
    agent = next((agent for agent in AGENTS if agent["id"] == agent_id), None)
    if agent:
        agent["status"] = data
    else:
        AGENTS.append({"id": agent_id, "address": agent_ip, "status": data})
        print(f"New agent connected: {agent_id} ({agent_ip})")
        print_agents()  # Print the updated list of agents

    # Print the received status
    print(f"Received status from {agent_id}: {data}")
    return jsonify({"message": "Status received"}), 200

@app.route('/alert', methods=['POST'])
def alert():
    """Endpoint for receiving alerts from agents."""
    data = request.json
    agent_id = data.get("agent_id")
    agent_ip = request.remote_addr

    if agent_ip not in AUTHORIZED_AGENTS:
        return jsonify({"error": "Unauthorized"}), 403

    print(f"Received alert from {agent_id}: {data}")
    return jsonify({"message": "Alert received"}), 200

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """Endpoint for receiving files from agents."""
    agent_ip = request.remote_addr

    if agent_ip not in AUTHORIZED_AGENTS:
        return jsonify({"error": "Unauthorized"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    file.save(file.filename)
    print(f"File '{file.filename}' received from {agent_ip}.")
    return jsonify({"message": "File received successfully"}), 200

@app.route('/agents', methods=['GET'])
def list_agents():
    """Endpoint for listing all connected agents."""
    return jsonify({"agents": AGENTS}), 200

def print_agents():
    """Print the list of connected agents."""
    print("\nConnected Agents:")
    for i, agent in enumerate(AGENTS):
        print(f"{i + 1}. ID: {agent['id']}, Address: {agent['address']}")

def send_command_to_agent(agent, command):
    """Send a command to the selected agent."""
    agent_url = f"http://{agent['address']}:5001/command"  # Assuming agent runs on port 5001
    try:
        if command == "send_file":
            print("Waiting to receive file address from the agent...")
            response = requests.post(agent_url, json={"command": command})
            if response.status_code == 200:
                file_address = response.json().get("file_address")
                if file_address:
                    print(f"Received file address: {file_address}")
                    # Now request the file from the agent
                    print("Requesting the file from the agent...")
                    file_response = requests.get(f"http://{agent['address']}:5001/download_file?file_address={file_address}", stream=True)
                    if file_response.status_code == 200:
                        file_name = file_address.split("/")[-1]  # Extract file name from the address
                        with open(file_name, "wb") as f:
                            for chunk in file_response.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                        print(f"File '{file_name}' received successfully.")
                    else:
                        print("Failed to download the file.")
                else:
                    print("No file address received from the agent.")
            else:
                print("Failed to receive file address from the agent.")
        else:
            response = requests.post(agent_url, json={"command": command})
            if response.status_code == 200:
                print(f"Response from {agent['id']}: {response.json()}")
            else:
                print(f"Failed to send command to {agent['id']}")
    except Exception as e:
        print(f"Error communicating with {agent['id']}: {e}")

def command_interface():
    """Command line interface for sending commands to agents."""
    while True:
        print_agents()
        try:
            selected_agent = int(input("Select an agent by number or enter 0 to exit: ")) - 1
            if selected_agent == -1:
                print("Exiting...")
                break
            if 0 <= selected_agent < len(AGENTS):
                agent = AGENTS[selected_agent]
                while True:
                    print("\nAvailable Commands:")
                    print("1. Get_Status")
                    print("2. Get_Process_Count")
                    print("3. Get_Logs")
                    print("4. Get_File")
                    print("5. Restart")
                    print("6. Back to Agent List")
                    command_number = input("Enter command number: ").strip()
                    commands = {
                        "1": "get_status",
                        "2": "get_process_count",
                        "3": "get_logs",
                        "4": "send_file",
                        "5": "restart",
                        "6": "back"
                    }
                    if command_number in commands:
                        command = commands[command_number]
                        if command == "back":
                            break
                        send_command_to_agent(agent, command)
                        # Wait for the user to press Enter before showing the command list again
                        input("\nPress Enter to continue...\n")
                    else:
                        print("Invalid command number. Try again.")
            else:
                print("Invalid selection. Try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def start_manager():
    """Start the manager REST API server."""
    print("Starting Manager REST API server...")
    # Start the command interface in a separate thread
    threading.Thread(target=command_interface, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)