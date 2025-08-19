"""
Enhanced error handling and connection management utilities.
"""

import logging
import functools
from flask import jsonify

logger = logging.getLogger(__name__)


def handle_connection_errors(func):
    """Decorator to handle common connection errors gracefully."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionAbortedError as e:
            logger.warning(f"Connection aborted: {e}")
            return jsonify({"error": "Connection was aborted"}), 503
        except ConnectionResetError as e:
            logger.warning(f"Connection reset: {e}")
            return jsonify({"error": "Connection was reset"}), 503
        except BrokenPipeError as e:
            logger.warning(f"Broken pipe: {e}")
            return jsonify({"error": "Connection pipe broken"}), 503
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return jsonify({"error": "Internal server error"}), 500
    return wrapper


def suppress_eventlet_warnings():
    """Suppress common eventlet warnings and connection errors."""
    import warnings
    
    # Suppress eventlet connection warnings
    warnings.filterwarnings("ignore", message=".*Connection.*aborted.*")
    warnings.filterwarnings("ignore", message=".*WinError 10053.*")
    warnings.filterwarnings("ignore", message=".*Broken pipe.*")
    warnings.filterwarnings("ignore", category=ConnectionAbortedError)
    warnings.filterwarnings("ignore", category=ConnectionResetError)
    warnings.filterwarnings("ignore", category=BrokenPipeError)


class ConnectionErrorHandler:
    """Context manager for handling connection errors."""
    
    def __init__(self, operation_name="operation"):
        self.operation_name = operation_name
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type in (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            logger.debug(f"Connection error during {self.operation_name}: {exc_val}")
            return True  # Suppress the exception
        elif exc_type is not None:
            logger.error(f"Unexpected error during {self.operation_name}: {exc_val}")
        return False
