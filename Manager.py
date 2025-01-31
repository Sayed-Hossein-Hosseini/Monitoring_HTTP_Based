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
