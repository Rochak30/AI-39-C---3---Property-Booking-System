from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.logout"))
        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """
    Restrict a route to one or more roles.

    Usage:
        @role_required("admin")
        def admin_dashboard(self): ...

        @role_required("host", "admin")
        def some_shared_view(self): ...

    Behavior:
    - Not logged in          -> redirect to login
    - Logged in, wrong role  -> redirect SILENTLY to their own dashboard
                                 (no error flash)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("auth.login"))

            user_role = session.get("role")
            if user_role not in allowed_roles:
                return redirect(_role_home_url(user_role))

            return f(*args, **kwargs)
        return decorated
    return decorator


def _role_home_url(role):
    """Maps a role to its own dashboard endpoint."""
    if role == "admin":
        return url_for("auth.admin_dashboard")
    elif role == "host":
        return url_for("auth.host_dashboard")
    else:
        return url_for("auth.guest_dashboard")