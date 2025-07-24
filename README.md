# Mach24 Flask Application
<!-- pyinstaller main.spec -->

A Flask-based web application for sensor data collection and visualization with real-time telemetry support.

## Features

- Real-time sensor data collection via serial communication
- Web-based dashboard with interactive visualizations
- SQLite database for data storage
- Export functionality to Excel/XLSX format
- WebSocket support for live data streaming
- Setup wizard for initial configuration

## Installation & Setup

### Running the EXE (Recommended)

1. Extract the distribution files
2. Run `mach24-server.exe` 
3. Open your browser to `http://localhost:5000`
4. Follow the setup wizard to configure your sensors

### Running from Source

1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Known Issues

### Eventlet Warning on Startup
When running the EXE, you may see this warning:
```
1 RLock(s) were not greened, to fix this error make sure you run eventlet.monkey_patch() before importing any other modules.
```

**This is a cosmetic warning and does not affect functionality.** It occurs because PyInstaller's bootloader imports some threading modules before our eventlet monkey patch can run. The application works perfectly despite this warning.

To minimize this warning in future builds, ensure eventlet.monkey_patch() is called as early as possible in the main.py file.

## Troubleshooting

### Port Already in Use
If you see "Port 5000 is already in use", either:
- Close any existing instances of the application
- Change the port in the configuration

### Serial Port Issues
- Ensure your sensor device is properly connected
- Check that no other applications are using the serial port
- Verify the correct COM port and baud rate settings

### Database Issues
- The application will create a new database file if one doesn't exist
- Database files are stored in the `database/` directory
- If corruption occurs, delete the database file and restart

## Building from Source

To create a new EXE distribution:

```bash
# Install build dependencies
pip install pyinstaller

# Build the application
pyinstaller main.spec

# The EXE will be in dist/mach24-server/
```

## API Endpoints

- `/` - Main dashboard
- `/setup` - Setup wizard
- `/api/data` - JSON data endpoint
- `/api/export` - Export data to Excel
- `/websocket` - Real-time data streaming

## Configuration

The application uses environment variables and database configuration:
- Database location: `database/sensor_data_*.db`
- Static files: `static/` directory  
- Templates: `templates/` directory

## License

Copyright © 2025 Mach24. All rights reserved.
