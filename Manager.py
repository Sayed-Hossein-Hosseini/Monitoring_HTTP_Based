from flask import Flask, request, jsonify
import threading
import requests

app = Flask(__name__)

# Configuration
AUTHORIZED_AGENTS = {"127.0.0.1"}  # Allowed agent IPs
AGENTS = []  # List to hold information about connected agents
