"""
SocketIO event handlers.
"""

import logging
from flask import request
from .utils.error_handling import handle_connection_errors, ConnectionErrorHandler

logger = logging.getLogger(__name__)


def register_socketio_events(socketio):
    """Register SocketIO event handlers."""
    
    @socketio.on('connect')
    @handle_connection_errors
    def handle_connect():
        """Handle new WebSocket connections."""
        logger.info(f"Client connected: {request.sid}")
        with ConnectionErrorHandler("sending connection response"):
            socketio.emit('connection_response', {
                'success': True,
                'message': 'Connected to Mach24 server',
                'sid': request.sid
            })

    @socketio.on('disconnect')
    @handle_connection_errors
    def handle_disconnect():
        """Handle WebSocket disconnections."""
        logger.info(f"Client disconnected: {request.sid}")

    @socketio.on('get_sensor_data')
    @handle_connection_errors
    def handle_get_sensor_data():
        """Handle request for current sensor data."""
        try:
            from .services.database_service import get_latest_sensor_data
            data = get_latest_sensor_data()
            
            with ConnectionErrorHandler("sending sensor data"):
                socketio.emit('sensor_data', data)
                
        except Exception as e:
            logger.error(f"Error getting sensor data: {e}")
            with ConnectionErrorHandler("sending error response"):
                socketio.emit('error', {'message': 'Failed to get sensor data'})

    @socketio.on('start_data_stream')
    @handle_connection_errors
    def handle_start_data_stream():
        """Handle request to start data streaming."""
        logger.info("Data streaming started")
        with ConnectionErrorHandler("sending stream status"):
            socketio.emit('stream_status', {'status': 'started'})

    @socketio.on('stop_data_stream')
    @handle_connection_errors
    def handle_stop_data_stream():
        """Handle request to stop data streaming."""
        logger.info("Data streaming stopped")
        with ConnectionErrorHandler("sending stream status"):
            socketio.emit('stream_status', {'status': 'stopped'})