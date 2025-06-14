import eventlet
eventlet.monkey_patch()
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
from flask_socketio import SocketIO


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'mach24_secret_key'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# # Define the absolute path to node_modules
# NODE_MODULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_modules')

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
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
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
    remote_st = db.Column(db.Integer, nullable=False)
    valve_1 = db.Column(db.Integer, nullable=False)
    valve_2 = db.Column(db.Integer, nullable=False)
    activ_st = db.Column(db.Integer, nullable=False)
    igni_st = db.Column(db.Integer, nullable=False)
    para_st = db.Column(db.String(20), nullable=False)
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
    fused_lat = db.Column(db.Float, nullable=False)
    fused_lon = db.Column(db.Float, nullable=False)
    rssi = db.Column(db.Float, nullable=False, default=0.0)  # RSSI value
    snr = db.Column(db.Float, nullable=False, default=0.0)   # SNR value
    # gps_alt = db.Column(db.Float, nullable=False)
    
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
            "remote_st": self.remote_st,
            "valve_1": self.valve_1,
            "valve_2": self.valve_2,
            "activ_st": self.activ_st,
            "igni_st": self.igni_st,
            "para_st": self.para_st,
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
            "fused_lat": self.fused_lat,
            "fused_lon": self.fused_lon,
            "rssi": self.rssi,
            "snr": self.snr,
            # "gps_alt": self.gps_alt
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
    remote_st = db.Column(db.Integer, nullable=False)
    valve_1 = db.Column(db.Integer, nullable=False)
    valve_2 = db.Column(db.Integer, nullable=False)
    activ_st = db.Column(db.Integer, nullable=False)
    igni_st = db.Column(db.Integer, nullable=False)
    para_st = db.Column(db.String(20), nullable=False)
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
    fused_lat = db.Column(db.Float, nullable=False)
    fused_lon = db.Column(db.Float, nullable=False)
    rssi = db.Column(db.Float, nullable=False, default=0.0)  # RSSI value
    snr = db.Column(db.Float, nullable=False, default=0.0)   # SNR value
    # gps_alt = db.Column(db.Float, nullable=False)
    
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
            "remote_st": self.remote_st,
            "valve_1": self.valve_1,
            "valve_2": self.valve_2,
            "activ_st": self.activ_st,
            "igni_st": self.igni_st,
            "para_st": self.para_st,
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
            "fused_lat": self.fused_lat,
            "fused_lon": self.fused_lon,
            "rssi": self.rssi,
            "snr": self.snr,
            # "gps_alt": self.gps_alt
        }

# store switch states

