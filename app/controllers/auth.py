from flask import render_template, request, redirect, url_for


class AuthController:

    # HOME
    def home(self):
        if request.method == "POST":
            print(request.form)

        return render_template("home.html")

    # LOGIN
    def login(self):

        if request.method == "POST":
            print(request.form)

            # Example redirect after login
            return redirect(url_for("auth.home"))

        return render_template("login.html")

    # REGISTER
    def register(self):

        if request.method == "POST":
            print(request.form)

            # Example redirect
            return redirect(url_for("auth.login"))

        return render_template("register.html")

    # ABOUT
    def about(self):

        products = [
            {"name": "iPhone 15", "price": 999, "model": "A3090"},
            {"name": "Samsung Galaxy S24", "price": 899, "model": "SM-S921B"},
            {"name": "MacBook Air", "price": 1299, "model": "M2"},
            {"name": "Dell XPS 13", "price": 1199, "model": "9320"},
            {"name": "Sony WH-1000XM4", "price": 349, "model": "XM4"},
            {"name": "iPad Pro", "price": 1099, "model": "6th Gen"},
            {"name": "Acer Nitro V15", "price": 1399, "model": "ANV15"}
        ]

        return render_template(
            "about.html",
            products=products
        )

    # CONTACT
    def contact(self):

        if request.method == "POST":
            print(request.form)

        return render_template("contact.html")

    # BROWSE
    def browse(self):
        return render_template("browse.html")

    # PROPERTY DETAIL
    def property_detail(self, prop_id):
        return render_template(
            "property_detail.html",
            prop_id=prop_id
        )

    # BOOKING CONFIRM
    def booking_confirm(self):
        return render_template("booking_confirm.html")

    # PASSWORD RESET
    def password_reset(self):

        if request.method == "POST":
            print(request.form)
            return redirect(url_for("auth.login"))

        return render_template("password_reset.html")

    # LOGOUT
    def logout(self):
        return redirect(url_for("auth.home"))

    # DASHBOARDS
    def guest_dashboard(self):
        return render_template("guest_dashboard.html")

    def host_dashboard(self):
        return render_template("host_dashboard.html")

    # ADMIN
    def admin(self):
        return render_template("admin.html")

    # FAQ
    def faq(self):
        return render_template("faq.html")