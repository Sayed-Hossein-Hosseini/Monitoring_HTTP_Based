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
CONNECTED = False  # Flag to track connection status
LAST_CONNECTION_TIME = 0  # Timestamp of the last successful connection
COOLDOWN_PERIOD = 30  # Cooldown period in seconds


def get_manager_ip():
    """Get the Manager IP address from the user."""
    return input("Enter Manager IP address (default: 127.0.0.1): ").strip() or "127.0.0.1"


def connect_to_manager():
    """Try to connect to the manager with retries."""
    global MANAGER_IP, CONNECTED, LAST_CONNECTION_TIME
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to Manager at {MANAGER_IP} (Attempt {attempt + 1}/{max_retries})...")
            response = requests.post(
                f"http://{MANAGER_IP}:5000/register",
                json={"agent_id": AGENT_ID, "address": "127.0.0.1"},  # Replace with actual IP if needed
                timeout=5  # Set a timeout for the request
            )
            if response.status_code == 200:
                print("Successfully connected to Manager.")
                CONNECTED = True
                LAST_CONNECTION_TIME = time.time()  # Update the last connection time
                return True
            else:
                print(f"Failed to connect to Manager. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Manager: {e}")

        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)  # Wait before retrying

    # If all attempts fail, ask for Manager IP again
    print("Failed to connect to Manager after multiple attempts.")
    CONNECTED = False
    return False


def monitor_cpu_usage():
    """Monitor CPU usage and send alerts if it exceeds 80%."""
    global CONNECTED, MANAGER_IP
    high_cpu_alert_sent = False  # Flag to track if high CPU alert has been sent

    while True:
        if CONNECTED:
            cpu_usage = psutil.cpu_percent(interval=1)  # Get CPU usage
            # print(f"Current CPU usage: {cpu_usage}%")  # Print current CPU usage in Agent console

            if cpu_usage > 80 and not high_cpu_alert_sent:
                # CPU usage is high, send alert
                alert_message = f"High CPU usage detected: {cpu_usage}%"
                print(alert_message)  # Print alert in Agent console
                try:
                    # Send alert to Manager
                    response = requests.post(
                        f"http://{MANAGER_IP}:5000/alert",
                        json={"agent_id": AGENT_ID, "message": alert_message},
                        timeout=5
                    )
                    if response.status_code == 200:
                        print("High CPU alert sent to Manager.")
                    else:
                        print(f"Failed to send high CPU alert to Manager. Status code: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Error sending high CPU alert: {e}")

                high_cpu_alert_sent = True  # Set flag to True

            elif cpu_usage <= 80 and high_cpu_alert_sent:
                # CPU usage is back to normal, send recovery message
                recovery_message = f"CPU usage back to normal: {cpu_usage}%"
                print(recovery_message)  # Print recovery message in Agent console
                try:
                    # Send recovery message to Manager
                    response = requests.post(
                        f"http://{MANAGER_IP}:5000/alert",
                        json={"agent_id": AGENT_ID, "message": recovery_message},
                        timeout=5
                    )
                    if response.status_code == 200:
                        print("CPU recovery message sent to Manager.")
                    else:
                        print(f"Failed to send CPU recovery message to Manager. Status code: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Error sending CPU recovery message: {e}")

                high_cpu_alert_sent = False  # Reset flag to False

        time.sleep(5)  # Check CPU usage every 5 seconds

def send_system_status():
    """Send system status to the manager."""
    global SEND_DATA, CONNECTED
    while True:
        if SEND_DATA and CONNECTED:
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
                response = requests.post(f"http://{MANAGER_IP}:5000/status", json=status_data, timeout=5)
                if response.status_code == 200:
                    print("System status sent successfully.")
                else:
                    print(f"Failed to send system status: {response.status_code}")
                    CONNECTED = False  # Mark connection as lost

                SEND_DATA = False  # Stop sending data after one response

            except requests.exceptions.RequestException as e:
                print(f"Error sending system status: {e}")
                CONNECTED = False  # Mark connection as lost

        time.sleep(1)  # Check flag every second


