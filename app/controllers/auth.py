import email as _email_module   # renamed to avoid collision with local var

from flask import render_template, request, flash, redirect, url_for, session, jsonify
from app.controllers.basecontroller import BaseController
from app.models.usermodel import User
from app.models.database import Database
from app.services.email_service import send_reset_code
from app.auth import role_required
import random
import string
from datetime import datetime, timedelta


class AuthController(BaseController):
    def __init__(self):
        self.user_model = User()

    # ════════════════════════════════════════════════════════════
    # HELPERS — password reset
    # ════════════════════════════════════════════════════════════

    def _generate_code(self):
        return ''.join(random.choices(string.digits, k=6))

    def _save_reset_code(self, email, code):
        db = Database()
        db.execute(
            "UPDATE password_resets SET used = TRUE WHERE email = %s AND used = FALSE",
            (email,)
        )
        expires_at = datetime.now() + timedelta(minutes=10)
        db.execute(
            "INSERT INTO password_resets (email, code, expires_at) VALUES (%s, %s, %s)",
            (email, code, expires_at)
        )
        db.close()

    def _verify_code(self, email, code):
        db = Database()
        row = db.fetch_one(
            """SELECT * FROM password_resets
               WHERE email = %s AND code = %s AND used = FALSE AND expires_at > NOW()
               ORDER BY created_at DESC LIMIT 1""",
            (email, code)
        )
        db.close()
        return row is not None

    def _mark_code_used(self, email, code):
        db = Database()
        db.execute(
            "UPDATE password_resets SET used = TRUE WHERE email = %s AND code = %s",
            (email, code)
        )
        db.close()

    # ════════════════════════════════════════════════════════════
    # AUTH
    # ════════════════════════════════════════════════════════════

    def login(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            email    = request.form.get("email")
            password = request.form.get("password")

            user_data = self.user_model.find_by("email", email)
            if user_data:
                user = User.from_db(user_data)
                if user.check_password(password):
                    session["user_id"]   = user_data["user_id"]
                    session["user_name"] = user_data["name"]
                    session["role"]      = user_data["role"]

                    # Let pending hosts know right at login, not just on the dashboard
                    if user_data["role"] == "host":
                        db = Database()
                        host_profile = db.fetch_one(
                            "SELECT verified FROM host_profiles WHERE user_id=%s",
                            (user_data["user_id"],)
                        )
                        db.close()
                        if host_profile and not host_profile["verified"]:
                            flash(
                                "Welcome back! Your host account is still pending admin approval. "
                                "You can log in and view your dashboard, but you won't be able to add "
                                "properties until you're approved.",
                                "warning"
                            )

                    return redirect(url_for("auth.dashboard"))

            flash("Invalid email or password.", "danger")

        return render_template("login.html")

    def register(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            name, email = self.get_form_data("name", "email")
            password = request.form.get("password", "")
            phone    = request.form.get("phone", "").strip()
            role     = request.form.get("role", "user")
            if role not in ("guest", "host"):
                role = "user"

            if not name or not email or not password:
                flash("All fields are required.", "danger")
                return render_template("register.html")
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("register.html")

            new_user = User(name=name, email=email, password=password, role=role)
            if new_user.email_exists():
                flash("Email already exists.", "danger")
                return render_template("register.html")

            try:
                user_id = new_user.save(phone=phone)
                if role == "host":
                    new_user.save_host_profile(
                        user_id,
                        request.form.get("id_type", ""),
                        request.form.get("id_number", ""),
                        request.form.get("property_type", ""),
                        request.form.get("payout_bank", ""),
                        request.form.get("host_address", ""),
                        request.form.get("consent") == "true"
                    )
            except Exception as e:
                flash("Registration failed: " + str(e), "danger")
                return render_template("register.html")

            return self.flash_and_redirect(
                "Registration successful! Please login.", "success", "auth.login"
            )

        return render_template("register.html")

    def logout(self):
    # If admin is impersonating, return to admin instead of
    # destroying the real admin session.
        if session.get("_impersonator_id"):
            return self.exit_view_as()

        session.clear()
        flash("Logged out successfully.", "success")
        return redirect(url_for("auth.login"))

    # ════════════════════════════════════════════════════════════
    # DASHBOARD — legacy redirect only
    # ════════════════════════════════════════════════════════════
    # /dashboard is kept alive for old bookmarks/links. It does no
    # rendering itself — it just sends the user to their role's own
    # URL: /admin/dashboard, /host/dashboard, or /guest/dashboard.

    def dashboard(self):
        if not self.is_logged_in():
            return redirect(url_for("auth.login"))

        role = session.get("role")
        if role == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        elif role == "host":
            return redirect(url_for("auth.host_dashboard"))
        else:
            return redirect(url_for("auth.guest_dashboard"))

    # ════════════════════════════════════════════════════════════
    # ADMIN — VIEW AS USER (impersonation for troubleshooting)
    # ════════════════════════════════════════════════════════════
    # Lets an admin temporarily see exactly what a user sees, fully
    # interactive (can submit forms / edit data as that user).
    # The admin's real identity is stashed in session under
    # "impersonator_*" keys and restored on exit_view_as().



    # ────────────────────────────────────────────────────────────
    # ADMIN DASHBOARD
    # ────────────────────────────────────────────────────────────

    @role_required("admin")
    def admin_dashboard(self):
        db = Database()

        # ── Stats ──────────────────────────────────────────────
        stats = {
            "total_users":      db.fetch_one("SELECT COUNT(*) AS c FROM users")["c"],
            "total_properties": db.fetch_one("SELECT COUNT(*) AS c FROM properties")["c"],
            "total_bookings":   db.fetch_one("SELECT COUNT(*) AS c FROM bookings")["c"],
            "open_queries":     db.fetch_one("SELECT COUNT(*) AS c FROM support_queries WHERE status='open'")["c"],
            "pending_hosts":    db.fetch_one("SELECT COUNT(*) AS c FROM host_profiles WHERE verified=FALSE")["c"],
            "pending_props":    db.fetch_one("SELECT COUNT(*) AS c FROM properties WHERE approval_status='pending'")["c"],
        }

        # ── Users ──────────────────────────────────────────────
        users = db.fetch_all("SELECT * FROM users ORDER BY registered_at DESC")

        # ── Pending host approvals ──────────────────────────────
        pending_hosts = db.fetch_all("""
            SELECT u.user_id, u.name, u.email, u.registered_at,
                   hp.host_profile_id, hp.id_type, hp.id_number,
                   hp.property_type, hp.payout_bank, hp.host_address, hp.verified
            FROM host_profiles hp
            JOIN users u ON u.user_id = hp.user_id
            WHERE hp.verified = FALSE
            ORDER BY hp.created_at DESC
        """)

        # ── All properties ─────────────────────────────────────
        properties = db.fetch_all("""
            SELECT p.*, u.name AS host_name
            FROM properties p
            LEFT JOIN users u ON u.user_id = p.host_id
            ORDER BY p.property_id DESC
        """)

        # ── All bookings ───────────────────────────────────────
        bookings = db.fetch_all("""
            SELECT b.*,
                   g.name  AS guest_name,
                   pr.title AS property_title,
                   h.name  AS host_name
            FROM bookings b
            JOIN users      g  ON g.user_id    = b.guest_id
            JOIN properties pr ON pr.property_id = b.property_id
            JOIN users      h  ON h.user_id    = pr.host_id
            ORDER BY b.created_at DESC
        """)

        # ── Support queries ────────────────────────────────────
        queries = db.fetch_all(
            "SELECT * FROM support_queries ORDER BY created_at DESC"
        )

        db.close()

        return render_template(
            "admin_dashboard.html",
            stats=stats,
            users=users,
            pending_hosts=pending_hosts,
            properties=properties,
            bookings=bookings,
            queries=queries,
        )

    # ── Admin actions ───────────────────────────────────────────

    def approve_host(self):
        if session.get("role") != "admin":
            return redirect(url_for("auth.admin_dashboard"))
        host_profile_id = request.form.get("host_profile_id")
        db = Database()
        db.execute(
            "UPDATE host_profiles SET verified=TRUE WHERE host_profile_id=%s",
            (host_profile_id,)
        )
        db.close()
        flash("Host approved.", "success")
        return redirect(url_for("auth.admin_dashboard"))

    def reject_host(self):
        if session.get("role") != "admin":
            return redirect(url_for("auth.admin_dashboard"))
        host_profile_id = request.form.get("host_profile_id")
        db = Database()
        # Get user_id BEFORE deleting the row, or the subquery below finds nothing
        profile = db.fetch_one(
            "SELECT user_id FROM host_profiles WHERE host_profile_id=%s",
            (host_profile_id,)
        )
        if profile:
            db.execute(
                "DELETE FROM host_profiles WHERE host_profile_id=%s",
                (host_profile_id,)
            )
            db.execute(
                "UPDATE users SET role='guest' WHERE user_id=%s",
                (profile["user_id"],)
            )
        db.close()
        flash("Host rejected and downgraded to guest.", "warning")
        return redirect(url_for("auth.admin_dashboard"))

    def approve_property(self):
        if session.get("role") != "admin":
            return redirect(url_for("auth.admin_dashboard"))
        property_id = request.form.get("property_id")
        db = Database()
        db.execute(
            "UPDATE properties SET approval_status='approved' WHERE property_id=%s",
            (property_id,)
        )
        db.close()
        flash("Property approved.", "success")
        return redirect(url_for("auth.admin_dashboard"))

    def reject_property(self):
        if session.get("role") != "admin":
            return redirect(url_for("auth.admin_dashboard"))
        property_id = request.form.get("property_id")
        db = Database()
        db.execute(
            "UPDATE properties SET approval_status='rejected' WHERE property_id=%s",
            (property_id,)
        )
        db.close()
        flash("Property rejected.", "warning")
        return redirect(url_for("auth.admin_dashboard"))

    def delete_user(self):
        if session.get("role") != "admin":
            return redirect(url_for("auth.admin_dashboard"))
        user_id = request.form.get("user_id")
        db = Database()
        db.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        db.close()
        flash("User deleted.", "warning")
        return redirect(url_for("auth.admin_dashboard"))

    # ── Admin: view-as (impersonation) ───────────────────────────

    def view_as_user(self):
        """
        Admin clicks 'Login as' on a user row. We stash the admin's real
        identity in session under separate _impersonator_* keys, then swap
        the active session to the target user. The target user's dashboard
        renders normally and is fully interactive (real actions, real DB
        writes) — this is for troubleshooting, not a read-only preview.
        """
        if session.get("role") != "admin":
            return redirect(url_for("auth.admin_dashboard"))

        target_user_id = request.form.get("user_id")
        db = Database()
        target = db.fetch_one("SELECT * FROM users WHERE user_id=%s", (target_user_id,))
        db.close()

        if not target:
            flash("User not found.", "danger")
            return redirect(url_for("auth.admin_dashboard"))

        if target["role"] == "admin":
            flash("You can't view-as another admin account.", "warning")
            return redirect(url_for("auth.admin_dashboard"))

        # Stash the real admin identity (only if not already impersonating —
        # prevents nested impersonation from clobbering the original admin)
        if not session.get("_impersonator_id"):
            session["_impersonator_id"]   = session.get("user_id")
            session["_impersonator_name"] = session.get("user_name")
            session["_impersonator_role"] = session.get("role")

        # Swap active session to the target user
        session["user_id"]   = target["user_id"]
        session["user_name"] = target["name"]
        session["role"]      = target["role"]

        flash(f"You are now viewing as {target['name']} ({target['role']}).", "info")

        if target["role"] == "host":
            return redirect(url_for("auth.host_dashboard"))
        else:
            return redirect(url_for("auth.guest_dashboard"))

    def exit_view_as(self):
        """Restore the original admin session after a view-as session."""
        if not session.get("_impersonator_id"):
            # Not impersonating anyone — nothing to exit
            return redirect(url_for("auth.dashboard"))

        session["user_id"]   = session.pop("_impersonator_id")
        session["user_name"] = session.pop("_impersonator_name")
        session["role"]      = session.pop("_impersonator_role")

        flash("Returned to your admin account.", "success")
        return redirect(url_for("auth.admin_dashboard"))

    def resolve_query(self):
        if session.get("role") != "admin":
            return redirect(url_for("auth.admin_dashboard"))
        query_id = request.form.get("query_id")
        db = Database()
        db.execute(
            "UPDATE support_queries SET status='resolved' WHERE query_id=%s",
            (query_id,)
        )
        db.close()
        flash("Query marked as resolved.", "success")
        return redirect(url_for("auth.admin_dashboard"))

    def delete_property_admin(self):
        if session.get("role") != "admin":
            return redirect(url_for("auth.admin_dashboard"))
        property_id = request.form.get("property_id")
        db = Database()
        db.execute("DELETE FROM properties WHERE property_id=%s", (property_id,))
        db.close()
        flash("Property deleted.", "warning")
        return redirect(url_for("auth.admin_dashboard"))

    # ────────────────────────────────────────────────────────────
    # HOST DASHBOARD
    # ────────────────────────────────────────────────────────────

    @role_required("host")
    def host_dashboard(self):
        host_id = session.get("user_id")
        db = Database()

        # Approval status from host_profiles
        host_profile = db.fetch_one(
            "SELECT * FROM host_profiles WHERE user_id=%s", (host_id,)
        )

        # My properties
        properties = db.fetch_all("""
            SELECT p.*,
                   COUNT(DISTINCT b.booking_id) AS booking_count,
                   COALESCE(SUM(CASE WHEN b.status='confirmed' THEN b.total_amount ELSE 0 END), 0) AS revenue
            FROM properties p
            LEFT JOIN bookings b ON b.property_id = p.property_id
            WHERE p.host_id = %s
            GROUP BY p.property_id
            ORDER BY p.property_id DESC
        """, (host_id,))

        # Bookings for my properties
        bookings = db.fetch_all("""
            SELECT b.*, g.name AS guest_name, p.title AS property_title
            FROM bookings b
            JOIN users      g ON g.user_id    = b.guest_id
            JOIN properties p ON p.property_id = b.property_id
            WHERE p.host_id = %s
            ORDER BY b.created_at DESC
        """, (host_id,))

        # Earnings summary
        earnings = db.fetch_one("""
            SELECT
                COALESCE(SUM(CASE WHEN b.status='confirmed'  THEN b.total_amount ELSE 0 END), 0) AS active_revenue,
                COALESCE(SUM(CASE WHEN b.status='completed'  THEN b.total_amount ELSE 0 END), 0) AS completed_revenue,
                COALESCE(SUM(CASE WHEN b.status IN ('confirmed','completed') THEN b.total_amount ELSE 0 END), 0) AS total_revenue,
                COUNT(CASE  WHEN b.status='confirmed'  THEN 1 END) AS active_count,
                COUNT(CASE  WHEN b.status='completed'  THEN 1 END) AS completed_count
            FROM bookings b
            JOIN properties p ON p.property_id = b.property_id
            WHERE p.host_id = %s
        """, (host_id,))

        # Host profile info
        user = db.fetch_one("SELECT * FROM users WHERE user_id=%s", (host_id,))

        db.close()

        return render_template(
            "host_dashboard.html",
            host_profile=host_profile,
            properties=properties,
            bookings=bookings,
            earnings=earnings,
            user=user,
        )

    # ── Host actions ────────────────────────────────────────────

    def host_update_profile(self):
        if session.get("role") != "host":
            return redirect(url_for("auth.host_dashboard"))

        user_id  = session.get("user_id")
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        phone    = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()

        db = Database()
        if password:
            from werkzeug.security import generate_password_hash
            db.execute(
                "UPDATE users SET name=%s, email=%s, phone=%s, password_hash=%s WHERE user_id=%s",
                (name, email, phone, generate_password_hash(password), user_id)
            )
        else:
            db.execute(
                "UPDATE users SET name=%s, email=%s, phone=%s WHERE user_id=%s",
                (name, email, phone, user_id)
            )
        session["user_name"] = name
        db.close()
        flash("Profile updated.", "success")
        return redirect(url_for("auth.host_dashboard"))

    def delete_property_host(self):
        if session.get("role") != "host":
            return redirect(url_for("auth.host_dashboard"))
        property_id = request.form.get("property_id")
        host_id     = session.get("user_id")
        db = Database()
        # Only delete if this host owns it
        db.execute(
            "DELETE FROM properties WHERE property_id=%s AND host_id=%s",
            (property_id, host_id)
        )
        db.close()
        flash("Property deleted.", "warning")
        return redirect(url_for("auth.host_dashboard"))

    # ════════════════════════════════════════════════════════════
    # BOOKING — create, cancel, review-cancel, mark-complete
    # ════════════════════════════════════════════════════════════

    def create_booking(self):
        """Guest creates a real booking. Replaces the old frontend-only flow."""
        if not self.is_logged_in():
            return jsonify({"error": "Please login first."}), 401
        if session.get("role") not in ("guest", "user"):
            return jsonify({"error": "Only guests can book."}), 403

        data = request.get_json(silent=True) or {}
        property_id  = data.get("property_id")
        checkin      = data.get("checkin_date")
        checkout     = data.get("checkout_date")
        guests       = data.get("guests_count")
        coupon_code  = (data.get("coupon_code") or "").strip().upper()
        guest_id     = session["user_id"]

        if not all([property_id, checkin, checkout, guests]):
            return jsonify({"error": "Missing required fields."}), 400

        db = Database()
        prop = db.fetch_one(
            "SELECT property_id, host_id, price_per_night, max_guests, title, "
            "approval_status, status FROM properties WHERE property_id=%s",
            (property_id,)
        )
        if not prop:
            db.close()
            return jsonify({"error": "Property not found."}), 404
        if prop["approval_status"] != "approved" or prop["status"] != "active":
            db.close()
            return jsonify({"error": "Property is not available for booking."}), 400

        try:
            guests_int = int(guests)
        except (TypeError, ValueError):
            db.close()
            return jsonify({"error": "Invalid guest count."}), 400
        if guests_int > int(prop["max_guests"]):
            db.close()
            return jsonify({"error": f"Maximum {prop['max_guests']} guests allowed."}), 400

        try:
            checkin_date  = datetime.strptime(checkin, "%Y-%m-%d").date()
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d").date()
        except ValueError:
            db.close()
            return jsonify({"error": "Invalid date format."}), 400
        if checkin_date >= checkout_date:
            db.close()
            return jsonify({"error": "Check-out must be after check-in."}), 400
        if checkin_date < datetime.now().date():
            db.close()
            return jsonify({"error": "Check-in date cannot be in the past."}), 400

        nights  = (checkout_date - checkin_date).days
        subtotal = nights * float(prop["price_per_night"])

        coupon_id = None
        discount_amount = 0.0
        if coupon_code:
            coupon = db.fetch_one(
                "SELECT coupon_id, type, value, expiry_date, active "
                "FROM coupons WHERE code=%s AND active=1",
                (coupon_code,)
            )
            if coupon and coupon["expiry_date"] and coupon["expiry_date"] < datetime.now().date():
                coupon = None
            if coupon:
                used = db.fetch_one(
                    "SELECT 1 FROM coupon_usage WHERE coupon_id=%s AND guest_id=%s",
                    (coupon["coupon_id"], guest_id)
                )
                if used:
                    db.close()
                    return jsonify({"error": "You have already used this coupon."}), 400
                coupon_id = coupon["coupon_id"]
                if coupon["type"] == "percentage":
                    discount_amount = subtotal * (float(coupon["value"]) / 100)
                elif coupon["type"] == "fixed":
                    discount_amount = min(float(coupon["value"]), subtotal)
            else:
                db.close()
                return jsonify({"error": "Invalid or expired coupon code."}), 400

        total_amount = max(subtotal - discount_amount, 0)
        booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # CHANGED: status from 'confirmed' to 'pending'
        db.execute(
            """INSERT INTO bookings
               (booking_id, guest_id, property_id, coupon_id, checkin_date, checkout_date,
                guests_count, total_amount, status, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', NOW())""",
            (booking_id, guest_id, property_id, coupon_id, checkin, checkout,
             guests_int, total_amount)
        )

        if coupon_id:
            db.execute(
                "INSERT INTO coupon_usage (coupon_id, guest_id, booking_id) VALUES (%s, %s, %s)",
                (coupon_id, guest_id, booking_id)
            )

        db.close()
        return jsonify({
            "success": True,
            "booking_id": booking_id,
            "total": float(total_amount),
            "nights": nights,
            "property_title": prop["title"],
        })

    def cancel_booking(self):
        """Guest requests cancellation; host must approve it."""
        if not self.is_logged_in():
            return jsonify({"error": "Please login first."}), 401
        if session.get("role") not in ("guest", "user"):
            return jsonify({"error": "Only guests can cancel."}), 403

        data = request.get_json(silent=True) or {}
        booking_id = data.get("booking_id")
        if not booking_id:
            return jsonify({"error": "Missing booking_id"}), 400

        guest_id = session["user_id"]
        db = Database()
        booking = db.fetch_one(
            "SELECT status, cancellation_status FROM bookings WHERE booking_id=%s AND guest_id=%s",
            (booking_id, guest_id)
        )
        if not booking:
            db.close()
            return jsonify({"error": "Booking not found."}), 404
        if booking["status"] in ("cancelled", "completed"):
            db.close()
            return jsonify({"error": "This booking cannot be cancelled."}), 400
        if booking["cancellation_status"] == "requested":
            db.close()
            return jsonify({"error": "Cancellation already requested."}), 400

        db.execute(
            "UPDATE bookings SET cancellation_status='requested' WHERE booking_id=%s",
            (booking_id,)
        )
        db.close()
        return jsonify({"success": True, "message": "Cancellation requested. Waiting for host approval."})

    def review_cancellation(self):
        """Host approves or rejects a guest's cancellation request."""
        if not self.is_logged_in():
            return jsonify({"error": "Please login first."}), 401
        if session.get("role") != "host":
            return jsonify({"error": "Only hosts can review cancellations."}), 403

        data = request.get_json(silent=True) or {}
        booking_id = data.get("booking_id")
        action     = data.get("action")
        host_id    = session["user_id"]

        if not booking_id or action not in ("approve", "reject"):
            return jsonify({"error": "Missing booking_id or invalid action."}), 400

        db = Database()
        booking = db.fetch_one(
            """SELECT b.* FROM bookings b
               JOIN properties p ON b.property_id = p.property_id
               WHERE b.booking_id=%s AND p.host_id=%s""",
            (booking_id, host_id)
        )
        if not booking:
            db.close()
            return jsonify({"error": "Booking not found or you are not the host."}), 404
        if booking["cancellation_status"] != "requested":
            db.close()
            return jsonify({"error": "No pending cancellation request for this booking."}), 400

        if action == "approve":
            db.execute(
                "UPDATE bookings SET status='cancelled', cancellation_status='approved' WHERE booking_id=%s",
                (booking_id,)
            )
            message = "Cancellation approved. Booking cancelled."
        else:
            db.execute(
                "UPDATE bookings SET cancellation_status='rejected' WHERE booking_id=%s",
                (booking_id,)
            )
            message = "Cancellation rejected. Booking remains active."

        db.close()
        return jsonify({"success": True, "message": message})

    def mark_booking_complete(self):
        """
        Host marks a confirmed stay as completed (after checkout).
        Without this, status never leaves 'confirmed' and 'completed_revenue'
        on the earnings dashboard would always show zero.
        """
        if not self.is_logged_in():
            return jsonify({"error": "Please login first."}), 401
        if session.get("role") != "host":
            return jsonify({"error": "Only hosts can do this."}), 403

        data = request.get_json(silent=True) or {}
        booking_id = data.get("booking_id")
        host_id = session["user_id"]
        if not booking_id:
            return jsonify({"error": "Missing booking_id"}), 400

        db = Database()
        booking = db.fetch_one(
            """SELECT b.status FROM bookings b
               JOIN properties p ON b.property_id = p.property_id
               WHERE b.booking_id=%s AND p.host_id=%s""",
            (booking_id, host_id)
        )
        if not booking:
            db.close()
            return jsonify({"error": "Booking not found or you are not the host."}), 404
        if booking["status"] != "confirmed":
            db.close()
            return jsonify({"error": "Only confirmed bookings can be marked complete."}), 400

        db.execute("UPDATE bookings SET status='completed' WHERE booking_id=%s", (booking_id,))
        db.close()
        return jsonify({"success": True, "message": "Booking marked as completed."})

    # ────────────────────────────────────────────────────────────
    # NEW: Confirm and Reject booking (host actions)
    # ────────────────────────────────────────────────────────────

    def confirm_booking(self):
        """Host confirms a pending booking."""
        if not self.is_logged_in() or session.get("role") != "host":
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        booking_id = data.get("booking_id")
        host_id = session["user_id"]

        if not booking_id:
            return jsonify({"error": "Missing booking_id"}), 400

        db = Database()
        booking = db.fetch_one(
            """SELECT b.status FROM bookings b
               JOIN properties p ON b.property_id = p.property_id
               WHERE b.booking_id=%s AND p.host_id=%s""",
            (booking_id, host_id)
        )
        if not booking:
            db.close()
            return jsonify({"error": "Booking not found or you are not the host."}), 404
        if booking["status"] != "pending":
            db.close()
            return jsonify({"error": "Only pending bookings can be confirmed."}), 400

        db.execute("UPDATE bookings SET status='confirmed' WHERE booking_id=%s", (booking_id,))
        db.close()
        return jsonify({"success": True, "message": "Booking confirmed."})

    def reject_booking(self):
        """Host rejects a pending booking (cancels it)."""
        if not self.is_logged_in() or session.get("role") != "host":
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        booking_id = data.get("booking_id")
        host_id = session["user_id"]

        if not booking_id:
            return jsonify({"error": "Missing booking_id"}), 400

        db = Database()
        booking = db.fetch_one(
            """SELECT b.status FROM bookings b
               JOIN properties p ON b.property_id = p.property_id
               WHERE b.booking_id=%s AND p.host_id=%s""",
            (booking_id, host_id)
        )
        if not booking:
            db.close()
            return jsonify({"error": "Booking not found or you are not the host."}), 404
        if booking["status"] != "pending":
            db.close()
            return jsonify({"error": "Only pending bookings can be rejected."}), 400

        db.execute("UPDATE bookings SET status='cancelled' WHERE booking_id=%s", (booking_id,))
        db.close()
        return jsonify({"success": True, "message": "Booking rejected and cancelled."})

    # ────────────────────────────────────────────────────────────
    # GUEST DASHBOARD
    # ────────────────────────────────────────────────────────────

    @role_required("guest", "user")
    def guest_dashboard(self):
        guest_id = session.get("user_id")
        db = Database()

        # Bookings grouped by status
        bookings = db.fetch_all("""
            SELECT b.*, p.title AS property_title, p.region, p.type
            FROM bookings b
            JOIN properties p ON p.property_id = b.property_id
            WHERE b.guest_id = %s
            ORDER BY b.created_at DESC
        """, (guest_id,))

        # Wishlist
        wishlist = db.fetch_all("""
            SELECT p.property_id, p.title, p.region, p.type, p.price_per_night
            FROM wishlist w
            JOIN properties p ON p.property_id = w.property_id
            WHERE w.user_id = %s
        """, (guest_id,))

        # Profile info
        user = db.fetch_one("SELECT * FROM users WHERE user_id=%s", (guest_id,))

        db.close()

        return render_template(
            "guest_dashboard.html",
            bookings=bookings,
            wishlist=wishlist,
            user=user,
        )

    # ── Guest actions ───────────────────────────────────────────

    def guest_update_profile(self):
        if not self.is_logged_in():
            return redirect(url_for("auth.login"))

        user_id  = session.get("user_id")
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        phone    = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()

        db = Database()
        if password:
            from werkzeug.security import generate_password_hash
            db.execute(
                "UPDATE users SET name=%s, email=%s, phone=%s, password_hash=%s WHERE user_id=%s",
                (name, email, phone, generate_password_hash(password), user_id)
            )
        else:
            db.execute(
                "UPDATE users SET name=%s, email=%s, phone=%s WHERE user_id=%s",
                (name, email, phone, user_id)
            )
        session["user_name"] = name
        db.close()
        flash("Profile updated.", "success")
        return redirect(url_for("auth.guest_dashboard"))

    # ════════════════════════════════════════════════════════════
    # WISHLIST — AJAX toggle
    # ════════════════════════════════════════════════════════════

    def toggle_wishlist(self):
        if not self.is_logged_in():
            return jsonify({"error": "login_required"}), 401

        user_id     = session.get("user_id")
        property_id = request.json.get("property_id") if request.is_json else request.form.get("property_id")

        db = Database()
        existing = db.fetch_one(
            "SELECT 1 FROM wishlist WHERE user_id=%s AND property_id=%s",
            (user_id, property_id)
        )
        if existing:
            db.execute(
                "DELETE FROM wishlist WHERE user_id=%s AND property_id=%s",
                (user_id, property_id)
            )
            action = "removed"
        else:
            db.execute(
                "INSERT IGNORE INTO wishlist (user_id, property_id) VALUES (%s,%s)",
                (user_id, property_id)
            )
            action = "added"
        db.close()
        return jsonify({"action": action, "property_id": property_id})

    def get_wishlist_ids(self):
        """Returns set of property_ids in this user's wishlist. Used by browse."""
        if not self.is_logged_in():
            return set()
        user_id = session.get("user_id")
        db = Database()
        rows = db.fetch_all(
            "SELECT property_id FROM wishlist WHERE user_id=%s", (user_id,)
        )
        db.close()
        return {r["property_id"] for r in rows}

    # ════════════════════════════════════════════════════════════
    # BROWSE — DB-driven
    # ════════════════════════════════════════════════════════════

    def browse(self):
        db = Database()
        # Only show approved properties on the public browse page
        properties = db.fetch_all("""
            SELECT p.*,
                   GROUP_CONCAT(DISTINCT a.name) AS amenity_list,
                   COALESCE(AVG(r.rating), 0)    AS avg_rating,
                   COUNT(DISTINCT b.booking_id)  AS booking_count
            FROM properties p
            LEFT JOIN property_amenities pa ON pa.property_id = p.property_id
            LEFT JOIN amenities          a  ON a.amenity_id   = pa.amenity_id
            LEFT JOIN reviews            r  ON r.property_id  = p.property_id
            LEFT JOIN bookings           b  ON b.property_id  = p.property_id
            WHERE p.approval_status = 'approved' AND p.status = 'active'
            GROUP BY p.property_id
            ORDER BY p.property_id ASC
        """)
        db.close()

        wishlist_ids = self.get_wishlist_ids()
        return render_template("browse.html", properties=properties, wishlist_ids=wishlist_ids)

    # ════════════════════════════════════════════════════════════
    # CONTACT — saves to DB
    # ════════════════════════════════════════════════════════════

    def contact(self):
        if request.method == "POST":
            name    = request.form.get("name", "").strip()
            email   = request.form.get("email", "").strip()
            subject = request.form.get("subject", "").strip()
            message = request.form.get("message", "").strip()

            if not name or not email or not subject or not message:
                flash("All fields are required.", "danger")
                return render_template("contact.html")

            db = Database()
            db.execute(
                "INSERT INTO support_queries (name, email, subject, message, status) VALUES (%s,%s,%s,%s,'open')",
                (name, email, subject, message)
            )
            db.close()
            flash("Your message has been sent. We'll get back to you soon!", "success")
            return redirect(url_for("auth.contact"))

        return render_template("contact.html")

    # ════════════════════════════════════════════════════════════
    # ADD PROPERTY — fixed column names to match actual schema
    # ════════════════════════════════════════════════════════════

    def add_property(self):
        if not self.is_logged_in():
            flash("Please login to add a property.", "warning")
            return redirect(url_for("auth.login"))

        if session.get("role") != "host":
            flash("Only hosts can add properties.", "warning")
            return redirect(url_for("auth.browse"))

        # Gate: unverified hosts cannot submit properties
        db = Database()
        host_profile = db.fetch_one(
            "SELECT verified FROM host_profiles WHERE user_id=%s",
            (session.get("user_id"),)
        )
        db.close()
        if not host_profile or not host_profile["verified"]:
            flash(
                "Your host account is still pending admin approval. "
                "You'll be able to add properties once approved.",
                "warning"
            )
            return redirect(url_for("auth.host_dashboard"))

        if request.method == "POST":
            title           = request.form.get("property_name", "").strip()
            prop_type       = request.form.get("property_type", "").strip()
            region          = request.form.get("region", "").strip()
            price_per_night = request.form.get("price_per_night", 0)
            max_guests      = request.form.get("max_guests", 1)

            if not title or not prop_type or not region or not price_per_night:
                flash("All required fields must be filled.", "danger")
                return render_template("add_property.html")

            try:
                db = Database()
                db.execute("""
                    INSERT INTO properties
                      (host_id, title, region, type, price_per_night, max_guests, status, approval_status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'active', 'pending')
                """, (
                    session.get("user_id"), title, region, prop_type,
                    price_per_night, max_guests
                ))
                db.close()
                flash("Property submitted for approval!", "success")
                return redirect(url_for("auth.host_dashboard"))
            except Exception as e:
                flash(f"Error adding property: {str(e)}", "danger")
                return render_template("add_property.html")

        return render_template("add_property.html")

    # ════════════════════════════════════════════════════════════
    # PASSWORD RESET (unchanged from original)
    # ════════════════════════════════════════════════════════════

    def forgot_password(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            if not email:
                flash("Please enter your email address.", "danger")
                return render_template("password_reset.html")

            user_data = self.user_model.find_by("email", email)
            if user_data:
                code = self._generate_code()
                self._save_reset_code(email, code)
                sent = send_reset_code(email, code)
                if not sent:
                    flash("Failed to send email. Please try again.", "danger")
                    return render_template("password_reset.html")

            return render_template("password_reset.html", sent=True, email=email)

        return render_template("password_reset.html")

    def verify_code(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        email = (request.args.get("email", "") or request.form.get("email", "")).strip().lower()

        if request.method == "POST":
            code = request.form.get("code", "").strip()
            if not code or len(code) != 6:
                flash("Please enter the full 6-digit code.", "danger")
                return render_template("verify_password.html", email=email)

            if self._verify_code(email, code):
                return redirect(url_for("auth.reset_password", email=email, code=code))

            flash("Invalid or expired code.", "danger")
            return render_template("verify_password.html", email=email)

        return render_template("verify_password.html", email=email)

    def reset_password(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        email = (request.args.get("email", "") or request.form.get("email", "")).strip().lower()
        code  = request.args.get("code", "") or request.form.get("code", "")

        if request.method == "GET":
            if not self._verify_code(email, code):
                flash("Reset link expired. Please request a new code.", "danger")
                return redirect(url_for("auth.forgot_password"))
            return render_template("update_password.html", email=email, code=code)

        password         = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("update_password.html", email=email, code=code)
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("update_password.html", email=email, code=code)
        if not self._verify_code(email, code):
            flash("Your reset code expired. Please request a new one.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user_data = self.user_model.find_by("email", email)
        if not user_data:
            flash("Account not found.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user = User.from_db(user_data)
        user.set_password(password)
        user.update(user_data["user_id"], update_password=True)
        self._mark_code_used(email, code)

        return self.flash_and_redirect(
            "Password updated! Please log in.", "success", "auth.login"
        )

    # ════════════════════════════════════════════════════════════
    # STATIC PAGES
    # ════════════════════════════════════════════════════════════

    def home(self):
        return render_template("home.html")

    def about(self):
        return render_template("about.html")

    def faq(self):
        return render_template("faq.html")

    def product_form(self):
        return render_template("product_form.html")

    # Property detail pages — kept as static templates for now.
    # When your teammate's add-property feature is done, replace with one
    # dynamic route: /property/<int:property_id>

    def property_mountain_view(self):
        return render_template("mountain_view.html")

    def property_thamel_heritage(self):
        return render_template("thamel_heritage.html")

    def property_jungle_retreat(self):
        return render_template("jungle_retreat.html")

    def property_lumbini_peace(self):
        return render_template("lumbini_peace.html")

    def property_mustang_desert(self):
        return render_template("mustang_desert.html")

    def property_lakeside_comfort(self):
        return render_template("lakeside_comfort.html")