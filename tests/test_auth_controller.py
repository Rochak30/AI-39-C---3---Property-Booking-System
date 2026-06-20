"""
=============================================================
  Pahuna — AuthController Unit Tests
=============================================================
  OOP Concepts demonstrated:
    - Inheritance: AuthController inherits from BaseController;
      tests verify inherited helpers work correctly.
    - Encapsulation: password is private in User model; tests
      confirm outside code cannot read it but check_password works.
    - Polymorphism: role_required decorator behaves differently
      based on the role stored in session.

  Run with:
      python -m pytest tests/test_auth_controller.py -v
  or:
      python -m unittest tests/test_auth_controller.py
=============================================================
"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from flask import Flask, Blueprint, session, get_flashed_messages
from app.controllers.auth import AuthController


# ─────────────────────────────────────────────────────────────────────────────
#  TEST APP FACTORY
#  Builds a minimal Flask app with every endpoint the controller redirects to,
#  so url_for() inside the controller never raises BuildError.
# ─────────────────────────────────────────────────────────────────────────────

def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    bp = Blueprint("auth", __name__)

    # Every endpoint the controller uses url_for() on must be registered.
    bp.route("/",                    endpoint="index")(lambda: "home")
    bp.route("/home",                endpoint="home")(lambda: "home")
    bp.route("/login",               endpoint="login")(lambda: "login")
    bp.route("/register",            endpoint="register")(lambda: "register")
    bp.route("/logout",              endpoint="logout")(lambda: "logout")
    bp.route("/dashboard",           endpoint="dashboard")(lambda: "dashboard")
    bp.route("/admin/dashboard",     endpoint="admin_dashboard")(lambda: "admin")
    bp.route("/host/dashboard",      endpoint="host_dashboard")(lambda: "host")
    bp.route("/guest/dashboard",     endpoint="guest_dashboard")(lambda: "guest")
    bp.route("/browse",              endpoint="browse")(lambda: "browse")
    bp.route("/contact",             endpoint="contact")(lambda: "contact")
    bp.route("/forgot-password",     endpoint="forgot_password")(lambda: "forgot")
    bp.route("/review/create",       endpoint="create_review")(lambda: "review")

    app.register_blueprint(bp)
    return app


# ─────────────────────────────────────────────────────────────────────────────
#  BASE CONTROLLER TESTS
#  Verifies the parent-class helpers that every controller inherits.
# ─────────────────────────────────────────────────────────────────────────────

class TestBaseController(unittest.TestCase):
    """
    OOP focus: Inheritance.
    AuthController inherits get_form_data, is_logged_in, etc. from BaseController.
    These tests confirm the inherited methods work correctly through the child class.
    """

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_is_logged_in_returns_false_when_no_session(self):
        """is_logged_in() returns False when user_id is not in session."""
        with self.app.test_request_context():
            self.assertFalse(self.controller.is_logged_in())

    def test_is_logged_in_returns_true_when_session_set(self):
        """is_logged_in() returns True once user_id is stored in session."""
        with self.app.test_request_context():
            session["user_id"] = 1
            self.assertTrue(self.controller.is_logged_in())

    def test_get_current_user_id_returns_none_when_not_logged_in(self):
        """get_current_user_id() returns None when no one is logged in."""
        with self.app.test_request_context():
            self.assertIsNone(self.controller.get_current_user_id())

    def test_get_current_user_id_returns_correct_id(self):
        """get_current_user_id() returns the ID stored in session."""
        with self.app.test_request_context():
            session["user_id"] = 42
            self.assertEqual(self.controller.get_current_user_id(), 42)

    def test_get_current_role_returns_none_when_not_logged_in(self):
        """get_current_role() returns None when session has no role."""
        with self.app.test_request_context():
            self.assertIsNone(self.controller.get_current_role())

    def test_get_current_role_returns_correct_role(self):
        """get_current_role() returns the role from session."""
        with self.app.test_request_context():
            session["role"] = "admin"
            self.assertEqual(self.controller.get_current_role(), "admin")

    def test_get_form_data_strips_whitespace(self):
        """get_form_data() trims leading/trailing spaces from form inputs."""
        with self.app.test_request_context(
            method="POST",
            data={"name": "  Alice  ", "email": " alice@example.com "}
        ):
            name, email = self.controller.get_form_data("name", "email")
            self.assertEqual(name, "Alice")
            self.assertEqual(email, "alice@example.com")

    def test_get_form_data_returns_empty_string_for_missing_field(self):
        """get_form_data() returns '' for a field that was not submitted."""
        with self.app.test_request_context(method="POST", data={}):
            (result,) = self.controller.get_form_data("nonexistent_field")
            self.assertEqual(result, "")

    def test_flash_and_redirect_sets_flash_message(self):
        """flash_and_redirect() stores the flash message in the session."""
        with self.app.test_request_context():
            self.controller.flash_and_redirect("Hello!", "success", "auth.login")
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Hello!"), flashes)

    def test_flash_and_redirect_returns_302(self):
        """flash_and_redirect() returns a redirect response."""
        with self.app.test_request_context():
            response = self.controller.flash_and_redirect("Bye", "info", "auth.login")
            self.assertEqual(response.status_code, 302)


# ─────────────────────────────────────────────────────────────────────────────
#  LOGIN TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()
        self.controller.user_model = MagicMock()

    @patch("app.controllers.auth.render_template")
    def test_login_get_renders_login_page(self, mock_render):
        """GET /login renders login.html."""
        mock_render.return_value = "login_page"
        with self.app.test_request_context(method="GET"):
            result = self.controller.login()
            self.assertEqual(result, "login_page")
            mock_render.assert_called_once_with("login.html")

    def test_already_logged_in_redirects_to_dashboard(self):
        """If already logged in, GET /login redirects to dashboard."""
        with self.app.test_request_context(method="GET"):
            session["user_id"] = 1
            response = self.controller.login()
            self.assertEqual(response.status_code, 302)
            self.assertIn("dashboard", response.location)

    @patch("app.controllers.auth.render_template")
    @patch("app.controllers.auth.User.from_db")
    def test_login_wrong_password_shows_error(self, mock_from_db, mock_render):
        """Wrong password flashes danger and stays on login page."""
        mock_render.return_value = "login_page"
        self.controller.user_model.find_by.return_value = {
            "user_id": 1, "name": "Bob", "email": "bob@example.com", "role": "guest"
        }
        fake_user = MagicMock()
        fake_user.check_password.return_value = False
        mock_from_db.return_value = fake_user

        with self.app.test_request_context(
            method="POST", data={"email": "bob@example.com", "password": "wrongpass"}
        ):
            self.controller.login()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Invalid email or password."), flashes)
            self.assertNotIn("user_id", session)

    @patch("app.controllers.auth.render_template")
    def test_login_unknown_email_shows_error(self, mock_render):
        """An email not in the database shows the same generic error."""
        mock_render.return_value = "login_page"
        self.controller.user_model.find_by.return_value = None

        with self.app.test_request_context(
            method="POST", data={"email": "ghost@nowhere.com", "password": "anything"}
        ):
            self.controller.login()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Invalid email or password."), flashes)

    @patch("app.controllers.auth.Database")
    @patch("app.controllers.auth.User.from_db")
    def test_login_success_sets_session_and_redirects(self, mock_from_db, mock_db_class):
        """Correct credentials populate session and redirect to dashboard."""
        self.controller.user_model.find_by.return_value = {
            "user_id": 7, "name": "Alice", "email": "alice@example.com", "role": "guest"
        }
        fake_user = MagicMock()
        fake_user.check_password.return_value = True
        mock_from_db.return_value = fake_user

        # DB is only called for host pending-check; guest skips it
        with self.app.test_request_context(
            method="POST", data={"email": "alice@example.com", "password": "secret123"}
        ):
            response = self.controller.login()
            self.assertEqual(session.get("user_id"), 7)
            self.assertEqual(session.get("user_name"), "Alice")
            self.assertEqual(session.get("role"), "guest")
            self.assertEqual(response.status_code, 302)

    @patch("app.controllers.auth.Database")
    @patch("app.controllers.auth.User.from_db")
    def test_login_pending_host_receives_warning_flash(self, mock_from_db, mock_db_class):
        """
        A host whose host_profiles.verified = FALSE should see a warning
        flash at login (but still be allowed in).
        """
        self.controller.user_model.find_by.return_value = {
            "user_id": 5, "name": "Host Harry", "email": "harry@host.com", "role": "host"
        }
        fake_user = MagicMock()
        fake_user.check_password.return_value = True
        mock_from_db.return_value = fake_user

        # Mock the DB to return an unverified host_profile
        mock_db_instance = MagicMock()
        mock_db_instance.fetch_one.return_value = {"verified": False}
        mock_db_class.return_value = mock_db_instance

        with self.app.test_request_context(
            method="POST", data={"email": "harry@host.com", "password": "password123"}
        ):
            response = self.controller.login()
            flashes = get_flashed_messages(with_categories=True)
            categories = [cat for cat, _ in flashes]
            self.assertIn("warning", categories)
            # Still redirected (login succeeds despite pending status)
            self.assertEqual(response.status_code, 302)


# ─────────────────────────────────────────────────────────────────────────────
#  REGISTER TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestRegister(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()
        self.controller.user_model = MagicMock()

    @patch("app.controllers.auth.render_template")
    def test_register_get_renders_form(self, mock_render):
        """GET /register renders register.html."""
        mock_render.return_value = "register_page"
        with self.app.test_request_context(method="GET"):
            result = self.controller.register()
            self.assertEqual(result, "register_page")
            mock_render.assert_called_once_with("register.html")

    @patch("app.controllers.auth.render_template")
    def test_register_missing_fields_rejected(self, mock_render):
        """Empty name/email/password shows a danger flash."""
        mock_render.return_value = "register_page"
        with self.app.test_request_context(
            method="POST", data={"name": "", "email": "", "password": ""}
        ):
            self.controller.register()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "All fields are required."), flashes)

    @patch("app.controllers.auth.render_template")
    def test_register_short_password_rejected(self, mock_render):
        """Password shorter than 6 characters is refused."""
        mock_render.return_value = "register_page"
        with self.app.test_request_context(
            method="POST",
            data={"name": "Bob", "email": "bob@example.com", "password": "abc"}
        ):
            self.controller.register()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Password must be at least 6 characters."), flashes)

    @patch("app.controllers.auth.render_template")
    @patch("app.controllers.auth.User")
    def test_register_duplicate_email_rejected(self, mock_user_class, mock_render):
        """Taken email address shows error and does NOT save."""
        mock_render.return_value = "register_page"
        fake_user = MagicMock()
        fake_user.email_exists.return_value = True
        mock_user_class.return_value = fake_user

        with self.app.test_request_context(
            method="POST",
            data={"name": "Bob", "email": "taken@example.com", "password": "secret1"}
        ):
            self.controller.register()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Email already exists."), flashes)
            fake_user.save.assert_not_called()

    @patch("app.controllers.auth.User")
    def test_register_guest_success_saves_and_redirects(self, mock_user_class):
        """Valid guest registration saves user and redirects to login."""
        fake_user = MagicMock()
        fake_user.email_exists.return_value = False
        fake_user.save.return_value = 10
        mock_user_class.return_value = fake_user

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Alice", "email": "alice@example.com",
                "password": "secret1", "role": "guest"
            }
        ):
            response = self.controller.register()
            fake_user.save.assert_called_once()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Registration successful! Please login."), flashes)

    @patch("app.controllers.auth.User")
    def test_register_host_saves_host_profile(self, mock_user_class):
        """
        Registering as a host must call save_host_profile() so the
        host_profiles row is created (needed for admin approval flow).
        OOP note: this tests that the child controller correctly
        delegates host-profile creation to the User model.
        """
        fake_user = MagicMock()
        fake_user.email_exists.return_value = False
        fake_user.save.return_value = 99
        mock_user_class.return_value = fake_user

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Host Raj", "email": "raj@host.com",
                "password": "secure99", "role": "host",
                "id_type": "Citizenship", "id_number": "123",
                "property_type": "Homestay", "payout_bank": "Nabil Bank",
                "host_address": "Kathmandu", "consent": "true"
            }
        ):
            self.controller.register()
            fake_user.save_host_profile.assert_called_once()

    @patch("app.controllers.auth.User")
    def test_register_invalid_role_defaults_to_user(self, mock_user_class):
        """An invalid role value (e.g. 'superadmin') silently defaults to 'user'."""
        fake_user = MagicMock()
        fake_user.email_exists.return_value = False
        fake_user.save.return_value = 11
        mock_user_class.return_value = fake_user

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Eve", "email": "eve@example.com",
                "password": "secret1", "role": "superadmin"
            }
        ):
            self.controller.register()
            # The User constructor must have been called with role='user' (not 'superadmin')
            call_kwargs = mock_user_class.call_args
            self.assertEqual(call_kwargs.kwargs.get("role") or call_kwargs.args[3], "user")


# ─────────────────────────────────────────────────────────────────────────────
#  LOGOUT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestLogout(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_logout_clears_session_and_redirects_to_login(self):
        """Logout wipes every session key and sends to /login."""
        with self.app.test_request_context():
            session["user_id"]   = 5
            session["user_name"] = "Alice"
            session["role"]      = "guest"

            response = self.controller.logout()

            self.assertNotIn("user_id",   session)
            self.assertNotIn("user_name", session)
            self.assertNotIn("role",      session)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("success", "Logged out successfully."), flashes)

    def test_logout_during_impersonation_exits_view_as(self):
        """
        If an admin is impersonating another user and that user clicks
        logout, the session should restore the admin — not log out entirely.
        """
        with self.app.test_request_context():
            # Set up impersonation state
            session["user_id"]             = 10     # currently viewing as user 10
            session["user_name"]           = "Guest Guy"
            session["role"]                = "guest"
            session["_impersonator_id"]    = 1
            session["_impersonator_name"]  = "Admin"
            session["_impersonator_role"]  = "admin"

            response = self.controller.logout()

            # Should restore admin, not destroy session
            self.assertEqual(session.get("user_id"),   1)
            self.assertEqual(session.get("role"),       "admin")
            self.assertNotIn("_impersonator_id", session)
            self.assertEqual(response.status_code, 302)


# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD REDIRECT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestDashboardRedirect(unittest.TestCase):
    """
    OOP focus: Polymorphism.
    The dashboard() method behaves differently based on session role —
    same method call, different outcome. That's runtime polymorphism.
    """

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_not_logged_in_redirects_to_login(self):
        """Visiting /dashboard without a session sends to /login."""
        with self.app.test_request_context():
            response = self.controller.dashboard()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)

    def test_admin_redirected_to_admin_dashboard(self):
        """Admin role → /admin/dashboard."""
        with self.app.test_request_context():
            session["user_id"] = 1
            session["role"]    = "admin"
            response = self.controller.dashboard()
            self.assertEqual(response.status_code, 302)
            self.assertIn("admin", response.location)

    def test_host_redirected_to_host_dashboard(self):
        """Host role → /host/dashboard."""
        with self.app.test_request_context():
            session["user_id"] = 2
            session["role"]    = "host"
            response = self.controller.dashboard()
            self.assertEqual(response.status_code, 302)
            self.assertIn("host", response.location)

    def test_guest_redirected_to_guest_dashboard(self):
        """Guest role → /guest/dashboard."""
        with self.app.test_request_context():
            session["user_id"] = 3
            session["role"]    = "guest"
            response = self.controller.dashboard()
            self.assertEqual(response.status_code, 302)
            self.assertIn("guest", response.location)

    def test_unknown_role_redirected_to_guest_dashboard(self):
        """Any unrecognised role falls back to the guest dashboard."""
        with self.app.test_request_context():
            session["user_id"] = 4
            session["role"]    = "user"
            response = self.controller.dashboard()
            self.assertEqual(response.status_code, 302)
            self.assertIn("guest", response.location)


# ─────────────────────────────────────────────────────────────────────────────
#  WISHLIST TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestToggleWishlist(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_toggle_wishlist_requires_login(self):
        """Unauthenticated wishlist toggle returns 401."""
        with self.app.test_request_context(
            method="POST",
            json={"property_id": 1}
        ):
            response, status = self.controller.toggle_wishlist()
            self.assertEqual(status, 401)

    @patch("app.controllers.auth.Database")
    def test_toggle_adds_when_not_in_wishlist(self, mock_db_class):
        """
        When property is NOT in wishlist, toggle inserts it and returns action='added'.
        OOP note: encapsulation — the wishlist logic is hidden inside the controller;
        callers only see the action result.
        """
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = None  # not in wishlist yet
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"property_id": 3}):
            session["user_id"] = 5
            response = self.controller.toggle_wishlist()
            data = response.get_json()
            self.assertEqual(data["action"], "added")
            mock_db.execute.assert_called()

    @patch("app.controllers.auth.Database")
    def test_toggle_removes_when_already_in_wishlist(self, mock_db_class):
        """When property IS already in wishlist, toggle removes it and returns action='removed'."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"user_id": 5, "property_id": 3}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"property_id": 3}):
            session["user_id"] = 5
            response = self.controller.toggle_wishlist()
            data = response.get_json()
            self.assertEqual(data["action"], "removed")


