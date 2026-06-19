"""
============================================================
APPLICATION FACTORY - Bookmandu

Module: app/__init__.py

Purpose: Application factory pattern for creating and configuring
the Flask application instance.

This module follows the application factory pattern which allows
for better testing, configuration management, and multiple
application instances.

============================================================
"""

from flask import Flask  # Import Flask class for creating app instance
from app.routes.authroutes import AuthRoutes  # Import authentication routes blueprint
from app.models.database import Database  # Import Database class for table creation
import config  # Import configuration settings (SECRET_KEY, etc.)


def create_app():
    """
    Application factory function that creates and configures
    a Flask application instance.
    
    Purpose:
        Creates a new Flask app instance with configured settings,
        database initialization, and route registration.
    
    How it works:
        1. Initializes Flask app with static and template folders
        2. Sets the secret key from config
        3. Creates database tables within app context
        4. Registers authentication routes blueprint
    
    Returns:
        Flask: Configured Flask application instance
    
    Usage:
        app = create_app()
        if __name__ == '__main__':
            app.run(debug=True)
    """
    # ── Initialize Flask Application ──
    # Create Flask instance with custom static and template folder paths
    # static_folder='static': Location of static files (CSS, JS, images)
    # template_folder='templates': Location of HTML templates
    app = Flask(__name__, static_folder='static', template_folder='templates')
    # ── Set Secret Key ──
    # Used for session signing and CSRF protection
    # Retrieved from config.py file for security
    app.secret_key = config.SECRET_KEY
    # ── Initialize Database ──
    # Create database tables if they don't exist
    # Using app.app_context() ensures proper application context
    # before performing database operations
    with app.app_context():
        Database.create_tables()
    # ── Register Blueprints ──
    # Create auth routes instance and register its blueprint
    # auth_routes.register() returns a Blueprint object
    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.register())
    # ── Return Configured App ──
    # Return the fully configured application instance
    return app