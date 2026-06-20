"""
=============================================================
    Pahuna — AuthController EXTENDED Unit Tests
=============================================================
  Covers the gaps left by test_auth_controller.py:
    - confirm_booking / reject_booking
    - cancel_booking / review_cancellation / mark_booking_complete
    - download_invoice
    - add_property
    - forgot_password / verify_code / reset_password
    - reject_property / admin_property_details
    - get_wishlist_ids / get_reviews
    - role_required decorator (tested directly, not bypassed)

  Run with:
      python -m pytest tests/test_auth_controller_extended.py -v
=============================================================
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta
from flask import Flask, Blueprint, session, get_flashed_messages
from app.controllers.auth import AuthController
from app.auth import role_required


# ─────────────────────────────────────────────────────────────────────────────
#  TEST APP FACTORY
#  Same shape as the original test file's factory, with the extra endpoints
#  these tests need (invoice download route, add-property, password reset).
# ─────────────────────────────────────────────────────────────────────────────

def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"

    bp = Blueprint("auth", __name__)

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
    bp.route("/verify-code",         endpoint="verify_code")(lambda: "verify")
    bp.route("/reset-password",      endpoint="reset_password")(lambda: "reset")
    bp.route("/review/create",       endpoint="create_review")(lambda: "review")
    bp.route("/add-property",        endpoint="add_property")(lambda: "add_property")

    app.register_blueprint(bp)
    return app


# ─────────────────────────────────────────────────────────────────────────────
#  CONFIRM / REJECT BOOKING (host actions)
# ─────────────────────────────────────────────────────────────────────────────

class TestConfirmBooking(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_confirm_booking_requires_login(self):
        """Unauthenticated confirm attempt returns 401."""
        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            response, status = self.controller.confirm_booking()
            self.assertEqual(status, 401)

    def test_confirm_booking_rejects_non_host(self):
        """A logged-in guest cannot confirm bookings."""
        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 3
            session["role"] = "guest"
            response, status = self.controller.confirm_booking()
            self.assertEqual(status, 401)

    @patch("app.controllers.auth.Database")
    def test_confirm_booking_not_found_returns_404(self, mock_db_class):
        """Booking that doesn't belong to this host returns 404."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = None
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 2
            session["role"] = "host"
            response, status = self.controller.confirm_booking()
            self.assertEqual(status, 404)

    @patch("app.controllers.auth.Database")
    def test_confirm_booking_only_pending_allowed(self, mock_db_class):
        """Trying to confirm an already-confirmed booking is refused with 400."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "booking_id": "ABC123", "status": "confirmed",
            "guest_email": "g@test.com", "guest_name": "Guest",
            "property_title": "Test Place"
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 2
            session["role"] = "host"
            response, status = self.controller.confirm_booking()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.send_booking_confirmation")
    @patch("app.controllers.auth.Database")
    def test_confirm_booking_success_updates_status_and_emails_guest(self, mock_db_class, mock_send_email):
        """Confirming a pending booking sets status='confirmed' and sends the guest an email."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "booking_id": "ABC123", "status": "pending",
            "guest_email": "guest@test.com", "guest_name": "Guest One",
            "property_title": "Mountain View",
            "checkin_date": date(2026, 8, 1), "checkout_date": date(2026, 8, 5),
            "total_amount": 10000,
        }
        mock_db_class.return_value = mock_db
        mock_send_email.return_value = True

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.confirm_booking()
            data = response.get_json()

            self.assertTrue(data["success"])
            mock_send_email.assert_called_once()
            update_calls = [str(c) for c in mock_db.execute.call_args_list]
            self.assertTrue(any("confirmed" in c for c in update_calls))

    @patch("app.controllers.auth.send_booking_confirmation")
    @patch("app.controllers.auth.Database")
    def test_confirm_booking_email_failure_does_not_break_response(self, mock_db_class, mock_send_email):
        """
        If the confirmation email raises, the booking is already confirmed in the DB
        and the endpoint must still return success (email failure is swallowed).
        """
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "booking_id": "ABC123", "status": "pending",
            "guest_email": "guest@test.com", "guest_name": "Guest One",
            "property_title": "Mountain View",
            "checkin_date": date(2026, 8, 1), "checkout_date": date(2026, 8, 5),
            "total_amount": 10000,
        }
        mock_db_class.return_value = mock_db
        mock_send_email.side_effect = Exception("SMTP down")

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.confirm_booking()
            data = response.get_json()
            self.assertTrue(data["success"])


