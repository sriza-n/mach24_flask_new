"""
Database management routes.
"""

import os
import logging
from flask import Blueprint, jsonify, send_file
from app.services.database_service import (
    get_available_databases, current_database, initialize_database,
    convert_database_to_xlsx, get_database_directory
)
from app import db

logger = logging.getLogger(__name__)

database_bp = Blueprint('database', __name__)


@database_bp.route('/databases', methods=['GET'])
def list_databases():
    """API endpoint to list available database files."""
    db_files = get_available_databases()
    return jsonify({
        'current': current_database['filename'],
        'available': db_files
    }), 200


@database_bp.route('/switch_database/<filename>', methods=['GET'])
def switch_database(filename):
    """API endpoint to switch to a different database file."""
    try:
        if filename not in get_available_databases():
            return jsonify({
                'success': False, 
                'message': f"Database {filename} not found"
            }), 404
            
        # Don't switch if it's already the current database
        if filename == current_database['filename']:
            return jsonify({
                'success': True, 
                'message': f"Already using database {filename}"
            }), 200
            
        # Close existing connections
        db.session.remove()
        
        # Initialize the new database
        from flask import current_app
        if initialize_database(current_app, filename):
            # Reinitialize SQLAlchemy with new database
            db.init_app(current_app)
            with current_app.app_context():
                db.create_all()
                
            return jsonify({
                'success': True, 
                'message': f"Switched to database {filename}"
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': f"Failed to switch to database {filename}"
            }), 500
    except Exception as e:
        logger.error(f"Error switching database: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@database_bp.route('/convert_db_to_xlsx/<filename>', methods=['GET'])
def convert_db_to_xlsx_route(filename):
    """API endpoint to convert a database file to XLSX and download it."""
    try:
        output, xlsx_filename = convert_database_to_xlsx(filename)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=xlsx_filename
        )
        
    except Exception as e:
        logger.error(f"Error converting database to XLSX: {e}")
        return jsonify({
            'success': False,
            'message': f'Error converting database: {str(e)}'
        }), 500


@database_bp.route('/delete_database/<filename>', methods=['DELETE'])
def delete_database(filename):
    """API endpoint to delete a database file by filename."""
    try:
        # Ensure filename ends with .db
        if not filename.endswith('.db'):
            filename += '.db'
        
        available_dbs = get_available_databases()
        if filename not in available_dbs:
            return jsonify({
                'success': False, 
                'message': f"Database {filename} not found"
            }), 404

        database_dir = get_database_directory()
        db_path = os.path.join(database_dir, filename)
        os.remove(db_path)
        logger.info(f"Deleted database file: {filename}")
        return jsonify({
            'success': True, 
            'message': f"Database {filename} deleted"
        }), 200
    except Exception as e:
        logger.error(f"Error deleting database: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
