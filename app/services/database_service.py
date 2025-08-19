"""
Database management service.
"""

import os
import sqlite3
import logging
from datetime import datetime
from app import db

logger = logging.getLogger(__name__)

# Store current database info for reference
current_database = {
    'filename': None,
    'path': None
}


def get_database_directory():
    """Get the database directory path."""
    # Go up two levels from app/services to get to the project root, then to database
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database')


def ensure_database_directory():
    """Create database directory if it doesn't exist."""
    database_dir = get_database_directory()
    if not os.path.exists(database_dir):
        os.makedirs(database_dir, exist_ok=True)
    return database_dir


def get_available_databases():
    """List all available database files in the database directory."""
    try:
        database_dir = get_database_directory()
        db_files = [f for f in os.listdir(database_dir) if f.endswith('.db')]
        db_files.sort(reverse=True)  # Most recent first
        return db_files
    except Exception as e:
        logger.error(f"Error listing database files: {e}")
        return []


def initialize_database(app, db_filename=None):
    """Initialize database connection with specified file or create new one."""
    global current_database
    
    database_dir = ensure_database_directory()
    
    if db_filename:
        # Use specified database file
        database_path = os.path.join(database_dir, db_filename)
        
        # Check if it's an existing database or if we're creating a new one
        if os.path.exists(database_path):
            logger.info(f"Using existing database: {db_filename}")
        else:
            logger.info(f"Creating new database: {db_filename}")
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
    
    # Create all tables after configuring the database URI
    with app.app_context():
        db.create_all()
        logger.info(f"Database tables created/verified for: {db_filename}")
    
    return True


def setup_database():
    """Setup database selection or creation."""
    print("\n" + "=" * 60)
    print("DATABASE SELECTION")
    print("=" * 60)
    
    # Get available databases
    available_dbs = get_available_databases()
    
    print("Available options:")
    print("1. Create new database")
    
    if available_dbs:
        print("2. Use existing database")
        print("\nExisting databases:")
        for i, db_file in enumerate(available_dbs, 1):
            # Extract date/time info from filename for better display
            if 'sensor_data_' in db_file:
                timestamp_part = db_file.replace('sensor_data_', '').replace('.db', '')
                try:
                    # Parse timestamp: YYYYMMDD_HHMMSS
                    if '_' in timestamp_part:
                        date_part, time_part = timestamp_part.split('_')
                        formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                        formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                        display_name = f"{formatted_date} {formatted_time}"
                    else:
                        display_name = timestamp_part
                except:
                    display_name = timestamp_part
            else:
                display_name = db_file.replace('.db', '')
            
            print(f"   {i}. {db_file} ({display_name})")
    
    print("-" * 60)
    
    while True:
        try:
            if available_dbs:
                choice = input("Select option (1 for new, 2 for existing): ").strip()
            else:
                choice = input("No existing databases found. Press Enter to create new database: ").strip()
                if choice == "":
                    choice = "1"
            
            if choice == "1":
                # Create new database
                while True:
                    db_name = input("Enter database name (or press Enter for auto-generated): ").strip()
                    if db_name == "":
                        # Auto-generate with timestamp - no need to set filename here
                        print(f"✓ Will create auto-generated database")
                        return None  # This will trigger auto-generation
                    else:
                        # User provided name
                        if not db_name.endswith('.db'):
                            db_name += '.db'
                        db_filename = db_name
                        
                        # Check if it already exists
                        if db_filename in available_dbs:
                            print(f"❌ Database {db_filename} already exists. Choose a different name.")
                        else:
                            print(f"✓ Will create database: {db_filename}")
                            return db_filename
                
            elif choice == "2" and available_dbs:
                # Use existing database
                print("\nSelect existing database:")
                for i, db_file in enumerate(available_dbs, 1):
                    print(f"{i}. {db_file}")
                
                while True:
                    try:
                        db_choice = int(input(f"Enter database number (1-{len(available_dbs)}): ").strip())
                        if 1 <= db_choice <= len(available_dbs):
                            selected_db = available_dbs[db_choice - 1]
                            print(f"✓ Selected database: {selected_db}")
                            return selected_db
                        else:
                            print(f"❌ Invalid choice. Please enter a number between 1 and {len(available_dbs)}.")
                    except ValueError:
                        print("❌ Invalid input. Please enter a number.")
                    except KeyboardInterrupt:
                        print("\n❌ Setup cancelled by user.")
                        exit(1)
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user.")
            exit(1)
        except Exception as e:
            print(f"❌ Error: {e}. Please try again.")


def convert_database_to_xlsx(filename):
    """Convert a database file to XLSX format."""
    # Import pandas only when needed to avoid conflicts with eventlet
    import pandas as pd
    from io import BytesIO
    
    database_dir = get_database_directory()
    
    # Validate filename
    if not filename.endswith('.db'):
        filename += '.db'
    
    available_dbs = get_available_databases()
    if filename not in available_dbs:
        raise FileNotFoundError(f"Database {filename} not found")
    
    # Construct database path
    db_path = os.path.join(database_dir, filename)
    
    # Connect to the specific database file
    conn = sqlite3.connect(db_path)
    
    # Create a BytesIO object to store Excel file in memory
    output = BytesIO()
    
    # List of tables to export
    tables = ['sensor_data', 'sensor_data0', 'switch_state']
    
    # Create Excel writer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for table in tables:
            try:
                # Read table data
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                if not df.empty:
                    # Write to Excel sheet
                    df.to_excel(writer, sheet_name=table, index=False)
                    logger.info(f"Exported {len(df)} records from table '{table}'")
                else:
                    logger.info(f"Table '{table}' is empty, skipping...")
            except Exception as e:
                logger.warning(f"Could not export table '{table}': {e}")
    
    # Close database connection
    conn.close()
    
    # Prepare the file for download
    output.seek(0)
    
    return output, filename.replace('.db', '.xlsx')
