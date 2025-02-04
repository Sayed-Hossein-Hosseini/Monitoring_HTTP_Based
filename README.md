# Monitoring_HTTP_Based

This project is an HTTP-based monitoring system that consists of a **Manager** and **Agent** architecture. The Manager is responsible for monitoring and managing multiple Agents, while the Agents collect and report system metrics such as CPU usage, memory usage, disk usage, and more. The system also supports file transfers, alerts, and remote commands.

---

## Features

### **Manager**
- **Agent Registration**: Agents can register with the Manager using their unique ID and IP address.
- **Status Monitoring**: Agents periodically send system status (CPU, memory, disk, network, uptime) to the Manager.
- **Alert Handling**: Agents can send alerts to the Manager (e.g., high CPU usage).
- **File Upload**: Agents can upload files to the Manager.
- **Command Interface**: The Manager can send commands to Agents (e.g., get status, get logs, restart system, download files).
- **Real-Time Monitoring**: The Manager provides a command-line interface (CLI) for interacting with Agents in real-time.

### **Agent**
- **System Metrics Collection**: Collects CPU, memory, disk, and network usage data.
- **Alert Generation**: Sends alerts to the Manager when system metrics exceed thresholds (e.g., CPU usage > 80%).
- **Command Execution**: Executes commands received from the Manager (e.g., restart, send logs, send files).
- **File Transfer**: Supports file upload and download between the Agent and Manager.
- **Connection Monitoring**: Automatically reconnects to the Manager if the connection is lost.

---

## Project Structure

### **Manager (`manager.py`)**
- **Endpoints**:
  - `/register`: Registers new Agents.
  - `/status`: Receives system status updates from Agents.
  - `/alert`: Receives alerts from Agents.
  - `/upload_file`: Handles file uploads from Agents.
  - `/agents`: Lists all connected Agents.
- **Command Interface**: Provides a CLI for sending commands to Agents.

### **Agent (`agent.py`)**
- **Endpoints**:
  - `/command`: Handles commands from the Manager.
  - `/download_file`: Handles file downloads requested by the Manager.
- **Background Tasks**:
  - Monitors CPU usage and sends alerts.
  - Sends system status updates to the Manager.
  - Monitors connection to the Manager and reconnects if necessary.

---

## How It Works

1. **Agent Registration**:
   - Agents register with the Manager by sending their ID and IP address to the `/register` endpoint.
   - The Manager maintains a list of connected Agents.

2. **System Monitoring**:
   - Agents collect system metrics (CPU, memory, disk, network, uptime) and send them to the Manager via the `/status` endpoint.

3. **Alert Handling**:
   - Agents monitor CPU usage and send alerts to the Manager via the `/alert` endpoint if usage exceeds 80%.

4. **File Transfer**:
   - Agents can upload files to the Manager using the `/upload_file` endpoint.
   - The Manager can request files from Agents using the `send_file` command.

5. **Command Execution**:
   - The Manager sends commands to Agents via the `/command` endpoint.
   - Supported commands:
     - `get_status`: Request system status.
     - `get_process_count`: Get the number of running processes.
     - `get_logs`: Retrieve system logs.
     - `restart`: Restart the Agent's system.
     - `send_file`: Request a file from the Agent.

6. **Connection Monitoring**:
   - Agents continuously monitor their connection to the Manager and attempt to reconnect if the connection is lost.

---

## Installation and Setup

### Prerequisites
- Python 3.x
- Flask (`pip install flask`)
- Requests (`pip install requests`)
- Psutil (`pip install psutil`)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Run the Manager**:
   ```bash
   python manager.py
   ```
   - The Manager will start on `http://0.0.0.0:5000`.

3. **Run the Agent**:
   ```bash
   python agent.py
   ```
   - The Agent will prompt you to enter the Manager's IP address (default: `127.0.0.1`).
   - The Agent will start on `http://0.0.0.0:5001`.

4. **Interact with the System**:
   - Use the Manager's CLI to send commands to Agents.
   - Monitor system status and alerts in real-time.

---

## Usage Examples

### **Manager CLI**
1. **List Connected Agents**:
   ```
   Connected Agents:
   1. ID: Agent1, Address: 127.0.0.1
   ```

2. **Send Commands to an Agent**:
   - Select an Agent and choose a command (e.g., `get_status`, `get_logs`, `send_file`).

3. **View Alerts**:
   - Alerts (e.g., high CPU usage) are displayed in the Manager's console.

### **Agent**
1. **Send System Status**:
   - The Agent periodically sends system status to the Manager.

2. **Send Alerts**:
   - The Agent sends alerts to the Manager when CPU usage exceeds 80%.

3. **Execute Commands**:
   - The Agent executes commands received from the Manager (e.g., restart, send logs).

---

## Screenshots

### Manager CLI
![Manager CLI](https://via.placeholder.com/600x400.png?text=Manager+CLI)

### Agent Console
![Agent Console](https://via.placeholder.com/600x400.png?text=Agent+Console)

---

## Future Enhancements
- **Dashboard**: Add a web-based dashboard for real-time monitoring.
- **Authentication**: Implement authentication for secure communication between the Manager and Agents.
- **More Metrics**: Add support for additional system metrics (e.g., GPU usage, temperature).
- **Scalability**: Optimize the system for large-scale deployments.

---

## Contribution  

If you would like to contribute to the development of this project, follow these steps:  

1. Fork the project.  
2. Create a new branch (`git checkout -b feature/YourFeatureName`).  
3. Commit your changes (`git commit -m 'Add some feature'`).  
4. Push your changes to your branch (`git push origin feature/YourFeatureName`).  
5. Create a Pull Request.

---

## Acknowledgments
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Psutil](https://psutil.readthedocs.io/) for system monitoring.
- [Scapy](https://scapy.net/) for network packet manipulation (if used in future enhancements).

---

## License  

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

> **Note:** This project is designed for educational and experimental purposes. Using it in production environments requires thorough testing and evaluation.

---

## Author
Sayyed Hossein Hosseini DolatAbadi 
