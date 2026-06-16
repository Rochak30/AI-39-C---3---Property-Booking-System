from flask import Blueprint
 
from app.controllers.auth import AuthController
from app.auth import login_required, admin_required
 
class AuthRoutes:
 
    def __init__(self):
 
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()
 
    def register(self):
        self.bp.route("/", endpoint="index")(self.controller.login)
        
        self.bp.route("/browse", methods=["GET"])(self.controller.browse)

        self.bp.route("/property/mountain-view")(self.controller.property_mountain_view)

        self.bp.route("/property/thamel-heritage")(self.controller.property_thamel_heritage)
        
        self.bp.route("/property/jungle-retreat")(self.controller.property_jungle_retreat)

        self.bp.route("/property/lumbini-peace")(self.controller.property_lumbini_peace)

        self.bp.route("/property/mustang-desert")(self.controller.property_mustang_desert)

        self.bp.route("/property/lakeside-comfort")(self.controller.property_lakeside_comfort)
        
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

        self.bp.route("/verify-code", methods=["GET", "POST"])(self.controller.verify_code)

        self.bp.route("/reset-password", methods=["GET", "POST"])(self.controller.reset_password)

        # ========== ADD PROPERTY ROUTE ==========
        self.bp.route("/add-property", methods=["GET", "POST"])(self.controller.add_property)

        return self.bp