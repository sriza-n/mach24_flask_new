"""
Mach24 Flask Application
A Flask-based web application for sensor data collection and visualization.
"""
import os
import json
import time
import logging
import threading
from datetime import datetime

from flask import Flask, jsonify, render_template, Response, send_from_directory, redirect, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import serial
import serial.tools.list_ports
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'mach24_secret_key'

# # Define the absolute path to node_modules
# NODE_MODULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'node_modules')

# @app.route('/node_modules/<path:filename>')
# def serve_node_modules(filename):
#     """Serve files from node_modules directory."""
#     try:
#         return send_from_directory(NODE_MODULES_PATH, filename)
#     except Exception as e:
#         logger.error(f"Error serving node_modules: {e}")
#         return f"File not found: {filename}", 404

# Configure the SQLite database-------------------------
# Create database directory if it doesn't exist
database_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir, exist_ok=True)

# Store current database info for reference
current_database = {
    'filename': None,
    'path': None
}

def get_available_databases():
    """List all available database files in the database directory."""
    try:
        db_files = [f for f in os.listdir(database_dir) if f.endswith('.db')]
        db_files.sort(reverse=True)  # Most recent first
        return db_files
    except Exception as e:
        logger.error(f"Error listing database files: {e}")
        return []

def initialize_database(db_filename=None):
    """Initialize database connection with specified file or create new one."""
    global current_database
    
    if db_filename:
        # Use specified database file
        database_path = os.path.join(database_dir, db_filename)
        if not os.path.exists(database_path):
            logger.error(f"Database file not found: {db_filename}")
            return False
        logger.info(f"Using existing database: {db_filename}")
    else:
        # Generate timestamp for database filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_filename = f'sensor_data_{timestamp}.db'
        database_path = os.path.join(database_dir, db_filename)
        logger.info(f"Creating new database: {db_filename}")
    
    # Update current database info
    current_database['filename'] = db_filename
    current_database['path'] = database_path
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return True

# Initialize with a new database by default
initialize_database()

db = SQLAlchemy(app)

# ========= Database Models =========
class SensorData(db.Model):
    """Model for sensor data when ST=1."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    record_sn = db.Column(db.String(20), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    teensytemp = db.Column(db.Float, nullable=False)
    nano_value1 = db.Column(db.Integer, nullable=False)
    nano_value2 = db.Column(db.Integer, nullable=False)
    nano_value3 = db.Column(db.Integer, nullable=False)
    nano_value4 = db.Column(db.Integer, nullable=False)
    valve_state = db.Column(db.String(20), nullable=False)
    x_pos = db.Column(db.Float, nullable=False)
    y_pos = db.Column(db.Float, nullable=False)
    alt = db.Column(db.Float, nullable=False)
    eu_x = db.Column(db.Float, nullable=False)
    eu_y = db.Column(db.Float, nullable=False)
    eu_z = db.Column(db.Float, nullable=False)
    acc_x = db.Column(db.Float, nullable=False)
    acc_y = db.Column(db.Float, nullable=False)
    acc_z = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    gps_alt = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "date": self.date,
            "time": self.time,
            "teensytime": self.teensytime,
            "record_sn": self.record_sn,
            "voltage": self.voltage,
            "current": self.current,
            "teensytemp": self.teensytemp,
            "nano_value1": self.nano_value1,
            "nano_value2": self.nano_value2,
            "nano_value3": self.nano_value3,
            "nano_value4": self.nano_value4,
            "valve_state": self.valve_state,
            "x_pos": self.x_pos,
            "y_pos": self.y_pos,
            "alt": self.alt,
            "eu_x": self.eu_x,
            "eu_y": self.eu_y,
            "eu_z": self.eu_z,
            "acc_x": self.acc_x,
            "acc_y": self.acc_y,
            "acc_z": self.acc_z,
            "lat": self.lat,
            "lon": self.lon,
            "gps_alt": self.gps_alt
        }

class SensorData0(db.Model):
    """Model for sensor data when ST=0."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    record_sn = db.Column(db.String(20), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    teensytemp = db.Column(db.Float, nullable=False)
    nano_value1 = db.Column(db.Integer, nullable=False)
    nano_value2 = db.Column(db.Integer, nullable=False)
    nano_value3 = db.Column(db.Integer, nullable=False)
    nano_value4 = db.Column(db.Integer, nullable=False)
    valve_state = db.Column(db.String(20), nullable=False)
    x_pos = db.Column(db.Float, nullable=False)
    y_pos = db.Column(db.Float, nullable=False)
    alt = db.Column(db.Float, nullable=False)
    eu_x = db.Column(db.Float, nullable=False)
    eu_y = db.Column(db.Float, nullable=False)
    eu_z = db.Column(db.Float, nullable=False)
    acc_x = db.Column(db.Float, nullable=False)
    acc_y = db.Column(db.Float, nullable=False)
    acc_z = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    gps_alt = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "date": self.date,
            "time": self.time,
            "teensytime": self.teensytime,
            "record_sn": self.record_sn,
            "voltage": self.voltage,
            "current": self.current,
            "teensytemp": self.teensytemp,
            "nano_value1": self.nano_value1,
            "nano_value2": self.nano_value2,
            "nano_value3": self.nano_value3,
            "nano_value4": self.nano_value4,
            "valve_state": self.valve_state,
            "x_pos": self.x_pos,
            "y_pos": self.y_pos,
            "alt": self.alt,
            "eu_x": self.eu_x,
            "eu_y": self.eu_y,
            "eu_z": self.eu_z,
            "acc_x": self.acc_x,
            "acc_y": self.acc_y,
            "acc_z": self.acc_z,
            "lat": self.lat,
            "lon": self.lon,
            "gps_alt": self.gps_alt
        }

