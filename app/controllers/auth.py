import email

from flask import render_template, request, flash, redirect, url_for, session
from app.controllers.basecontroller import BaseController
from app.models.usermodel import User
from app.models.database import Database
from app.services.email_service import send_reset_code
import random
import string
from datetime import datetime, timedelta


class AuthController(BaseController):
    def __init__(self):
        self.user_model = User()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _generate_code(self):
        """Generate a random 6-digit numeric code."""
        return ''.join(random.choices(string.digits, k=6))

    def _save_reset_code(self, email, code):
        """Store the code in password_resets, invalidating any previous ones."""
        db = Database()
        # Mark any existing unused codes for this email as used
        db.execute(
            "UPDATE password_resets SET used = TRUE WHERE email = %s AND used = FALSE",
            (email,)
        )
        # Insert new code with 10-minute expiry
        expires_at = datetime.now() + timedelta(minutes=10)
        db.execute(
            "INSERT INTO password_resets (email, code, expires_at) VALUES (%s, %s, %s)",
            (email, code, expires_at)
        )
        db.close()

    def _verify_code(self, email, code):
        """
        Check the code is valid, unused, and not expired.
        Returns True/False.
        """
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
        """Mark the code as used after successful password reset."""
        db = Database()
        db.execute(
            "UPDATE password_resets SET used = TRUE WHERE email = %s AND code = %s",
            (email, code)
        )
        db.close()

    # ── Auth Routes ──────────────────────────────────────────────────────────

    def login(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            print("EMAIL:", email)
            print("PASSWORD:", password)

            user_data = self.user_model.find_by("email", email)
            print("USER DATA:", user_data)

            if user_data:
                user = User.from_db(user_data)
                result = user.check_password(password)
                print("PASSWORD CHECK:", result)

                if result:
                    print("LOGIN SUCCESS")
                    session["user_id"] = user_data["user_id"]
                    session["user_name"] = user_data["name"]
                    session["role"] = user_data["role"]
                    return redirect(url_for("auth.dashboard"))

            print("LOGIN FAILED")
            flash("Invalid email or password.", "danger")

        return render_template("login.html")

    def dashboard(self):
        return render_template("dashboard.html")

    def register(self):
        print("REGISTER METHOD CALLED")
        print("Request method:", request.method)

        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            name, email = self.get_form_data("name", "email")
            password = request.form.get("password", "")

            role = request.form.get("role", "user")
            if role not in ("guest", "host"):
                role = "user"

            print("NAME:", name, "EMAIL:", email, "ROLE:", role)

            if not name or not email or not password:
                flash("All fields are required.", "danger")
                return render_template("register.html")
            if len(name) > 100:
                flash("Name must be under 100 characters.", "danger")
                return render_template("register.html")
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("register.html")

            new_user = User(name=name, email=email, password=password, role=role)

            if new_user.email_exists():
                flash("Email already exists.", "danger")
                return render_template("register.html")

            try:
                user_id = new_user.save()
                print("USER SAVED — user_id:", user_id)

                if role == "host":
                    id_type       = request.form.get("id_type", "")
                    id_number     = request.form.get("id_number", "")
                    property_type = request.form.get("property_type", "")
                    payout_bank   = request.form.get("payout_bank", "")
                    host_address  = request.form.get("host_address", "")
                    consent       = request.form.get("consent") == "true"

                    new_user.save_host_profile(
                        user_id, id_type, id_number, property_type,
                        payout_bank, host_address, consent
                    )
                    print("HOST PROFILE SAVED")

            except Exception as e:
                print("SAVE ERROR:", e)
                flash("Registration failed: " + str(e), "danger")
                return render_template("register.html")

            return self.flash_and_redirect(
                "Registration successful! Please login.", "success", "auth.login"
            )

        return render_template("register.html")

    # ── Password Reset — Step 1: Request code ────────────────────────────────

    def forgot_password(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()

            if not email:
                flash("Please enter your email address.", "danger")
                return render_template("password_reset.html")

            # Always show success UI — don't reveal whether email exists
            user_data = self.user_model.find_by("email", email)
            if user_data:
                code = self._generate_code()
                self._save_reset_code(email, code)
                sent = send_reset_code(email, code)
                if not sent:
                    flash("Failed to send email. Please try again.", "danger")
                    return render_template("password_reset.html")
                print(f"RESET CODE for {email}: {code}")  # visible in terminal for testing

            # Show success state regardless (security: don't leak which emails exist)
            return render_template("password_reset.html", sent=True, email=email)

        return render_template("password_reset.html")

    # ── Password Reset — Step 2: Verify code ─────────────────────────────────

    def verify_code(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        email = request.args.get("email", "") or request.form.get("email", "")
        email = email.strip().lower()

        if request.method == "POST":
            code = request.form.get("code", "").strip()
            print("VERIFY POST — email:", repr(email), "code:", repr(code))  # ADD THIS

            if not code or len(code) != 6:
                flash("Please enter the full 6-digit code.", "danger")
                return render_template("verify_password.html", email=email)

            result = self._verify_code(email, code)
            print("VERIFY RESULT:", result)  # ADD THIS

            if result:
                return redirect(url_for("auth.reset_password", email=email, code=code))
            else:
                flash("Invalid or expired code. Please try again or request a new one.", "danger")
                return render_template("verify_password.html", email=email)

        return render_template("verify_password.html", email=email)

    # ── Password Reset — Step 3: Set new password ─────────────────────────────

    def reset_password(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        email = request.args.get("email", "") or request.form.get("email", "")
        code  = request.args.get("code", "")  or request.form.get("code", "")
        email = email.strip().lower()

        # If arriving via GET, re-verify code is still valid
        if request.method == "GET":
            if not self._verify_code(email, code):
                flash("This reset link has expired. Please request a new code.", "danger")
                return redirect(url_for("auth.forgot_password"))
            return render_template("update_password.html", email=email, code=code)

        if request.method == "POST":
            password         = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not password or len(password) < 8:
                flash("Password must be at least 8 characters.", "danger")
                return render_template("update_password.html", email=email, code=code)

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("update_password.html", email=email, code=code)

            # Final re-check the code hasn't expired between GET and POST
            if not self._verify_code(email, code):
                flash("Your reset code expired. Please request a new one.", "danger")
                return redirect(url_for("auth.forgot_password"))

            # Update password in DB
            user_data = self.user_model.find_by("email", email)
            if not user_data:
                flash("Account not found.", "danger")
                return redirect(url_for("auth.forgot_password"))

            user = User.from_db(user_data)
            user.set_password(password)
            user.update(user_data["user_id"], update_password=True)

            # Mark code as used so it can't be reused
            self._mark_code_used(email, code)

            print(f"PASSWORD RESET SUCCESS for {email}")
            return self.flash_and_redirect(
                "Password updated! Please log in with your new password.",
                "success", "auth.login"
            )

    # ── Other Routes ──────────────────────────────────────────────────────────

    def about(self):
        return render_template("about.html")

    def browse(self):
        return render_template("browse.html")

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

    def faq(self):
        return render_template("faq.html")

    def home(self):
        return render_template("home.html")

    def contact(self):
        return render_template("contact.html")

    def product_form(self):
        if request.method == "POST":
            print(request.form)
            name        = request.form.get("name")
            description = request.form.get("description")
            price       = request.form.get("price")
            category    = request.form.get("category")
            stock       = request.form.get("stock")
            print(name, description, price, category, stock)
        return render_template("product_form.html")

    # Add this method to your AuthController class

    def add_property(self):
        """Route for adding a new property - HOSTS ONLY."""
        # Check if user is logged in
        if not self.is_logged_in():
            flash("Please login to add a property.", "warning")
            return redirect(url_for("auth.login"))
        
        # Check if user is a host
        if session.get('role') != 'host':
            flash("⚠️ Only hosts can add properties. Please register as a host.", "warning")
            return redirect(url_for("auth.browse"))
        
        if request.method == "POST":
            # Get form data
            property_name = request.form.get("property_name")
            property_type = request.form.get("property_type")
            region = request.form.get("region")
            address = request.form.get("address")
            tagline = request.form.get("tagline")
            description = request.form.get("description")
            price_per_night = request.form.get("price_per_night")
            amenities = request.form.getlist("amenities")
            max_guests = request.form.get("max_guests")
            bedrooms = request.form.get("bedrooms")
            bathrooms = request.form.get("bathrooms")
            checkin_time = request.form.get("checkin_time")
            checkout_time = request.form.get("checkout_time")
            host_bio = request.form.get("host_bio")
            host_languages = request.form.get("host_languages")
            response_time = request.form.get("response_time")
            additional_rules = request.form.get("additional_rules")
            rules = request.form.getlist("rules")
            
            # Validate required fields
            if not all([property_name, property_type, region, address, tagline, description, price_per_night]):
                flash("All required fields must be filled.", "danger")
                return render_template("add_property.html")
            
            try:
                # Insert property into database
                db = Database()
                user_id = session.get("user_id")
                
                # Convert lists to comma-separated strings
                amenities_str = ','.join(amenities) if amenities else ''
                rules_str = ','.join(rules) if rules else ''
                
                # Handle image uploads
                images = request.files.getlist("images")
                image_filenames = []
                
                # Create upload directory if it doesn't exist
                import os
                upload_dir = os.path.join('app', 'static', 'images', 'properties')
                os.makedirs(upload_dir, exist_ok=True)
                
                for idx, image in enumerate(images):
                    if image and image.filename:
                        # Generate unique filename
                        import time
                        ext = image.filename.rsplit('.', 1)[1].lower() if '.' in image.filename else 'jpg'
                        filename = f"property_{user_id}_{int(time.time())}_{idx}.{ext}"
                        filepath = os.path.join(upload_dir, filename)
                        image.save(filepath)
                        image_filenames.append(filename)
                
                # Store images as comma-separated string
                images_str = ','.join(image_filenames) if image_filenames else ''
                
                query = """
                    INSERT INTO properties 
                    (user_id, property_name, property_type, region, address, tagline, description, 
                    price_per_night, amenities, max_guests, bedrooms, bathrooms, 
                    checkin_time, checkout_time, images, rules, additional_rules,
                    host_bio, host_languages, response_time, created_at, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                """
                
                db.execute(query, (
                    user_id, property_name, property_type, region, address, tagline, description,
                    price_per_night, amenities_str, max_guests or 2, bedrooms or 1, bathrooms or 1,
                    checkin_time or '15:00', checkout_time or '12:00', images_str, rules_str,
                    additional_rules, host_bio, host_languages, response_time or 'Within 1 hour',
                    'pending'  # Status: pending review
                ))
                db.close()
                
                flash("✅ Property added successfully! It will be reviewed by our team before going live.", "success")
                return redirect(url_for("auth.browse"))
                
            except Exception as e:
                print("ERROR adding property:", e)
                flash(f"Error adding property: {str(e)}", "danger")
                return render_template("add_property.html")
        
        # GET request - show the form
        return render_template("add_property.html")

    def logout(self):
        session.pop("user_id", None)
        session.pop("user_name", None)
        session.pop("role", None)
        flash("Logged out successfully.", "success")
        return redirect(url_for("auth.login"))