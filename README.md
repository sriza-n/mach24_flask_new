# Mach24 Flask Application

A Flask-based web application for sensor data collection and visualization.

## Features

- Real-time sensor data collection via serial port
- Data storage in SQLite database
- Data visualization and streaming
- IP camera video streaming
- WebSocket-based real-time updates with Socket.IO

## Installation

There are two ways to set up the application:

### Option 1: Automated Setup (Recommended for Windows)

1. Run the setup script:

```powershell
# In PowerShell
.\setup.ps1
```

This script will create a virtual environment, upgrade pip, and install all required dependencies.

### Option 2: Manual Setup

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

3. Update pip and install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

The application will run on http://localhost:5000

## Available Routes

- `/` - Main dashboard
- `/visualize` - Data visualization page
- `/stream` - Data streaming page
- `/latest_data` - API endpoint for latest sensor data
- `/status` - API endpoint for system status
- `/serial_status` - API endpoint for serial connection status
- `/video` - Video streaming from IP camera

## Serial Communication

The application automatically attempts to connect to available serial ports. Data is expected in JSON format with the prefix "D:". Example:

```
D:{"T":"12:34:56", "p1":101.3, "p2":102.5, "ST":1, "T1":25.3, "LC":12.34}
```

## Socket.IO Events

- `connection_test` - Connection established
- `new_data` - New sensor data received
- `connection_status` - Serial connection status update
- `start_serial` - Request to start serial connection
- `stop_serial` - Request to stop serial connection

## Database

Data is stored in the `database/sensor_data.db` SQLite database with two tables:
- `sensor_data` - For data with ST=1
- `sensor_data0` - For data with ST=0

## Requirements

- Python 3.6 or higher
- Flask and extensions (see requirements.txt)
- Serial device for data collection (optional)
- IP camera for video streaming (optional)
