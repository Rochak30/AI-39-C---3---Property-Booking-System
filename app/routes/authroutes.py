from flask import Blueprint
from app.controllers.auth import AuthController
from app.auth import login_required, admin_required

class AuthRoutes:

    def __init__(self):
        self.bp         = Blueprint("auth", __name__)
        self.controller = AuthController()

    def register(self):
        # ── Public pages ──────────────────────────────────────
        self.bp.route("/",        endpoint="index")(self.controller.home)
        self.bp.route("/home",    methods=["GET", "POST"])(self.controller.home)
        self.bp.route("/about",   methods=["GET", "POST"])(self.controller.about)
        self.bp.route("/contact", methods=["GET", "POST"])(self.controller.contact)
        self.bp.route("/faq",     methods=["GET"])(self.controller.faq)
        self.bp.route("/chatbot", methods=["GET"])(self.controller.chatbot)
        # ── Auth ──────────────────────────────────────────────
        self.bp.route("/login",    methods=["GET", "POST"])(self.controller.login)
        self.bp.route("/register", methods=["GET", "POST"])(self.controller.register)
        self.bp.route("/logout",   methods=["GET"])(self.controller.logout)
        # ── Password reset ────────────────────────────────────
        self.bp.route("/forgot-password",  methods=["GET", "POST"])(self.controller.forgot_password)
        self.bp.route("/verify-code",      methods=["GET", "POST"])(self.controller.verify_code)
        self.bp.route("/reset-password",   methods=["GET", "POST"])(self.controller.reset_password)

        # ── Dashboard ──────────────────────────────────────────
        # /dashboard is a legacy redirect (old bookmarks/links) — it sends
        # the user to whichever of the three role-specific URLs below applies.
        self.bp.route("/dashboard", methods=["GET"])(self.controller.dashboard)
        self.bp.route("/admin/dashboard", methods=["GET", "POST"])(self.controller.admin_dashboard)
        self.bp.route("/host/dashboard",  methods=["GET", "POST"])(self.controller.host_dashboard)
        self.bp.route("/guest/dashboard", methods=["GET", "POST"])(self.controller.guest_dashboard)
        # ── Admin actions (POST only) ─────────────────────────
        self.bp.route("/admin/approve-host",       methods=["POST"])(self.controller.approve_host)
        self.bp.route("/admin/reject-host",        methods=["POST"])(self.controller.reject_host)
        self.bp.route("/admin/approve-property",   methods=["POST"])(self.controller.approve_property)
        self.bp.route("/admin/reject-property",    methods=["POST"])(self.controller.reject_property)
        self.bp.route("/admin/delete-user",        methods=["POST"])(self.controller.delete_user)
        self.bp.route("/admin/delete-property",    methods=["POST"])(self.controller.delete_property_admin)
        self.bp.route("/admin/resolve-query",      methods=["POST"])(self.controller.resolve_query)
        self.bp.route("/admin/view-as-user",       methods=["POST"])(self.controller.view_as_user)
        self.bp.route("/admin/exit-view-as",       methods=["GET"])(self.controller.exit_view_as)
        # ── Host actions ──────────────────────────────────────
        self.bp.route("/host/update-profile",  methods=["POST"])(self.controller.host_update_profile)
        self.bp.route("/host/delete-property", methods=["POST"])(self.controller.delete_property_host)
        # ── Guest actions ─────────────────────────────────────
        self.bp.route("/guest/update-profile", methods=["POST"])(self.controller.guest_update_profile)
        # ── Wishlist (AJAX) ───────────────────────────────────
        self.bp.route("/wishlist/toggle", methods=["POST"])(self.controller.toggle_wishlist)
        # ── Booking ──────────────────────────────────────────
        self.bp.route("/booking/create",        methods=["POST"])(self.controller.create_booking)
        self.bp.route("/booking/cancel",         methods=["POST"])(self.controller.cancel_booking)
        self.bp.route("/booking/cancel-review",  methods=["POST"])(self.controller.review_cancellation)
        self.bp.route("/booking/mark-complete",  methods=["POST"])(self.controller.mark_booking_complete)
        self.bp.route("/booking/confirm", methods=["POST"])(self.controller.confirm_booking)
        self.bp.route("/booking/reject",  methods=["POST"])(self.controller.reject_booking)
        # ── Browse ────────────────────────────────────────────
        self.bp.route("/browse", methods=["GET"])(self.controller.browse)
        # ── Property detail pages ─────────────────────────────
        self.bp.route("/property/mountain-view")(self.controller.property_mountain_view)
        self.bp.route("/property/thamel-heritage")(self.controller.property_thamel_heritage)
        self.bp.route("/property/jungle-retreat")(self.controller.property_jungle_retreat)
        self.bp.route("/property/lumbini-peace")(self.controller.property_lumbini_peace)
        self.bp.route("/property/mustang-desert")(self.controller.property_mustang_desert)
        self.bp.route("/property/lakeside-comfort")(self.controller.property_lakeside_comfort)
        # ── Add property ──────────────────────────────────────
        self.bp.route("/add-property",  methods=["GET", "POST"])(self.controller.add_property)
        # ── Misc ──────────────────────────────────────────────
        self.bp.route("/product_form",  methods=["GET", "POST"])(self.controller.product_form)
        return self.bp
    
    