# ─────────────────────────────────────────────────────────────────────────────
#  CONTACT FORM TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestContact(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.render_template")
    def test_contact_get_renders_template(self, mock_render):
        """GET /contact renders contact.html."""
        mock_render.return_value = "contact_page"
        with self.app.test_request_context(method="GET"):
            result = self.controller.contact()
            mock_render.assert_called_once_with("contact.html")

    @patch("app.controllers.auth.render_template")
    def test_contact_missing_fields_shows_error(self, mock_render):
        """Submitting the contact form with empty fields shows a danger flash."""
        mock_render.return_value = "contact_page"
        with self.app.test_request_context(
            method="POST",
            data={"name": "", "email": "", "subject": "", "message": ""}
        ):
            self.controller.contact()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "All fields are required."), flashes)

    @patch("app.controllers.auth.Database")
    def test_contact_valid_submission_saves_to_db(self, mock_db_class):
        """
        A complete contact form POSTs to the DB (support_queries table)
        and redirects with a success flash.
        This is the core of the feature — verifies the frontend form
        is no longer just calling a JS toast.
        """
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(
            method="POST",
            data={
                "name": "Ramesh", "email": "ramesh@email.com",
                "subject": "Booking issue", "message": "I cannot cancel my booking."
            }
        ):
            response = self.controller.contact()

            # DB execute was called (the INSERT)
            mock_db.execute.assert_called_once()
            # The INSERT call should include 'open' status
            call_args = mock_db.execute.call_args[0]
            self.assertIn("open", str(call_args))

            # Success flash
            flashes = get_flashed_messages(with_categories=True)
            self.assertTrue(any(cat == "success" for cat, _ in flashes))

            # Redirect after success
            self.assertEqual(response.status_code, 302)


