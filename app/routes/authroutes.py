from flask import Blueprint
from app.controllers.auth import AuthController


class AuthRoutes:

    def __init__(self):

        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()

    def register(self):

        # HOME
        self.bp.route("/", methods=["GET", "POST"])(
            self.controller.home
        )

        self.bp.route("/home", methods=["GET", "POST"])(
            self.controller.home
        )

        # AUTH
        self.bp.route("/login", methods=["GET", "POST"])(
            self.controller.login
        )

        self.bp.route("/register", methods=["GET", "POST"])(
            self.controller.register
        )

        self.bp.route("/reset-password", methods=["GET", "POST"])(
            self.controller.password_reset
        )

        self.bp.route("/logout", methods=["GET"])(
            self.controller.logout
        )

        # ABOUT / CONTACT / FAQ
        self.bp.route("/about", methods=["GET"])(
            self.controller.about
        )

        self.bp.route("/contact", methods=["GET", "POST"])(
            self.controller.contact
        )

        self.bp.route("/faq", methods=["GET"])(
            self.controller.faq
        )

        # BROWSE + PROPERTY
        self.bp.route("/browse", methods=["GET"])(
            self.controller.browse
        )

        self.bp.route("/property/<int:prop_id>", methods=["GET"])(
            self.controller.property_detail
        )

        self.bp.route("/booking/confirm", methods=["GET"])(
            self.controller.booking_confirm
        )

        # DASHBOARDS
        self.bp.route("/dashboard/guest", methods=["GET"])(
            self.controller.guest_dashboard
        )

        self.bp.route("/dashboard/host", methods=["GET"])(
            self.controller.host_dashboard
        )

        # ADMIN
        self.bp.route("/admin", methods=["GET"])(
            self.controller.admin
        )

        return self.bp