# Create the database and tables
with app.app_context():
    db.create_all()

# ========= Serial Communication =========

# Serial communication globals
ser = None
connection_status = "disconnected"
connection_message = "Not connected to any serial port"
latest_data = None

def close_serial():
    """Close the serial connection if open."""
    global ser, connection_status, connection_message
    if ser and ser.is_open:
        ser.close()
        ser = None
    connection_status = "disconnected"
    connection_message = "Serial connection closed"
    logger.info("Serial connection closed")

def send_data(data):
    """Send data to the serial port."""
    try:
        if ser and ser.is_open:
            ser.write(data.encode('utf-8'))
            logger.info(f"Sent: {data}")
            return True
        logger.warning("Cannot send data: Serial port not open")
        return False
    except serial.SerialException as e:
        logger.error(f"Error sending data: {e}")
        close_serial()
        return False

def connect_to_serial():
    """Attempt to connect to an available serial port."""
    global ser, connection_status, connection_message
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        connection_status = "retrying"
        connection_message = "No COM ports available"
        logger.warning("No COM ports available")
        return False
        
    for port in ports:
        try:
            ser = serial.Serial(port.device, 115200, timeout=1)
            connection_status = "connected"
            connection_message = f"Connected to {port.device}"
            logger.info(f"Connected to {port.device}")
            return True
        except serial.SerialException as e:
            logger.error(f"Error opening serial port {port.device}: {e}")
            if hasattr(e, 'errno') and e.errno == 13:
                logger.error("Permission denied. Try running as administrator.")
    
    connection_status = "retrying"
    connection_message = "Failed to connect to any available ports"
    return False

