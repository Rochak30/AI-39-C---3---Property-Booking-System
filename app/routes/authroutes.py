
from flask import Blueprint
 
from app.controllers.auth import AuthController
from app.auth import login_required, admin_required
 
class AuthRoutes:
 
    def __init__(self):
 
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()
 
    def register(self):
        self.bp.route("/", endpoint="index")(self.controller.login)
 
        self.bp.route("/login", methods=["GET", "POST"])(self.controller.login)
 
        self.bp.route("/register", methods=["GET", "POST"])(self.controller.register)
 
        self.bp.route("/about", methods=["GET", "POST"])(self.controller.about)
 
        self.bp.route("/contact", methods=["GET", "POST"])(self.controller.contact)
 
        self.bp.route("/home", methods=["GET", "POST"])(self.controller.home)
 
        self.bp.route("/product_form", methods=["GET", "POST"])(self.controller.product_form)
 
        self.bp.route("/logout", methods=["GET"])(self.controller.logout)
 
        self.bp.route("/dashboard", methods=["GET", "POST"])(self.controller.dashboard)

        self.bp.route("/faq", methods=["GET"])(self.controller.faq)
        
        self.bp.route("/forgot-password", methods=["GET", "POST"])(self.controller.forgot_password)
 
        return self.bp