"""
Mach24 Flask Application Entry Point
A Flask-based web application for sensor data collection and visualization.

This is the main entry point that initializes and runs the application.
The application logic has been modularized into the following components:

- app/: Core application setup and initialization
- app/models.py: Database models
- app/routes/: Route handlers (main_routes, api_routes, database_routes)
- app/services/: Business logic (serial_service, database_service)
- app/utils/: Utility functions (coordinates, setup)
"""

# Critical: This must be the very first import and patch
import eventlet
eventlet.monkey_patch(all=True, thread=True, socket=True, os=True, select=True, time=True)

# Additional eventlet configuration for PyInstaller
import eventlet.hubs
eventlet.hubs.use_hub('selects')  # Use selects hub which works better in PyInstaller

# Suppress the eventlet RLock warning that can occur in PyInstaller builds
import warnings
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")
warnings.filterwarnings("ignore", category=UserWarning, module="eventlet")
warnings.filterwarnings("ignore", message=".*RLock.*")

import os
import threading
import logging

# Import application factory and services
from app import create_app, socketio
from app.services.database_service import (
    setup_database, initialize_database, current_database, 
    get_available_databases
)
from app.services.serial_service import (
    serial_communication, set_data_acquisition_mode, 
    get_data_acquisition_mode, close_serial
)
from app.utils.setup import (
    display_banner, setup_data_acquisition, display_setup_summary, 
    launch_browser
)

logger = logging.getLogger(__name__)


def run_initial_setup():
    """Run the complete initial setup process."""
    try:
        display_banner()
        
        # Setup data acquisition mode
        data_acquisition_mode = setup_data_acquisition()
        set_data_acquisition_mode(data_acquisition_mode)
        
        # Setup database
        selected_database = setup_database()
        
        # Create Flask app
        app = create_app()
        
        # Initialize database with selected option
        if not initialize_database(app, selected_database):
            print("❌ Failed to initialize database")
            return None, None
            
        display_setup_summary(data_acquisition_mode, selected_database, current_database)
        return app, data_acquisition_mode
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user.")
        return None, None
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return None, None


def setup_reloader_process():
    """Setup for Flask reloader process."""
    # Create Flask app
    app = create_app()
    
    # For reloader process, use the last known configuration
    # Initialize with a default database if none exists
    if not current_database['filename']:
        available_dbs = get_available_databases()
        if available_dbs:
            # Use the most recent database
            initialize_database(app, available_dbs[0])
            logger.info(f"Reloader: Using database {available_dbs[0]}")
        else:
            # Create a new database
            initialize_database(app)
            logger.info("Reloader: Created new database")
    
    return app


if __name__ == '__main__':
    try:
        # Only run setup if this is not a reloader process
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            # Run initial setup only on the main process
            app, data_acquisition_mode = run_initial_setup()
            if app is None:
                print("❌ Setup failed. Exiting...")
                exit(1)
        else:
            # For reloader process, use simplified setup
            app = setup_reloader_process()
            data_acquisition_mode = get_data_acquisition_mode()
        
        # Start serial thread only if in serial mode
        if data_acquisition_mode == "serial":
            serial_thread = threading.Thread(target=serial_communication, args=(app,), daemon=True)
            serial_thread.start()
            logger.info("Serial communication thread started")
        else:
            logger.info("Wireless mode selected - serial communication disabled")
        
        # Launch browser automatically (only on main process)
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            launch_browser()
        
        logger.info("Starting Flask-SocketIO server on port 5000 (eventlet)")
        # Disable reloader to prevent issues with global variables and database connections
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        close_serial()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