class SwitchState(db.Model):
    """Model for storing switch and valve state data."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    record_sn = db.Column(db.String(20), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    teensytemp = db.Column(db.Float, nullable=False)
    remote_st = db.Column(db.Integer, nullable=False)
    valve_1 = db.Column(db.Integer, nullable=False)
    valve_2 = db.Column(db.Integer, nullable=False)
    activ_st = db.Column(db.Integer, nullable=False)
    igni_st = db.Column(db.Integer, nullable=False)
    para_st = db.Column(db.String(20), nullable=False)
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
    fused_lat = db.Column(db.Float, nullable=False)
    fused_lon = db.Column(db.Float, nullable=False)
    rssi = db.Column(db.Float, nullable=False, default=0.0)  # RSSI value
    snr = db.Column(db.Float, nullable=False, default=0.0)   # SNR value
    
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
            "remote_st": self.remote_st,
            "valve_1": self.valve_1,
            "valve_2": self.valve_2,
            "activ_st": self.activ_st,
            "igni_st": self.igni_st,
            "para_st": self.para_st,
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
            "fused_lat": self.fused_lat,
            "fused_lon": self.fused_lon,
            "rssi": self.rssi,
            "snr": self.snr
        }

# Create the database and tables
with app.app_context():
    db.create_all()


# processing xy to latlong
# processing xy to latlong
from pyproj import Transformer, CRS

def xy_to_latlon(x_meters, y_meters, alt_meters, origin_lat, origin_lon):
    """
    Convert local X,Y coordinates (in meters) to lat/lon
    using a local tangent plane projection (transverse mercator)
    
    Parameters:
    -----------
    x_meters : float
        X coordinate in meters from origin
    y_meters : float
        Y coordinate in meters from origin
    alt_meters : float
        Altitude in meters above ground level
    origin_lat : float
        Latitude of the origin point
    origin_lon : float
        Longitude of the origin point
        
    Returns:
    --------
    tuple: (latitude, longitude, altitude)
        Converted WGS84 coordinates
    """
    # Create a transformer from local XY meters to WGS84 lat/lon
    transformer = Transformer.from_crs(
        # Local tangent plane centered at origin
        CRS.from_proj4(f"+proj=tmerc +lat_0={origin_lat} +lon_0={origin_lon} +k=1 +x_0=0 +y_0=0"),
        CRS.from_epsg(4326),  # Used by Google Maps, OpenStreetMap, and other web mapping services
        always_xy=True
    )
    
    # Transform the coordinates including altitude
    lon, lat, alt = transformer.transform(x_meters, y_meters, alt_meters)
    return lat, lon, alt

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

origin_lat = None
origin_lon = None
origin_set = False

def filter_message(message):
    """Process incoming messages from the serial port."""
    global latest_data
    global origin_lat, origin_lon, origin_set
    # Handle comma-separated format instead of JSON
    try:
        # Parse comma-separated values
        values = message.strip().split(',')
                   
        # Extract values from the message
        nano_value4 = int(values[6])  # This determines which table to use
        # Create record data with current timestamp
        date_time = datetime.now()

        # Set origin coordinates only once (from first message)
        if not origin_set:
            origin_lat = float(values[19])  # Store first origin latitude
            origin_lon = float(values[20])  # Store first origin longitude
            origin_set = True
            # logger.info(f"Origin coordinates set: lat={origin_lat}, lon={origin_lon}")

        x_pos = float(values[10])
        y_pos = float(values[11])
        alt = float(values[12])
        imulat, imulon ,fusedalt = xy_to_latlon(x_pos, y_pos, alt, origin_lat, origin_lon)
        # Updated record_data dictionary with all fields
                # Fuse origin coordinates with IMU-calculated coordinates
        # Simple weighted average fusion (you can adjust weights as needed)
        weight_origin = 0.2  # Weight for origin coordinates
        weight_imu = 0.8    # Weight for IMU-calculated coordinates
        
        fused_lat = (float(values[19]) * weight_origin) + (round(imulat,6) * weight_imu)
        fused_lon = (float(values[20]) * weight_origin) + (round(imulon,6) * weight_imu)
        # print(f"Fused coordinates: lat={fused_lat}, lon={fused_lon}")
        # Add RSSI and SNR, set to 0 if not available
        rssi = 0
        snr = 0
        if len(values) > 22:
            try:
                rssi = float(values[22])
            except Exception:
                rssi = 0
        if len(values) > 23:
            try:
                snr = float(values[23])
            except Exception:
                snr = 0

        record_data = {
        'date': date_time.strftime('%Y-%m-%d'),
        'time': date_time.strftime('%H:%M:%S:%f')[:-3],
        'teensytime': values[1],
        'record_sn': values[0],
        'voltage': float(values[9]),
        'current': float(values[8]),
        'teensytemp': float(values[21]),
        'remote_st': values[2],
        'valve_1': int(values[3]),
        'valve_2': int(values[4]),
        'activ_st': int(values[5]),
        'igni_st': int(values[6]),
        'para_st': values[7],
        'x_pos': float(values[10]),
        'y_pos': float(values[11]),
        'alt': float(values[12]),
        'eu_x': float(values[13]),
        'eu_y': float(values[14]),
        'eu_z': float(values[15]),
        'acc_x': float(values[16]),
        'acc_y': float(values[17]),
        'acc_z': float(values[18]),
        'lat': float(values[19]),
        'lon': float(values[20]),
        # 'fused_lat':round(imulat,6),
        # 'fused_lon': round(imulon,6),
        'fused_lat':fused_lat,
        'fused_lon': fused_lon,
        'rssi': rssi,
        'snr': snr,
        # 'gps_alt': float(values[20]),
        }
   
        # Update latest data for AJAX polling
        latest_data = record_data

        # Emit new data to all websocket clients
        socketio.emit('new_data', record_data)

        with app.app_context():
            # Choose table based on nanoValue4
            model = SensorData if nano_value4 == 0 else SensorData0
            new_record = model(**record_data)
            db.session.add(new_record)

            # Store switch state data separately
            new_switch_state = SwitchState(**record_data)
            db.session.add(new_switch_state)
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
    return render_template('homescreen.html')

@app.route('/page/home')
def home_page():
    return render_template('home.html')

@app.route('/page/homescreen')
def home_screen():
    return render_template('homescreen.html')

@app.route('/websocket')
def websocket_page():
    return render_template('websocket.html')


@app.route('/test_emit')
def test_emit():
    """Emit a test message to all websocket clients."""
    record_data = {
        "date": "2025-06-02",
        "time": "17:09:00",
        "teensytime": "123456",
        "record_sn": "1",
        "voltage": 3.3,
        "current": 0.1,
        "teensytemp": 25.0,
        "remote_st": 1,
        "valve_1": 0,
        "valve_2": 0,
        "activ_st": 1,
        "igni_st": 0,
        "para_st": "A",
        "x_pos": 10.0,
        "y_pos": 20.0,
        "alt": 100.0,
        "eu_x": 0.0,
        "eu_y": 0.0,
        "eu_z": 0.0,
        "acc_x": 0.0,
        "acc_y": 0.0,
        "acc_z": 0.0,
        "lat": 40.0,
        "lon": -74.0,
        "fused_lat": 40.0,
        "fused_lon": -74.0
    }
    socketio.emit('new_data', record_data)
    return "Test data emitted!", 200


@app.route('/page/dash1')
def dashboard_page():
    """Render the data visualization page."""
    try:
        records = SensorData.query.order_by(SensorData.id.desc()).all()
        data = [record.to_dict() for record in records]
        return render_template('dash1.html', data=data)
    except Exception as e:
        logger.error(f"Error in visualize_data: {e}")
        return f"Error loading visualization: {str(e)}", 500
    
@app.route('/page/dash2')
def settings_page():
    return render_template('dash2.html')

@app.route('/page/dash3', methods=['GET'])
def visualize_data():
    """Render the data visualization page."""
    try:
        records = SensorData.query.order_by(SensorData.id.desc()).all()
        data = [record.to_dict() for record in records]
        return render_template('dash3.html', data=data)
    except Exception as e:
        logger.error(f"Error in visualize_data: {e}")
        return f"Error loading visualization: {str(e)}", 500
    
@app.route('/page/dash5', methods=['GET'])
def visualize_data2():
    """Render the data visualization page."""
    try:
        records = SensorData.query.order_by(SensorData.id.desc()).all()
        data = [record.to_dict() for record in records]
        return render_template('dash5.html', data=data)
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

@app.route('/latest_sw', methods=['GET'])
def latest_switch_state():
    """API endpoint to get the latest switch state data."""
    try:
        # Query the most recent switch state record
        latest_switch = SwitchState.query.order_by(SwitchState.id.desc()).limit(1).first()
        
        if latest_switch:
            return jsonify(latest_switch.to_dict()), 200
        else:
            # If no switch state records exist yet
            return jsonify({"message": "No switch state data available"}), 404
    except Exception as e:
        logger.error(f"Error in latest_switch_state: {e}")
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
    

@app.after_request
def add_headers(response):
    """Add security and cache headers to all responses."""
    # Add cache control headers
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# ========= Main Entry Point =========

if __name__ == '__main__':
    try:
        serial_thread = threading.Thread(target=serial_communication, daemon=True)
        serial_thread.start()
        logger.info("Starting Flask-SocketIO server on port 5000 (eventlet)")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        close_serial()
    except Exception as e:
        logger.error(f"Error starting server: {e}")