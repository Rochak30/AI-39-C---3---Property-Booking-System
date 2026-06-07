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

                    session["user_id"] = user_data["id"]
                    session["user_name"] = user_data["name"]
                    session["role"] = user_data["role"]

                    return redirect(url_for("auth.dashboard"))

            print("LOGIN FAILED")
            flash("Invalid email or password.", "danger")

        return render_template("login.html")

    def dashboard(self):
        # if not self.is_logged_in():
        #     return redirect(url_for("auth.login"))
        return render_template("dashboard.html")

    def register(self):
        print("REGISTER METHOD CALLED")
        print("Request method:", request.method)

        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            name, email = self.get_form_data("name", "email")
            password = request.form.get("password", "")

            print("NAME:", name)
            print("EMAIL:", email)
            print("PASSWORD:", password)

            if not name or not email or not password:
                print("FAILED: missing fields")
                flash("All fields are required.", "danger")
                return render_template("register.html")

            if len(name) > 100:
                print("FAILED: name too long")
                flash("Name must be under 100 characters.", "danger")
                return render_template("register.html")

            if len(password) < 6:
                print("FAILED: password too short")
                flash("Password must be at least 6 characters.", "danger")
                return render_template("register.html")

            new_user = User(name=name, email=email, password=password, role="user")
            print("USER CREATED:", new_user)

            print("CHECKING EMAIL...")
            if new_user.email_exists():
                print("FAILED: email exists")
                flash("Email already exists.", "danger")
                return render_template("register.html")

            print("SAVING USER...")
            try:
                new_user.save()
                print("SAVED SUCCESSFULLY")
            except Exception as e:
                print("SAVE ERROR:", e)
                flash("Registration failed: " + str(e), "danger")
                return render_template("register.html")

            return self.flash_and_redirect(
                "Registration successful! Please login.", "success", "auth.login"
            )

        return render_template("register.html")

    def forgot_password(self):
        """
        GET  /forgot-password  — show the reset-request form
        POST /forgot-password  — look up the email and (in production)
                                 send a reset link; flash success either
                                 way so we don't reveal whether the email
                                 exists (security best practice).
        """
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip()

            if not email:
                flash("Please enter your email address.", "danger")
                return render_template("password_reset.html")

            # Look up the user (but don't reveal whether they exist)
            user_data = self.user_model.find_by("email", email)

            if user_data:
                # TODO: generate a signed token, store it, and email the link.
                # Example (requires itsdangerous + an email utility):
                #
                #   token = generate_reset_token(email)
                #   reset_url = url_for("auth.reset_password", token=token, _external=True)
                #   send_reset_email(email, reset_url)
                #
                print(f"RESET REQUESTED for existing user: {email}")
            else:
                # Still succeed silently — never reveal missing accounts
                print(f"RESET REQUESTED for unknown email: {email}")

            # Always show the same success message
            flash(
                f"If an account exists for {email}, a reset link has been sent.",
                "success",
            )
            return render_template("password_reset.html")

        return render_template("password_reset.html")

    def about(self):
        return render_template("about.html")

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