def get_system_logs():
    """Retrieve system logs with proper permissions."""
    if os.name == "nt":  # Windows
        try:
            result = subprocess.run(
                ["wevtutil", "qe", "Application", "/c:10", "/rd:true", "/f:text"],
                capture_output=True, text=True, check=True
            )
            return result.stdout if result.stdout else "No logs available"
        except Exception as e:
            return f"Error retrieving Windows logs: {e}"
    else:  # Linux/macOS
        log_file = "/var/log/syslog" if os.path.exists("/var/log/syslog") else None
        if log_file:
            try:
                with open(log_file, "r", errors="ignore") as f:
                    logs = f.readlines()[-10:]
                return "\n".join(logs) if logs else "No logs available"
            except Exception as e:
                return f"Error retrieving Linux logs: {e}"
        return "System log file not found."


def restart_system():
    """Restart the agent's system."""
    try:
        if os.name == "nt":  # Windows
            os.system("shutdown -r -t 0")
        else:  # Linux/macOS
            os.system("sudo reboot")
    except Exception as e:
        print(f"Error restarting system: {e}")


@app.route('/command', methods=['POST'])
def handle_command():
    """Endpoint for handling commands from the manager."""
    global SEND_DATA
    data = request.json
    command = data.get("command")

    if not command:
        return jsonify({"error": "Missing command"}), 400

    if command == "get_status":
        SEND_DATA = True  # Enable sending data
        return jsonify({"message": "Sending system status..."}), 200
    elif command == "get_process_count":
        process_count = len(psutil.pids())
        return jsonify({"process_count": process_count}), 200
    elif command == "get_logs":
        logs = get_system_logs()
        return jsonify({"logs": logs}), 200
    elif command == "restart":
        restart_system()
        return jsonify({"message": "Restarting system..."}), 200
    elif command == "send_file":
        file_address = input("Enter the file path to send: ").strip()
        if os.path.exists(file_address):
            return jsonify({"file_address": file_address}), 200
        else:
            return jsonify({"error": "File not found"}), 404
    else:
        return jsonify({"error": "Unknown command"}), 400


@app.route('/download_file', methods=['GET'])
def download_file():
    """Endpoint for downloading a file."""
    file_address = request.args.get("file_address")
    if file_address and os.path.exists(file_address):
        return send_file(file_address, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

    def monitor_connection():
        """Monitor the connection to the manager and attempt reconnection if lost."""
        global CONNECTED, MANAGER_IP, LAST_CONNECTION_TIME, COOLDOWN_PERIOD
        while True:
            if CONNECTED:
                # Check if the Manager is still reachable
                try:
                    response = requests.get(f"http://{MANAGER_IP}:5000/ping", timeout=5)
                    if response.status_code != 200:
                        print("Connection to Manager lost.")
                        CONNECTED = False
                except requests.exceptions.RequestException as e:
                    print(f"Connection to Manager lost: {e}")
                    CONNECTED = False
            else:
                # Check if the cooldown period has passed
                if time.time() - LAST_CONNECTION_TIME > COOLDOWN_PERIOD:
                    print("Attempting to reconnect to Manager...")
                    if connect_to_manager():
                        print("Reconnected to Manager.")
                    else:
                        print("Reconnection failed. Please check the Manager IP and try again.")
                        MANAGER_IP = get_manager_ip()  # Get new Manager IP from the user

            time.sleep(10)  # Check connection status every 10 seconds


def start_agent():
    """Start the agent REST API server."""
    global MANAGER_IP, CONNECTED
    MANAGER_IP = get_manager_ip()  # Get Manager IP from the user
    print(f"Connecting to Manager at {MANAGER_IP}...")

    # Try to connect to the manager with retries
    if not connect_to_manager():
        print("Failed to connect to Manager. Please check the Manager IP and try again.")
        MANAGER_IP = get_manager_ip()  # Get new Manager IP from the user
        if not connect_to_manager():
            print("Exiting...")
            return

    # Start the connection monitor in a separate thread
    threading.Thread(target=monitor_connection, daemon=True).start()

    # Start the system status sender in a separate thread
    threading.Thread(target=send_system_status, daemon=True).start()

    # Start the CPU usage monitor in a separate thread
    threading.Thread(target=monitor_cpu_usage, daemon=True).start()

    # Start the Flask server to handle commands from the manager
    app.run(host="0.0.0.0", port=5001)

if __name__ == "__main__":
    start_agent()




