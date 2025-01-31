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

def send_system_status():
    """Send system status to the manager."""
    global SEND_DATA
    while True:
        if SEND_DATA:
            try:
                # Gather system information
                memory_usage = psutil.virtual_memory().percent
                cpu_usage = psutil.cpu_percent(interval=1)
                disk_usage = psutil.disk_usage('/').percent
                net_io = psutil.net_io_counters()
                net_info = f"Sent: {net_io.bytes_sent / (1024 ** 2):.2f} MB, Received: {net_io.bytes_recv / (1024 ** 2):.2f} MB"
                uptime_seconds = time.time() - psutil.boot_time()
                uptime = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))

                # Prepare data to send
                status_data = {
                    "agent_id": AGENT_ID,
                    "memory_usage": memory_usage,
                    "cpu_usage": cpu_usage,
                    "disk_usage": disk_usage,
                    "network_info": net_info,
                    "uptime": uptime
                }

                # Send data to the manager
                response = requests.post(f"http://{MANAGER_IP}:5000/status", json=status_data)
                if response.status_code == 200:
                    print("System status sent successfully.")
                else:
                    print(f"Failed to send system status: {response.status_code}")

                SEND_DATA = False  # Stop sending data after one response

            except Exception as e:
                print(f"Error sending system status: {e}")

        time.sleep(1)  # Check flag every second
