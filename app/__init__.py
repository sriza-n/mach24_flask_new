"""
Mach24 Flask Application Package
Core application initialization and setup.
"""

# Import standard library modules
import os
import logging

# Import third-party modules
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    """Create and configure the Flask application."""
    # Specify the correct template and static folders relative to the project root
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(project_root, 'templates')
    static_folder = os.path.join(project_root, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Basic app configuration
    app.config['SECRET_KEY'] = 'mach24_secret_key'
    
    # Set default SQLAlchemy configuration to suppress warnings
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Temporary, will be overridden
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure logging to reduce noise from connection errors
    logging.getLogger('eventlet.wsgi').setLevel(logging.ERROR)
    logging.getLogger('eventlet').setLevel(logging.ERROR)
    
    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
    
    # Register error handlers
    @app.errorhandler(ConnectionAbortedError)
    def handle_connection_aborted(e):
        logger.debug(f"Connection aborted: {e}")
        return "", 503
    
    @app.errorhandler(ConnectionResetError)
    def handle_connection_reset(e):
        logger.debug(f"Connection reset: {e}")
        return "", 503
    
    @app.errorhandler(BrokenPipeError)
    def handle_broken_pipe(e):
        logger.debug(f"Broken pipe: {e}")
        return "", 503
    
    # Register blueprints
    from .routes import register_routes
    register_routes(app)
    
    # Register SocketIO events
    from .socketio_events import register_socketio_events
    register_socketio_events(socketio)
    
    return app
