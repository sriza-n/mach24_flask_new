"""
Serial communication service.
"""

import serial
import serial.tools.list_ports
import time
import logging
from datetime import datetime
from app import db, socketio
from app.models import SensorData, SensorData0, SwitchState
from app.utils.coordinates import xy_to_latlon

logger = logging.getLogger(__name__)

# Serial communication globals
ser = None
connection_status = "disconnected"
connection_message = "Not connected to any serial port"
latest_data = None
data_acquisition_mode = "serial"  # "serial" or "wireless"

# Global origin coordinates
origin_lat = None
origin_lon = None
origin_set = False


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
            ser.write(data.encode())
            logger.info(f"Data sent: {data}")
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
    
    # Close existing connection if any
    if ser and ser.is_open:
        ser.close()
        ser = None
    
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        connection_status = "retrying"
        connection_message = "No COM ports available"
        logger.warning("No COM ports available")
        return False
        
    for port in ports:
        try:
            logger.info(f"Trying to connect to {port.device}")
            ser = serial.Serial(port.device, 115200, timeout=1)
            connection_status = "connected"
            connection_message = f"Connected to {port.device}"
            logger.info(f"Successfully connected to {port.device}")
            return True
        except serial.SerialException as e:
            logger.warning(f"Failed to connect to {port.device}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to {port.device}: {e}")
    
    connection_status = "retrying"
    connection_message = "Failed to connect to any available ports"
    return False


def filter_message(message, app):
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
            origin_lat = float(values[17])
            origin_lon = float(values[18])
            origin_set = True
            logger.info(f"Origin coordinates set: lat={origin_lat}, lon={origin_lon}")

        x_pos = float(values[10])
        y_pos = float(values[11])
        alt = float(values[12])
        imulat, imulon, fusedalt = xy_to_latlon(x_pos, y_pos, alt, origin_lat, origin_lon)
        
        # Fuse origin coordinates with IMU-calculated coordinates
        # Simple weighted average fusion (you can adjust weights as needed)
        weight_origin = 0.2  # Weight for origin coordinates
        weight_imu = 0.8    # Weight for IMU-calculated coordinates
        
        fused_lat = (float(values[17]) * weight_origin) + (round(imulat, 6) * weight_imu)
        fused_lon = (float(values[18]) * weight_origin) + (round(imulon, 6) * weight_imu)

        record_data = {
            'date': date_time.strftime('%Y-%m-%d'),
            'time': date_time.strftime('%H:%M:%S:%f')[:-3],
            'teensytime': values[1],
            'record_sn': values[0],
            'voltage': float(values[9]),
            'current': float(values[8]),
            'remote_st': int(values[2]),
            'valve_1': int(values[3]),
            'valve_2': int(values[4]),
            'activ_st': int(values[5]),
            'igni_st': int(values[6]),
            'para_st': int(values[7]),
            'x_pos': float(values[10]),
            'y_pos': float(values[11]),
            'alt': float(values[12]),
            'eu_x': float(values[13]),
            'eu_y': float(values[14]),
            'eu_z': float(values[15]),
            'acc': float(values[16]),
            'lat': float(values[17]),
            'lon': float(values[18]),
            'fused_lat': fused_lat,
            'fused_lon': fused_lon,
            'rssi': float(values[19]),
            'snr': float(values[20]),
            'p1': float(values[21]),
            'p2': float(values[22]), 
            'load': float(values[23]),    
            'servo1_angle': int(values[24]), 
            'servo2_angle': int(values[25]), 
            'config_mode': int(values[26]), 
            'test_mode': int(values[27]),  
            'connection_state': int(values[28]),
        }
   
        # Update latest data for AJAX polling
        latest_data = record_data

        # Emit new data to all websocket clients
        socketio.emit('new_data', record_data)

        with app.app_context():
            try:
                # Determine which table to use based on igni_st value
                model = SensorData if nano_value4 == 0 else SensorData0
                
                # Create and save the record
                new_record = model(**record_data)
                db.session.add(new_record)
                
                # Also add to switch state table
                new_switch_state = SwitchState(**record_data)
                db.session.add(new_switch_state)
                
                db.session.commit()
                
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
                db.session.rollback()
                
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        with app.app_context():
            db.session.rollback()


def serial_communication(app):
    """Main serial communication loop."""
    global ser, connection_status
    
    # Only run serial communication if mode is set to serial
    if data_acquisition_mode != "serial":
        logger.info(f"Data acquisition mode is set to '{data_acquisition_mode}'. Serial communication disabled.")
        return
    
    logger.info("Starting serial communication thread")
    
    while True:
        # If not connected, try to connect
        if ser is None or not ser.is_open:
            if not connect_to_serial():
                time.sleep(2)  # Wait before retrying
                continue

        # Read from serial port
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    filter_message(line, app)
                
        except UnicodeDecodeError:
            logger.warning("Failed to decode serial data as UTF-8")
        except serial.SerialException as e:
            logger.error(f"Serial communication error: {e}")
            close_serial()
            time.sleep(2)
        except Exception as e:
            logger.error(f"Unexpected error in serial communication: {e}")
            time.sleep(1)


def get_connection_status():
    """Get current serial connection status."""
    return {
        'status': connection_status,
        'message': connection_message
    }


def get_latest_data():
    """Get the latest sensor data."""
    return latest_data


def set_data_acquisition_mode(mode):
    """Set the data acquisition mode."""
    global data_acquisition_mode
    data_acquisition_mode = mode
    logger.info(f"Data acquisition mode set to: {mode}")


def get_data_acquisition_mode():
    """Get the current data acquisition mode."""
    return data_acquisition_mode


def get_origin_coordinates():
    """Get the origin coordinates."""
    global origin_lat, origin_lon, origin_set
    return origin_lat, origin_lon, origin_set


def set_origin_coordinates(lat, lon):
    """Set the origin coordinates."""
    global origin_lat, origin_lon, origin_set
    origin_lat = lat
    origin_lon = lon
    origin_set = True


def update_latest_data(data):
    """Update the latest data."""
    global latest_data
    latest_data = data