# ─────────────────────────────────────────────────────────────────────────────
#  REVIEW TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateReview(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_review_requires_login(self):
        """Unauthenticated review attempt returns 401."""
        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "rating": 4, "comment": "Great place!"
        }):
            response, status = self.controller.create_review()
            self.assertEqual(status, 401)

    @patch("app.controllers.auth.Database")
    def test_review_missing_rating_returns_400(self, mock_db_class):
        """Missing rating field returns 400 bad request."""
        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "comment": "Nice place"
        }):
            session["user_id"] = 5
            response, status = self.controller.create_review()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_review_out_of_range_rating_rejected(self, mock_db_class):
        """Rating outside 1–5 range is rejected with 400."""
        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "rating": 6, "comment": "Too high!"
        }):
            session["user_id"] = 5
            response, status = self.controller.create_review()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_review_short_comment_rejected(self, mock_db_class):
        """A comment shorter than 2 characters is refused."""
        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "rating": 4, "comment": "X"
        }):
            session["user_id"] = 5
            response, status = self.controller.create_review()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_valid_review_saved_to_db(self, mock_db_class):
        """
        A valid review is inserted into the reviews table and the response
        contains the reviewer's name, rating, and comment.
        This is the core fix — reviews now persist across sessions.
        """
        mock_db = MagicMock()
        mock_db.execute_get_id.return_value = 42   # fake new review_id
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "rating": 5, "comment": "Absolutely loved it!"
        }):
            session["user_id"]   = 7
            session["user_name"] = "Priya"

            response = self.controller.create_review()
            data = response.get_json()

            self.assertTrue(data["success"])
            self.assertEqual(data["review"]["rating"],     5)
            self.assertEqual(data["review"]["comment"],    "Absolutely loved it!")
            self.assertEqual(data["review"]["guest_name"], "Priya")

            # Verify the INSERT actually happened
            mock_db.execute_get_id.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN ACTIONS TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestAdminActions(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.Database")
    def test_approve_host_sets_verified_true(self, mock_db_class):
        """approve_host() flips host_profiles.verified to TRUE."""
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(
            method="POST", data={"host_profile_id": "3"}
        ):
            session["role"] = "admin"
            self.controller.approve_host()
            call_sql = mock_db.execute.call_args[0][0]
            self.assertIn("verified", call_sql.lower())
            self.assertIn("TRUE", call_sql)

    @patch("app.controllers.auth.Database")
    def test_reject_host_deletes_profile_and_downgrades_role(self, mock_db_class):
        """
        reject_host() must fetch user_id BEFORE deleting the row,
        then downgrade that user's role to 'guest'.
        This was a known bug in an earlier version — this test pins the fix.
        """
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"user_id": 8}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(
            method="POST", data={"host_profile_id": "2"}
        ):
            session["role"] = "admin"
            self.controller.reject_host()

            calls = [str(c) for c in mock_db.execute.call_args_list]
            delete_called = any("DELETE" in c for c in calls)
            update_called = any("role" in c.lower() and "guest" in c for c in calls)
            self.assertTrue(delete_called, "DELETE FROM host_profiles was not called")
            self.assertTrue(update_called, "UPDATE users SET role='guest' was not called")

    @patch("app.controllers.auth.Database")
    def test_non_admin_cannot_delete_user(self, mock_db_class):
        """A non-admin calling delete_user() should be redirected, not execute the delete."""
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(
            method="POST", data={"user_id": "5"}
        ):
            session["role"] = "guest"
            response = self.controller.delete_user()
            # Redirect, not a successful delete
            self.assertEqual(response.status_code, 302)
            mock_db.execute.assert_not_called()

    @patch("app.controllers.auth.Database")
    def test_approve_property_sets_approved_status(self, mock_db_class):
        """approve_property() sets approval_status to 'approved'."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "property_id": 1, "title": "Test Property",
            "host_email": "host@test.com", "host_name": "Host"
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(
            method="POST", data={"property_id": "1"}
        ):
            session["role"] = "admin"
            with patch("app.controllers.auth.send_property_approval_email"):
                self.controller.approve_property()
            call_sql = mock_db.execute.call_args[0][0]
            self.assertIn("approved", call_sql)


# ─────────────────────────────────────────────────────────────────────────────
#  IMPERSONATION (VIEW AS USER) TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestImpersonation(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.Database")
    def test_view_as_stashes_admin_session(self, mock_db_class):
        """
        view_as_user() saves the real admin session under _impersonator_*
        keys before swapping to the target user.
        """
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "user_id": 10, "name": "Guest Guy", "role": "guest"
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(
            method="POST", data={"user_id": "10"}
        ):
            session["user_id"]   = 1
            session["user_name"] = "Admin"
            session["role"]      = "admin"

            self.controller.view_as_user()

            self.assertEqual(session.get("_impersonator_id"),   1)
            self.assertEqual(session.get("_impersonator_name"), "Admin")
            self.assertEqual(session.get("_impersonator_role"), "admin")
            self.assertEqual(session.get("user_id"),   10)
            self.assertEqual(session.get("role"),       "guest")

    def test_exit_view_as_restores_admin_session(self):
        """exit_view_as() fully restores the admin's original session."""
        with self.app.test_request_context():
            session["user_id"]             = 10
            session["user_name"]           = "Guest Guy"
            session["role"]                = "guest"
            session["_impersonator_id"]    = 1
            session["_impersonator_name"]  = "Admin"
            session["_impersonator_role"]  = "admin"

            self.controller.exit_view_as()

            self.assertEqual(session.get("user_id"),   1)
            self.assertEqual(session.get("user_name"), "Admin")
            self.assertEqual(session.get("role"),       "admin")
            self.assertNotIn("_impersonator_id",   session)
            self.assertNotIn("_impersonator_name", session)
            self.assertNotIn("_impersonator_role", session)

    @patch("app.controllers.auth.Database")
    def test_admin_cannot_view_as_another_admin(self, mock_db_class):
        """An admin account cannot be impersonated — should redirect with warning."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "user_id": 2, "name": "Admin 2", "role": "admin"
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(
            method="POST", data={"user_id": "2"}
        ):
            session["user_id"] = 1
            session["role"]    = "admin"

            response = self.controller.view_as_user()

            flashes = get_flashed_messages(with_categories=True)
            self.assertTrue(any("warning" == cat for cat, _ in flashes))
            self.assertEqual(response.status_code, 302)


# ─────────────────────────────────────────────────────────────────────────────
#  CREATE BOOKING TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateBooking(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_booking_requires_login(self):
        """Unauthenticated booking attempt returns 401."""
        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "checkin_date": "2026-08-01",
            "checkout_date": "2026-08-05", "guests_count": 2
        }):
            response, status = self.controller.create_booking()
            self.assertEqual(status, 401)

    @patch("app.controllers.auth.Database")
    def test_booking_exceeding_max_guests_rejected(self, mock_db_class):
        """
        Guest capacity validation — if guests_count > max_guests the booking
        is refused with a 400 error.
        This is user story US-?? from the spec: 'Guest cannot exceed property capacity.'
        """
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "property_id": 1, "host_id": 2, "price_per_night": 2500,
            "max_guests": 2, "title": "Mountain View",
            "approval_status": "approved", "status": "active"
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "checkin_date": "2026-08-01",
            "checkout_date": "2026-08-05", "guests_count": 10
        }):
            session["user_id"] = 3
            session["role"]    = "guest"
            response, status = self.controller.create_booking()
            self.assertEqual(status, 400)
            data = response.get_json()
            self.assertIn("guest", data["error"].lower())

    @patch("app.controllers.auth.Database")
    def test_booking_past_checkin_rejected(self, mock_db_class):
        """Check-in date in the past is refused."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "property_id": 1, "host_id": 2, "price_per_night": 2500,
            "max_guests": 4, "title": "Test",
            "approval_status": "approved", "status": "active"
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "checkin_date": "2020-01-01",
            "checkout_date": "2020-01-05", "guests_count": 2
        }):
            session["user_id"] = 3
            session["role"]    = "guest"
            response, status = self.controller.create_booking()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_booking_checkout_before_checkin_rejected(self, mock_db_class):
        """Checkout date before check-in date is refused."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "property_id": 1, "host_id": 2, "price_per_night": 2500,
            "max_guests": 4, "title": "Test",
            "approval_status": "approved", "status": "active"
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={
            "property_id": 1, "checkin_date": "2026-09-10",
            "checkout_date": "2026-09-05", "guests_count": 2
        }):
            session["user_id"] = 3
            session["role"]    = "guest"
            response, status = self.controller.create_booking()
            self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)