def filter_message(message):
    """Process incoming messages from the serial port."""
    global latest_data
    # Handle comma-separated format instead of JSON
    try:
        # Parse comma-separated values
        values = message.strip().split(',')
                   
        # Extract values from the message
        nano_value4 = int(values[5])  # This determines which table to use
        # Create record data with current timestamp
        date_time = datetime.now()
        # Updated record_data dictionary with all fields
        record_data = {
        'date': date_time.strftime('%Y-%m-%d'),
        'time': date_time.strftime('%H:%M:%S:%f')[:-3],
        'teensytime': values[1],
        'record_sn': values[0],
        'voltage': float(values[7]),
        'current': float(values[8]),
        'teensytemp': float(values[21]),
        'nano_value1': int(values[2]),
        'nano_value2': int(values[3]),
        'nano_value3': int(values[4]),
        'nano_value4': int(values[5]),
        'valve_state': values[6],
        'x_pos': float(values[9]),
        'y_pos': float(values[10]),
        'alt': float(values[11]),
        'eu_x': float(values[12]),
        'eu_y': float(values[13]),
        'eu_z': float(values[14]),
        'acc_x': float(values[15]),
        'acc_y': float(values[16]),
        'acc_z': float(values[17]),
        'lat': float(values[18]),
        'lon': float(values[19]),
        'gps_alt': float(values[20]),
        }
        
        # Update latest data for AJAX polling
        latest_data = record_data

        with app.app_context():
            # Choose table based on nanoValue4
            model = SensorData if nano_value4 == 0 else SensorData0
            new_record = model(**record_data)
            db.session.add(new_record)
            db.session.commit()

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        with app.app_context():
            db.session.rollback()

def serial_communication():
    """Main serial communication loop."""
    global ser, connection_status
    
    logger.info("Starting serial communication thread")
    
    while True:
        # If not connected, try to connect
        if ser is None:
            logger.info("Attempting to connect to serial port...")
            
            if not connect_to_serial():
                logger.warning(f"Connection status: {connection_status}, {connection_message}")
                time.sleep(5)  # Wait before retrying
                continue
                
            logger.info(f"Connection status: {connection_status}, {connection_message}")

        # Read from serial port
        try:
            if ser.in_waiting:
                raw_data = ser.readline()
                if raw_data:
                    # Process the data
                    message = raw_data.decode('utf-8', errors='ignore').strip()
                    # logger.debug(f"Received: {message}")
                    print(f"Received: {message}")
                    filter_message(message)
            else:
                # Small sleep to prevent CPU hogging when no data
                time.sleep(0.01)
                
        except UnicodeDecodeError:
            logger.error(f"Failed to decode data from serial port")
        except serial.SerialException as e:
            logger.error(f"Serial error: {e}")
            close_serial()
        except Exception as e:
            logger.error(f"Unexpected error in serial communication: {e}")
            close_serial()



# ========= Routes =========

@app.route('/loading')
def loading_screen():
    """Display a loading screen before launching the app."""
    return render_template('loading.html')

@app.route('/reset_loading')
def reset_loading():
    """Reset the loading screen flag (for testing)."""
    response = redirect('/loading')
    response.set_cookie('app_loaded', '', expires=0)
    return response

@app.route('/')
def index():
    """Render the main index page or redirect to loading screen on first visit."""
    # Check if this is first visit
    first_visit = request.cookies.get('app_loaded') != 'true'
    
    if first_visit:
        return redirect('/loading')
    
    logger.info(f"Index page accessed. Connection status: {connection_status}")
    return render_template('index.html')

@app.route('/visualize', methods=['GET'])
def visualize_data():
    """Render the data visualization page."""
    try:
        records = SensorData.query.order_by(SensorData.id.desc()).all()
        data = [record.to_dict() for record in records]
        return render_template('visualize.html', data=data)
    except Exception as e:
        logger.error(f"Error in visualize_data: {e}")
        return f"Error loading visualization: {str(e)}", 500

@app.route('/stream', methods=['GET'])
def stream_data():
    """Render the data streaming page."""
    try:
        records = SensorData.query.order_by(SensorData.id.desc()).all()
        data = [record.to_dict() for record in records]
        return render_template('stream.html', data=data)
    except Exception as e:
        logger.error(f"Error in stream_data: {e}")
        return f"Error loading stream page: {str(e)}", 500

@app.route('/latest_data', methods=['GET'])
def latest_data_route():
    """API endpoint to get the latest sensor data."""
    try:
        # Return the cached latest data if available
        if latest_data:
            return jsonify([latest_data]), 200
            
        # Otherwise retrieve from database
        records = SensorData.query.order_by(SensorData.id.desc()).limit(1).all()
        data = [record.to_dict() for record in records]
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error in latest_data: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/serial_status', methods=['GET'])
def serial_status():
    """API endpoint to get serial connection status."""
    return jsonify({
        'status': connection_status,
        'message': connection_message
    }), 200

