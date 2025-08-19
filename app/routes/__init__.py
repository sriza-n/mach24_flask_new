"""
Route registration module.
"""

from .main_routes import main_bp
from .api_routes import api_bp
from .database_routes import database_bp


def register_routes(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(database_bp)
