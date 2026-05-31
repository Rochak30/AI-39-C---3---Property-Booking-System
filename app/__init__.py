from flask import Flask
from app.routes.authroutes import AuthRoutes
from app.models.database import Database
import config

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.secret_key = config.SECRET_KEY

    with app.app_context():
        Database.create_tables()

    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.register())
    return app


