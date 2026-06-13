from flask import render_template, request, flash, redirect, url_for, session
from app.controllers.basecontroller import BaseController
from app.models.usermodel import User


class AuthController(BaseController):
    def __init__(self):
        self.user_model = User()

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

            # Sanitize role — never allow self-registration as admin
            role = request.form.get("role", "user")
            if role not in ("guest", "host"):
                role = "user"

            print("NAME:", name)
            print("EMAIL:", email)
            print("PASSWORD:", password)
            print("ROLE:", role)

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
                # save() now returns the new user_id
                user_id = new_user.save()
                print("USER SAVED — user_id:", user_id)

                # ── If registering as host, save profile too ──
                if role == "host":
                    id_type      = request.form.get("id_type", "")
                    id_number    = request.form.get("id_number", "")
                    property_type = request.form.get("property_type", "")
                    payout_bank  = request.form.get("payout_bank", "")
                    host_address = request.form.get("host_address", "")
                    consent      = request.form.get("consent") == "true"

                    print("HOST FIELDS:", id_type, id_number, property_type,
                          payout_bank, host_address, consent)

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

    def forgot_password(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip()

            if not email:
                flash("Please enter your email address.", "danger")
                return render_template("password_reset.html")

            user_data = self.user_model.find_by("email", email)

            if user_data:
                print(f"RESET REQUESTED for existing user: {email}")
            else:
                print(f"RESET REQUESTED for unknown email: {email}")

            flash(
                f"If an account exists for {email}, a reset link has been sent.",
                "success",
            )
            return render_template("password_reset.html")

        return render_template("password_reset.html")

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
            name = request.form.get("name")
            description = request.form.get("description")
            price = request.form.get("price")
            category = request.form.get("category")
            stock = request.form.get("stock")
            print(name, description, price, category, stock)
        return render_template("product_form.html")

    def logout(self):
        session.pop("user_id", None)
        session.pop("user_name", None)
        session.pop("role", None)
        flash("Logged out successfully.", "success")
        return redirect(url_for("auth.login"))