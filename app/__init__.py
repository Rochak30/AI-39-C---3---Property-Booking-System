from flask import Flask
from app.routes.authroutes import AuthRoutes
# from app.models.database import Database


def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # # Initialize database tables
    # with app.app_context():
    #     Database.create_tables()

    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.register())

    return app