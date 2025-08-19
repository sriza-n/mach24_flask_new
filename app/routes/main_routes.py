"""
Main application routes (pages and basic endpoints).
"""

import logging
from flask import Blueprint, render_template, jsonify, Response, request, redirect
from app.models import SensorData, SensorData0, SwitchState
from app.services.serial_service import get_connection_status, get_latest_data
import requests

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def loading_screen():
    """Display a loading screen before launching the app."""
    response = render_template('loading.html')
    # Clear any existing app state cookies
    response = render_template('loading.html')
    return response


@main_bp.route('/home')
def direct_home():
    """Direct access to home page after loading."""
    connection_status = get_connection_status()
    logger.info(f"Home page accessed. Connection status: {connection_status['status']}")
    return render_template('home.html')


@main_bp.route('/about')
def about():
    """Direct access to about page."""
    connection_status = get_connection_status()
    logger.info(f"About page accessed. Connection status: {connection_status['status']}")
    return render_template('about.html')


@main_bp.route('/page/database')
def database_page():
    """Render the database management page."""
    return render_template('database.html')


@main_bp.route('/page/home')
def home_page():
    return render_template('home.html')


@main_bp.route('/page/homescreen')
def home_screen():
    return render_template('homescreen.html')


@main_bp.route('/websocket')
def websocket_page():
    return render_template('websocket.html')


@main_bp.route('/page/dash1')
def dashboard_page():
    """Render the data visualization page."""
    try:
        # Get some recent data for the dashboard
        records = SensorData.query.order_by(SensorData.id.desc()).limit(10).all()
        return render_template('dash1.html', records=records)
    except Exception as e:
        logger.error(f"Error in dashboard_page: {e}")
        return render_template('dash1.html', records=[])
    

@main_bp.route('/page/dash2')
def groundtest_page():
    """Render the ground test page."""
    try:
        # Get some recent data for the dashboard
        records = SensorData.query.order_by(SensorData.id.desc()).limit(10).all()
        return render_template('dash2.html', records=records)
    except Exception as e:
        logger.error(f"Error in groundtest_page: {e}")
        return render_template('dash2.html', records=[])


@main_bp.route('/page/dash3', methods=['GET'])
def visualize_data():
    """Render the data visualization page."""
    try:
        # Get some recent data for visualization
        records = SensorData.query.order_by(SensorData.id.desc()).limit(100).all()
        return render_template('dash3.html', records=records)
    except Exception as e:
        logger.error(f"Error in visualize_data: {e}")
        return render_template('dash3.html', records=[])
    

@main_bp.route('/page/dash5', methods=['GET'])
def visualize_data2():
    """Render the data visualization page 2."""
    try:
        # Get some recent data for visualization
        records = SensorData.query.order_by(SensorData.id.desc()).limit(100).all()
        return render_template('dash5.html', records=records)
    except Exception as e:
        logger.error(f"Error in visualize_data2: {e}")
        return render_template('dash5.html', records=[])


@main_bp.route('/stream', methods=['GET'])
def stream_data():
    """Render the data streaming page."""
    try:
        # Get some recent data for streaming
        records = SensorData.query.order_by(SensorData.id.desc()).limit(50).all()
        return render_template('index.html', records=records)
    except Exception as e:
        logger.error(f"Error in stream_data: {e}")
        return render_template('index.html', records=[])


@main_bp.route('/video')
def video_feed():
    """Stream video from an IP camera."""
    ip_camera_url = "http://192.168.1.2:8080/video"
    
    try:
        response = requests.get(ip_camera_url, stream=True, timeout=5)
        if response.status_code != 200:
            logger.error(f"Camera returned status code: {response.status_code}")
            return "Camera not available", 503
        
        boundary = response.headers.get('Content-Type', '').split('boundary=')[-1]
        if not boundary:
            logger.error("No boundary found in camera response")
            return "Invalid camera stream format", 503
            
        boundary = boundary.encode()
        logger.debug(f"Video boundary: {boundary.decode()}")
        
        def generate():
            buffer = b""
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    buffer += chunk
                    while b'--' + boundary in buffer:
                        frame_end = buffer.find(b'--' + boundary)
                        if frame_end != -1:
                            frame = buffer[:frame_end]
                            buffer = buffer[frame_end + len(boundary) + 2:]
                            if b'\r\n\r\n' in frame:
                                image_start = frame.find(b'\r\n\r\n') + 4
                                if image_start < len(frame):
                                    yield (b'--frame\r\n'
                                           b'Content-Type: image/jpeg\r\n\r\n' + 
                                           frame[image_start:] + b'\r\n')
        
        return Response(generate(), content_type='multipart/x-mixed-replace; boundary=frame')
    
    except requests.RequestException as e:
        logger.error(f"Error connecting to camera: {e}")
        return "Camera connection failed", 503
    except Exception as e:
        logger.error(f"Unexpected error in video_feed: {e}")
        return "Internal server error", 500


@main_bp.after_request
def add_headers(response):
    """Add security and cache headers to all responses."""
    # Add cache control headers
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