@app.route('/start_serial', methods=['GET'])
def start_serial():
    """API endpoint to start serial connection."""
    if connection_status == "connected":
        return jsonify({"message": "Serial connection already running"}), 200
        
    result = connect_to_serial()
    return jsonify({
        'success': result,
        'status': connection_status,
        'message': connection_message
    }), 200
    
@app.route('/stop_serial', methods=['GET'])
def stop_serial():
    """API endpoint to stop serial connection."""
    close_serial()
    return jsonify({
        'success': True,
        'status': connection_status,
        'message': connection_message
    }), 200

@app.route('/video')
def video_feed():
    """Stream video from an IP camera."""
    ip_camera_url = "http://192.168.1.2:8080/video"
    
    try:
        response = requests.get(ip_camera_url, stream=True, timeout=5)
        if response.status_code != 200:
            logger.error(f"Error accessing camera: status code {response.status_code}")
            return f"Error: Unable to access the camera stream (status code {response.status_code})", 502
        
        boundary = response.headers.get('Content-Type', '').split('boundary=')[-1]
        if not boundary:
            logger.error("No boundary found in response headers")
            return "Error: Invalid video stream format", 502
            
        boundary = boundary.encode()
        logger.debug(f"Video boundary: {boundary.decode()}")
        
        def generate():
            buffer = b""
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    buffer += chunk
                    while True:
                        start = buffer.find(boundary)
                        if start == -1:
                            break
                        end = buffer.find(boundary, start + len(boundary))
                        if end == -1:
                            break
                        frame = buffer[start + len(boundary):end]
                        buffer = buffer[end:]
                        if frame:
                            header_end = frame.find(b'\r\n\r\n')
                            if header_end != -1:
                                frame = frame[header_end + 4:]
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            except Exception as e:
                logger.error(f"Error in video stream generator: {e}")
                yield b'--frame\r\nContent-Type: text/plain\r\n\r\nVideo stream error\r\n\r\n'
        
        return Response(generate(), content_type='multipart/x-mixed-replace; boundary=frame')
    
    except requests.RequestException as e:
        logger.error(f"Error connecting to camera: {e}")
        return f"Error: Unable to connect to camera: {e}", 502
    except Exception as e:
        logger.error(f"Unexpected error in video_feed: {e}")
        return f"Error: {str(e)}", 500


# ---------------------------------routes for database management---------------------------------
@app.route('/databases', methods=['GET'])
def list_databases():
    """API endpoint to list available database files."""
    db_files = get_available_databases()
    return jsonify({
        'current': current_database['filename'],
        'available': db_files
    }), 200

@app.route('/switch_database/<filename>', methods=['GET'])
def switch_database(filename):
    """API endpoint to switch to a different database file."""
    try:
        if filename not in get_available_databases():
            return jsonify({'success': False, 'message': f"Database {filename} not found"}), 404
            
        # Don't switch if it's already the current database
        if filename == current_database['filename']:
            return jsonify({'success': True, 'message': f"Already using {filename}"}), 200
            
        # Close existing connections
        db.session.remove()
        
        # Initialize the new database
        if initialize_database(filename):
            # Reinitialize SQLAlchemy with new database
            db.init_app(app)
            with app.app_context():
                # Verify database tables
                if not db.engine.has_table('sensor_data') or not db.engine.has_table('sensor_data0'):
                    logger.warning(f"Selected database may not have the required tables")
                
            return jsonify({
                'success': True, 
                'message': f"Switched to database: {filename}"
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': "Failed to switch database"
            }), 500
    except Exception as e:
        logger.error(f"Error switching database: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ========= Main Entry Point =========

if __name__ == '__main__':
    try:
        # Start the serial communication in a background thread
        serial_thread = threading.Thread(target=serial_communication, daemon=True)
        serial_thread.start()
        
        # Start the Flask server
        logger.info("Starting Flask server on port 5000")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        close_serial()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
