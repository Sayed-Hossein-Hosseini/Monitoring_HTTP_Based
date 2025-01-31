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