class TestRejectBooking(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_reject_booking_requires_host(self):
        """Non-host cannot reject a booking."""
        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            response, status = self.controller.reject_booking()
            self.assertEqual(status, 401)

    @patch("app.controllers.auth.Database")
    def test_reject_booking_only_pending_allowed(self, mock_db_class):
        """Cannot reject a booking that's already confirmed/cancelled."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"status": "cancelled"}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 2
            session["role"] = "host"
            response, status = self.controller.reject_booking()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_reject_booking_success_cancels(self, mock_db_class):
        """Rejecting a pending booking sets status='cancelled'."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"status": "pending"}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.reject_booking()
            data = response.get_json()
            self.assertTrue(data["success"])
            call_sql = mock_db.execute.call_args[0][0]
            self.assertIn("cancelled", call_sql)


# ─────────────────────────────────────────────────────────────────────────────
#  CANCEL BOOKING / REVIEW CANCELLATION / MARK COMPLETE
# ─────────────────────────────────────────────────────────────────────────────

class TestCancelBooking(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_cancel_booking_requires_login(self):
        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            response, status = self.controller.cancel_booking()
            self.assertEqual(status, 401)

    def test_cancel_booking_rejects_host(self):
        """Only guests can request a cancellation, not hosts."""
        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 2
            session["role"] = "host"
            response, status = self.controller.cancel_booking()
            self.assertEqual(status, 403)

    @patch("app.controllers.auth.Database")
    def test_cancel_booking_not_found(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = None
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 3
            session["role"] = "guest"
            response, status = self.controller.cancel_booking()
            self.assertEqual(status, 404)

    @patch("app.controllers.auth.Database")
    def test_cancel_booking_already_completed_rejected(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"status": "completed", "cancellation_status": None}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 3
            session["role"] = "guest"
            response, status = self.controller.cancel_booking()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_cancel_booking_already_requested_rejected(self, mock_db_class):
        """Cannot double-submit a cancellation request."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"status": "confirmed", "cancellation_status": "requested"}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 3
            session["role"] = "guest"
            response, status = self.controller.cancel_booking()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_cancel_booking_success_sets_requested(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"status": "confirmed", "cancellation_status": None}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "ABC123"}):
            session["user_id"] = 3
            session["role"] = "guest"
            response = self.controller.cancel_booking()
            data = response.get_json()
            self.assertTrue(data["success"])
            call_sql = mock_db.execute.call_args[0][0]
            self.assertIn("requested", call_sql)


class TestReviewCancellation(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_review_cancellation_requires_host(self):
        with self.app.test_request_context(method="POST", json={"booking_id": "X", "action": "approve"}):
            session["user_id"] = 3
            session["role"] = "guest"
            response, status = self.controller.review_cancellation()
            self.assertEqual(status, 403)

    def test_review_cancellation_invalid_action_rejected(self):
        with self.app.test_request_context(method="POST", json={"booking_id": "X", "action": "maybe"}):
            session["user_id"] = 2
            session["role"] = "host"
            response, status = self.controller.review_cancellation()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_review_cancellation_no_pending_request(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"cancellation_status": None}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "X", "action": "approve"}):
            session["user_id"] = 2
            session["role"] = "host"
            response, status = self.controller.review_cancellation()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_review_cancellation_approve_cancels_booking(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"cancellation_status": "requested"}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "X", "action": "approve"}):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.review_cancellation()
            data = response.get_json()
            self.assertTrue(data["success"])
            call_sql = mock_db.execute.call_args[0][0]
            self.assertIn("cancelled", call_sql)

    @patch("app.controllers.auth.Database")
    def test_review_cancellation_reject_keeps_booking_active(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"cancellation_status": "requested"}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "X", "action": "reject"}):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.review_cancellation()
            data = response.get_json()
            self.assertTrue(data["success"])
            call_sql = mock_db.execute.call_args[0][0]
            self.assertIn("rejected", call_sql)
            self.assertNotIn("status='cancelled'", call_sql)


class TestMarkBookingComplete(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_mark_complete_requires_host(self):
        with self.app.test_request_context(method="POST", json={"booking_id": "X"}):
            session["user_id"] = 3
            session["role"] = "guest"
            response, status = self.controller.mark_booking_complete()
            self.assertEqual(status, 403)

    @patch("app.controllers.auth.Database")
    def test_mark_complete_only_confirmed_allowed(self, mock_db_class):
        """A pending or already-completed booking cannot be marked complete."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"status": "pending"}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "X"}):
            session["user_id"] = 2
            session["role"] = "host"
            response, status = self.controller.mark_booking_complete()
            self.assertEqual(status, 400)

    @patch("app.controllers.auth.Database")
    def test_mark_complete_success(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"status": "confirmed"}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", json={"booking_id": "X"}):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.mark_booking_complete()
            data = response.get_json()
            self.assertTrue(data["success"])
            call_sql = mock_db.execute.call_args[0][0]
            self.assertIn("completed", call_sql)


# ─────────────────────────────────────────────────────────────────────────────
#  DOWNLOAD INVOICE
# ─────────────────────────────────────────────────────────────────────────────

class TestDownloadInvoice(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_invoice_requires_login(self):
        with self.app.test_request_context():
            response = self.controller.download_invoice("ABC123")
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)

    @patch("app.controllers.auth.Database")
    def test_invoice_booking_not_found(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = None
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            session["user_id"] = 3
            response = self.controller.download_invoice("ABC123")
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Booking not found."), flashes)

    @patch("app.controllers.auth.Database")
    def test_invoice_wrong_guest_not_authorized(self, mock_db_class):
        """A guest cannot download another guest's invoice."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "guest_id": 99, "status": "confirmed",
            "booking_id": "ABC123", "property_title": "Test", "region": "Kathmandu",
            "guest_name": "Other Guest", "guest_email": "other@test.com",
            "host_name": "Host", "checkin_date": date(2026, 8, 1),
            "checkout_date": date(2026, 8, 5), "guests_count": 2,
            "total_amount": 5000,
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            session["user_id"] = 3
            session["role"] = "guest"
            response = self.controller.download_invoice("ABC123")
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "You are not authorized to view this invoice."), flashes)

    @patch("app.controllers.auth.Database")
    def test_invoice_pending_booking_rejected(self, mock_db_class):
        """Invoices are only available for confirmed/completed bookings."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "guest_id": 3, "status": "pending",
            "booking_id": "ABC123", "property_title": "Test", "region": "Kathmandu",
            "guest_name": "Guest", "guest_email": "guest@test.com",
            "host_name": "Host", "checkin_date": date(2026, 8, 1),
            "checkout_date": date(2026, 8, 5), "guests_count": 2,
            "total_amount": 5000,
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            session["user_id"] = 3
            session["role"] = "guest"
            response = self.controller.download_invoice("ABC123")
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertTrue(any("Invoice is available only" in msg for _, msg in flashes))

    @patch("app.controllers.auth.Database")
    def test_invoice_admin_can_download_any_booking(self, mock_db_class):
        """An admin is authorized regardless of who the guest is."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "guest_id": 99, "status": "confirmed",
            "booking_id": "ABC123", "property_title": "Test", "region": "Kathmandu",
            "guest_name": "Guest", "guest_email": "guest@test.com",
            "host_name": "Host", "checkin_date": date(2026, 8, 1),
            "checkout_date": date(2026, 8, 5), "guests_count": 2,
            "total_amount": 5000,
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            session["user_id"] = 1
            session["role"] = "admin"
            response = self.controller.download_invoice("ABC123")
            # Should reach PDF generation, not redirect
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, "application/pdf")

    @patch("app.controllers.auth.Database")
    def test_invoice_success_generates_pdf(self, mock_db_class):
        """A valid, owned, confirmed booking generates a downloadable PDF."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "guest_id": 3, "status": "confirmed",
            "booking_id": "ABC123", "property_title": "Mountain View", "region": "Pokhara",
            "guest_name": "Priya", "guest_email": "priya@test.com",
            "host_name": "Host Raj", "checkin_date": date(2026, 8, 1),
            "checkout_date": date(2026, 8, 5), "guests_count": 2,
            "total_amount": 10000,
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            session["user_id"] = 3
            session["role"] = "guest"
            response = self.controller.download_invoice("ABC123")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, "application/pdf")
            self.assertIn("invoice_ABC123.pdf", response.headers.get("Content-Disposition", ""))


# ─────────────────────────────────────────────────────────────────────────────
#  ADD PROPERTY
# ─────────────────────────────────────────────────────────────────────────────

class TestAddProperty(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_add_property_requires_login(self):
        with self.app.test_request_context(method="GET"):
            response = self.controller.add_property()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)

    def test_add_property_rejects_non_host(self):
        with self.app.test_request_context(method="GET"):
            session["user_id"] = 3
            session["role"] = "guest"
            response = self.controller.add_property()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/browse", response.location)

    @patch("app.controllers.auth.Database")
    def test_add_property_unverified_host_blocked(self, mock_db_class):
        """An unverified host is redirected before reaching the form, GET or POST."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"verified": False}
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="GET"):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.add_property()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/host/dashboard", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertTrue(any("pending admin approval" in msg for _, msg in flashes))

    @patch("app.controllers.auth.Database")
    def test_add_property_no_host_profile_blocked(self, mock_db_class):
        """A host with no host_profiles row at all is also blocked (not just verified=False)."""
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = None
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="GET"):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.add_property()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/host/dashboard", response.location)

    @patch("app.controllers.auth.render_template")
    @patch("app.controllers.auth.Database")
    def test_add_property_verified_host_get_renders_form(self, mock_db_class, mock_render):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"verified": True}
        mock_db_class.return_value = mock_db
        mock_render.return_value = "add_property_page"

        with self.app.test_request_context(method="GET"):
            session["user_id"] = 2
            session["role"] = "host"
            result = self.controller.add_property()
            self.assertEqual(result, "add_property_page")

    @patch("app.controllers.auth.render_template")
    @patch("app.controllers.auth.Database")
    def test_add_property_missing_required_fields_rejected(self, mock_db_class, mock_render):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"verified": True}
        mock_db_class.return_value = mock_db
        mock_render.return_value = "add_property_page"

        with self.app.test_request_context(method="POST", data={
            "property_name": "", "property_type": "", "region": "", "price_per_night": ""
        }):
            session["user_id"] = 2
            session["role"] = "host"
            self.controller.add_property()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "All required fields must be filled."), flashes)

    @patch("app.controllers.auth.Database")
    def test_add_property_success_inserts_pending_inactive(self, mock_db_class):
        """
        A valid submission must insert with status='inactive' and
        approval_status='pending' — properties are NOT visible until approved.
        """
        # First call (verification gate) -> verified True
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {"verified": True}
        mock_db.execute_get_id.return_value = 55
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", data={
            "property_name": "Lakeside Comfort",
            "property_type": "Homestay",
            "region": "Pokhara",
            "price_per_night": "3000",
            "max_guests": "4",
        }):
            session["user_id"] = 2
            session["role"] = "host"
            response = self.controller.add_property()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/host/dashboard", response.location)

            insert_sql = mock_db.execute_get_id.call_args[0][0]
            self.assertIn("pending", insert_sql)
            self.assertIn("inactive", insert_sql)

            flashes = get_flashed_messages(with_categories=True)
            self.assertTrue(any("submitted for admin review" in msg for _, msg in flashes))


# ─────────────────────────────────────────────────────────────────────────────
#  PASSWORD RESET FLOW
# ─────────────────────────────────────────────────────────────────────────────

class TestForgotPassword(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()
        self.controller.user_model = MagicMock()

    @patch("app.controllers.auth.render_template")
    def test_forgot_password_get_renders_form(self, mock_render):
        mock_render.return_value = "reset_page"
        with self.app.test_request_context(method="GET"):
            result = self.controller.forgot_password()
            self.assertEqual(result, "reset_page")

    @patch("app.controllers.auth.render_template")
    def test_forgot_password_empty_email_rejected(self, mock_render):
        mock_render.return_value = "reset_page"
        with self.app.test_request_context(method="POST", data={"email": ""}):
            self.controller.forgot_password()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Please enter your email address."), flashes)

    @patch("app.controllers.auth.render_template")
    @patch("app.controllers.auth.send_reset_code")
    @patch.object(AuthController, "_save_reset_code")
    @patch.object(AuthController, "_generate_code")
    def test_forgot_password_unknown_email_still_shows_sent_page(
        self, mock_gen_code, mock_save_code, mock_send, mock_render
    ):
        """
        Security: an email that doesn't exist in the DB should NOT reveal that
        fact — the UI shows the same 'sent' confirmation either way.
        """
        mock_render.return_value = "sent_page"
        self.controller.user_model.find_by.return_value = None

        with self.app.test_request_context(method="POST", data={"email": "ghost@nowhere.com"}):
            self.controller.forgot_password()
            mock_send.assert_not_called()
            mock_render.assert_called_once_with(
                "password_reset.html", sent=True, email="ghost@nowhere.com"
            )

    @patch("app.controllers.auth.render_template")
    @patch("app.controllers.auth.send_reset_code")
    @patch.object(AuthController, "_save_reset_code")
    @patch.object(AuthController, "_generate_code")
    def test_forgot_password_known_email_sends_code(
        self, mock_gen_code, mock_save_code, mock_send, mock_render
    ):
        mock_gen_code.return_value = "123456"
        mock_send.return_value = True
        mock_render.return_value = "sent_page"
        self.controller.user_model.find_by.return_value = {"user_id": 1, "email": "a@b.com"}

        with self.app.test_request_context(method="POST", data={"email": "a@b.com"}):
            self.controller.forgot_password()
            mock_save_code.assert_called_once_with("a@b.com", "123456")
            mock_send.assert_called_once_with("a@b.com", "123456")

    @patch("app.controllers.auth.render_template")
    @patch("app.controllers.auth.send_reset_code")
    @patch.object(AuthController, "_save_reset_code")
    @patch.object(AuthController, "_generate_code")
    def test_forgot_password_email_send_failure_shows_error(
        self, mock_gen_code, mock_save_code, mock_send, mock_render
    ):
        mock_gen_code.return_value = "123456"
        mock_send.return_value = False
        mock_render.return_value = "reset_page"
        self.controller.user_model.find_by.return_value = {"user_id": 1, "email": "a@b.com"}

        with self.app.test_request_context(method="POST", data={"email": "a@b.com"}):
            self.controller.forgot_password()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Failed to send email. Please try again."), flashes)


class TestVerifyCode(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.render_template")
    def test_verify_code_get_renders_form(self, mock_render):
        mock_render.return_value = "verify_page"
        with self.app.test_request_context(method="GET", query_string={"email": "a@b.com"}):
            result = self.controller.verify_code()
            self.assertEqual(result, "verify_page")

    @patch("app.controllers.auth.render_template")
    def test_verify_code_incomplete_code_rejected(self, mock_render):
        mock_render.return_value = "verify_page"
        with self.app.test_request_context(method="POST", data={"email": "a@b.com", "code": "123"}):
            self.controller.verify_code()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Please enter the full 6-digit code."), flashes)

    @patch.object(AuthController, "_verify_code")
    def test_verify_code_valid_redirects_to_reset(self, mock_verify):
        mock_verify.return_value = True
        with self.app.test_request_context(
            method="POST", data={"email": "a@b.com", "code": "123456"}
        ):
            response = self.controller.verify_code()
            self.assertEqual(response.status_code, 302)
            self.assertIn("reset-password", response.location)

    @patch("app.controllers.auth.render_template")
    @patch.object(AuthController, "_verify_code")
    def test_verify_code_invalid_shows_error(self, mock_verify, mock_render):
        mock_verify.return_value = False
        mock_render.return_value = "verify_page"
        with self.app.test_request_context(
            method="POST", data={"email": "a@b.com", "code": "999999"}
        ):
            self.controller.verify_code()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Invalid or expired code."), flashes)


class TestResetPassword(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()
        self.controller.user_model = MagicMock()

    @patch.object(AuthController, "_verify_code")
    def test_reset_password_get_expired_code_redirects(self, mock_verify):
        mock_verify.return_value = False
        with self.app.test_request_context(
            method="GET", query_string={"email": "a@b.com", "code": "123456"}
        ):
            response = self.controller.reset_password()
            self.assertEqual(response.status_code, 302)
            self.assertIn("forgot-password", response.location)

    @patch("app.controllers.auth.render_template")
    @patch.object(AuthController, "_verify_code")
    def test_reset_password_get_valid_code_renders_form(self, mock_verify, mock_render):
        mock_verify.return_value = True
        mock_render.return_value = "update_password_page"
        with self.app.test_request_context(
            method="GET", query_string={"email": "a@b.com", "code": "123456"}
        ):
            result = self.controller.reset_password()
            self.assertEqual(result, "update_password_page")

    @patch("app.controllers.auth.render_template")
    def test_reset_password_post_short_password_rejected(self, mock_render):
        mock_render.return_value = "update_password_page"
        with self.app.test_request_context(
            method="POST",
            data={"email": "a@b.com", "code": "123456", "password": "short", "confirm_password": "short"}
        ):
            self.controller.reset_password()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Password must be at least 8 characters."), flashes)

    @patch("app.controllers.auth.render_template")
    def test_reset_password_post_mismatched_passwords_rejected(self, mock_render):
        mock_render.return_value = "update_password_page"
        with self.app.test_request_context(
            method="POST",
            data={
                "email": "a@b.com", "code": "123456",
                "password": "longenough1", "confirm_password": "different1"
            }
        ):
            self.controller.reset_password()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Passwords do not match."), flashes)

    @patch.object(AuthController, "_verify_code")
    def test_reset_password_post_expired_code_redirects(self, mock_verify):
        mock_verify.return_value = False
        with self.app.test_request_context(
            method="POST",
            data={
                "email": "a@b.com", "code": "123456",
                "password": "longenough1", "confirm_password": "longenough1"
            }
        ):
            response = self.controller.reset_password()
            self.assertEqual(response.status_code, 302)
            self.assertIn("forgot-password", response.location)

    @patch.object(AuthController, "_verify_code")
    def test_reset_password_post_account_not_found(self, mock_verify):
        mock_verify.return_value = True
        self.controller.user_model.find_by.return_value = None
        with self.app.test_request_context(
            method="POST",
            data={
                "email": "ghost@b.com", "code": "123456",
                "password": "longenough1", "confirm_password": "longenough1"
            }
        ):
            response = self.controller.reset_password()
            self.assertEqual(response.status_code, 302)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Account not found."), flashes)

    @patch("app.controllers.auth.User.from_db")
    @patch.object(AuthController, "_mark_code_used")
    @patch.object(AuthController, "_verify_code")
    def test_reset_password_post_success_updates_and_redirects(
        self, mock_verify, mock_mark_used, mock_from_db
    ):
        mock_verify.return_value = True
        self.controller.user_model.find_by.return_value = {"user_id": 5, "email": "a@b.com"}
        fake_user = MagicMock()
        mock_from_db.return_value = fake_user

        with self.app.test_request_context(
            method="POST",
            data={
                "email": "a@b.com", "code": "123456",
                "password": "longenough1", "confirm_password": "longenough1"
            }
        ):
            response = self.controller.reset_password()
            fake_user.set_password.assert_called_once_with("longenough1")
            fake_user.update.assert_called_once_with(5, update_password=True)
            mock_mark_used.assert_called_once_with("a@b.com", "123456")
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)


# ─────────────────────────────────────────────────────────────────────────────
#  REJECT PROPERTY / ADMIN PROPERTY DETAILS
# ─────────────────────────────────────────────────────────────────────────────

class TestRejectProperty(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.Database")
    def test_reject_property_not_found(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = None
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", data={"property_id": "1"}):
            session["role"] = "admin"
            response = self.controller.reject_property()
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("danger", "Property not found."), flashes)

    @patch("app.controllers.auth.send_property_rejection_email")
    @patch("app.controllers.auth.Database")
    def test_reject_property_sets_rejected_and_emails_host(self, mock_db_class, mock_send_email):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "property_id": 1, "title": "Bad Listing",
            "host_email": "host@test.com", "host_name": "Host"
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context(method="POST", data={"property_id": "1"}):
            session["role"] = "admin"
            self.controller.reject_property()
            call_sql = mock_db.execute.call_args[0][0]
            self.assertIn("rejected", call_sql)
            mock_send_email.assert_called_once()

    @patch("app.controllers.auth.Database")
    def test_reject_property_non_admin_redirected(self, mock_db_class):
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        with self.app.test_request_context(method="POST", data={"property_id": "1"}):
            session["role"] = "host"
            response = self.controller.reject_property()
            self.assertEqual(response.status_code, 302)
            mock_db.execute.assert_not_called()


class TestAdminPropertyDetails(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_admin_property_details_requires_admin(self):
        with self.app.test_request_context():
            session["role"] = "guest"
            response, status = self.controller.admin_property_details(1)
            self.assertEqual(status, 403)

    @patch("app.controllers.auth.Database")
    def test_admin_property_details_not_found(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = None
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            session["role"] = "admin"
            response, status = self.controller.admin_property_details(999)
            self.assertEqual(status, 404)

    @patch("app.controllers.auth.Database")
    def test_admin_property_details_converts_time_fields_to_strings(self, mock_db_class):
        """Time objects must be stringified so the JSON response doesn't break."""
        from datetime import time
        mock_db = MagicMock()
        mock_db.fetch_one.return_value = {
            "property_id": 1, "host_name": "Host",
            "checkin_time": time(14, 0), "checkout_time": time(11, 0),
            "breakfast_time": None,
        }
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            session["role"] = "admin"
            response = self.controller.admin_property_details(1)
            data = response.get_json()
            self.assertEqual(data["checkin_time"], "14:00:00")
            self.assertEqual(data["checkout_time"], "11:00:00")
            self.assertIsNone(data["breakfast_time"])


# ─────────────────────────────────────────────────────────────────────────────
#  WISHLIST IDS / REVIEWS
# ─────────────────────────────────────────────────────────────────────────────

class TestGetWishlistIds(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    def test_returns_empty_set_when_not_logged_in(self):
        with self.app.test_request_context():
            result = self.controller.get_wishlist_ids()
            self.assertEqual(result, set())

    @patch("app.controllers.auth.Database")
    def test_returns_set_of_property_ids(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_all.return_value = [{"property_id": 1}, {"property_id": 3}]
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            session["user_id"] = 5
            result = self.controller.get_wishlist_ids()
            self.assertEqual(result, {1, 3})


class TestGetReviews(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.controller = AuthController()

    @patch("app.controllers.auth.Database")
    def test_get_reviews_returns_json_list(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_all.return_value = [
            {"review_id": 1, "guest_name": "Priya", "rating": 5, "comment": "Lovely!"}
        ]
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            response = self.controller.get_reviews(1)
            data = response.get_json()
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["guest_name"], "Priya")

    @patch("app.controllers.auth.Database")
    def test_get_reviews_empty_returns_empty_list(self, mock_db_class):
        mock_db = MagicMock()
        mock_db.fetch_all.return_value = []
        mock_db_class.return_value = mock_db

        with self.app.test_request_context():
            response = self.controller.get_reviews(999)
            data = response.get_json()
            self.assertEqual(data, [])


# ─────────────────────────────────────────────────────────────────────────────
#  role_required DECORATOR
#  Tested directly against a dummy view, NOT through the controller, since the
#  existing tests call controller methods unbound from their decorators.
# ─────────────────────────────────────────────────────────────────────────────

class TestRoleRequiredDecorator(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()

        @role_required("admin")
        def admin_only_view():
            return "admin content"

        @role_required("host", "admin")
        def shared_view():
            return "shared content"

        self.admin_only_view = admin_only_view
        self.shared_view = shared_view

    def test_not_logged_in_redirects_to_login_with_warning(self):
        with self.app.test_request_context():
            response = self.admin_only_view()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertIn(("warning", "Please login first."), flashes)

    def test_correct_role_allowed_through(self):
        with self.app.test_request_context():
            session["user_id"] = 1
            session["role"] = "admin"
            result = self.admin_only_view()
            self.assertEqual(result, "admin content")

    def test_wrong_role_redirected_silently_to_own_dashboard(self):
        """
        Logged in but wrong role -> redirected to the user's OWN dashboard,
        with NO error flash (per the documented 'silent' behavior).
        """
        with self.app.test_request_context():
            session["user_id"] = 3
            session["role"] = "guest"
            response = self.admin_only_view()
            self.assertEqual(response.status_code, 302)
            self.assertIn("guest", response.location)
            flashes = get_flashed_messages(with_categories=True)
            self.assertEqual(flashes, [])  # silent, no flash

    def test_multi_role_decorator_allows_either_listed_role(self):
        with self.app.test_request_context():
            session["user_id"] = 2
            session["role"] = "host"
            result = self.shared_view()
            self.assertEqual(result, "shared content")

        with self.app.test_request_context():
            session["user_id"] = 1
            session["role"] = "admin"
            result = self.shared_view()
            self.assertEqual(result, "shared content")

    def test_multi_role_decorator_blocks_unlisted_role(self):
        with self.app.test_request_context():
            session["user_id"] = 3
            session["role"] = "guest"
            response = self.shared_view()
            self.assertEqual(response.status_code, 302)
            self.assertIn("guest", response.location)


if __name__ == "__main__":
    unittest.main(verbosity=2)