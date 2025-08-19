"""
API routes for data and serial communication.
"""

import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from app import db
from app.models import SensorData, SensorData0, SwitchState
from app.services.serial_service import (
    get_connection_status, connect_to_serial, close_serial, 
    get_latest_data, get_origin_coordinates, set_origin_coordinates,
    update_latest_data
)
from app.utils.coordinates import xy_to_latlon

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


@api_bp.route('/latest_sw', methods=['GET'])
def latest_switch_state():
    """API endpoint to get the latest switch state data."""
    try:
        # Get the most recent switch state record
        latest_switch = SwitchState.query.order_by(SwitchState.id.desc()).first()
        
        if latest_switch:
            return jsonify([latest_switch.to_dict()]), 200
        else:
            return jsonify([]), 200
    except Exception as e:
        logger.error(f"Error in latest_switch_state: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/serial_status', methods=['GET'])
def serial_status():
    """API endpoint to get serial connection status."""
    status = get_connection_status()
    return jsonify(status), 200


@api_bp.route('/start_serial', methods=['GET'])
def start_serial():
    """API endpoint to start serial connection."""
    status = get_connection_status()
    if status['status'] == "connected":
        return jsonify({
            'success': True,
            'status': status['status'],
            'message': 'Already connected'
        }), 200
        
    result = connect_to_serial()
    status = get_connection_status()
    return jsonify({
        'success': result,
        'status': status['status'],
        'message': status['message']
    }), 200
    

@api_bp.route('/stop_serial', methods=['GET'])
def stop_serial():
    """API endpoint to stop serial connection."""
    close_serial()
    status = get_connection_status()
    return jsonify({
        'success': True,
        'status': status['status'],
        'message': status['message']
    }), 200


@api_bp.route('/add_data', methods=['POST'])
def add_data():
    """API endpoint to manually add sensor data to the database."""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        # Validate required fields - updated to match new database schema
        required_fields = [
            'teensytime', 'record_sn', 'voltage', 'current',
            'remote_st', 'valve_1', 'valve_2', 'activ_st', 'igni_st', 'para_st',
            'x_pos', 'y_pos', 'alt', 'eu_x', 'eu_y', 'eu_z',
            'acc', 'lat', 'lon', 'snr', 'rssi'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {missing_fields}'
            }), 400
        
        # Create record data with current timestamp if not provided
        current_time = datetime.now()

        origin_lat, origin_lon, origin_set = get_origin_coordinates()
        # Set origin coordinates only once (from first message)
        if not origin_set:
            set_origin_coordinates(float(data['lat']), float(data['lon']))
            origin_lat, origin_lon, origin_set = get_origin_coordinates()
            logger.info(f"Origin coordinates set: lat={origin_lat}, lon={origin_lon}")

        x_pos = float(data['x_pos'])
        y_pos = float(data['y_pos'])
        alt = float(data['alt'])
        imulat, imulon, fusedalt = xy_to_latlon(x_pos, y_pos, alt, origin_lat, origin_lon)
        
        # Fuse origin coordinates with IMU-calculated coordinates
        # Simple weighted average fusion (you can adjust weights as needed)
        weight_origin = 0.2  # Weight for origin coordinates
        weight_imu = 0.8    # Weight for IMU-calculated coordinates
        
        fused_lat = (float(data['lat']) * weight_origin) + (round(imulat, 6) * weight_imu)
        fused_lon = (float(data['lon']) * weight_origin) + (round(imulon, 6) * weight_imu)
 
        record_data = {
            'date': data.get('date', current_time.strftime('%Y-%m-%d')),
            'time': data.get('time', current_time.strftime('%H:%M:%S:%f')[:-3]),
            'teensytime': data['teensytime'],
            'record_sn': data['record_sn'],
            'voltage': float(data['voltage']),
            'current': float(data['current']),
            'remote_st': int(data['remote_st']),
            'valve_1': int(data['valve_1']),
            'valve_2': int(data['valve_2']),
            'activ_st': int(data['activ_st']),
            'igni_st': int(data['igni_st']),
            'para_st': int(data['para_st']),
            'x_pos': float(data['x_pos']),
            'y_pos': float(data['y_pos']),
            'alt': float(data['alt']),
            'eu_x': float(data['eu_x']),
            'eu_y': float(data['eu_y']),
            'eu_z': float(data['eu_z']),
            'acc': float(data['acc']),  # Changed from separate acc_x, acc_y, acc_z
            'lat': float(data['lat']),
            'lon': float(data['lon']),
            'fused_lat': fused_lat,
            'fused_lon': fused_lon,
            'rssi': float(data.get('rssi', 0.0)),  # Default to 0.0 if not provided
            'snr': float(data.get('snr', 0.0)),
            # New fields from updated database schema
            'p1': float(data.get('p1', 0.0)),
            'p2': float(data.get('p2', 0.0)),
            'load': float(data.get('load', 0.0)),
            'servo1_angle': int(data.get('servo1_angle', 0)),
            'servo2_angle': int(data.get('servo2_angle', 0)),
            'config_mode': int(data.get('config_mode', 0)),
            'test_mode': int(data.get('test_mode', 0)),
            'connection_state': int(data.get('connection_state', 0))
        }
        
        # Determine which table to use based on igni_st value (similar to serial logic)
        igni_st_value = int(data['igni_st'])
        model = SensorData if igni_st_value == 0 else SensorData0
        
        # Create and save the new record
        new_record = model(**record_data)
        db.session.add(new_record)
        
        # Also add to switch state table
        new_switch_state = SwitchState(**record_data)
        db.session.add(new_switch_state)
        
        db.session.commit()
        
        # Update latest data for real-time updates
        update_latest_data(record_data)
        
        # Emit new data to websocket clients
        from app import socketio
        socketio.emit('new_data', record_data)
        
        return jsonify({
            'success': True,
            'message': 'Data added successfully',
            'data': record_data
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Invalid data type: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding data: {e}")
        return jsonify({
            'success': False,
            'message': f'Database error: {str(e)}'
        }), 500
