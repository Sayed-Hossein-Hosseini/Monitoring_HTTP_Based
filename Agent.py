from flask import Flask, request, jsonify, send_file
import psutil
import time
import socket
import threading
import requests
import os
import subprocess

app = Flask(__name__)

# Configuration
MANAGER_IP = None  # Will be set by the user
AGENT_ID = socket.gethostname()  # Unique identifier for the agent (hostname)
SEND_DATA = False  # Flag to control when to send data

def get_manager_ip():
    """Get the Manager IP address from the user."""
    return input("Enter Manager IP address (default: 127.0.0.1): ").strip() or "127.0.0.1"