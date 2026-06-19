"""
=============================================================
  OOP Concept: INHERITANCE, ENCAPSULATION & POLYMORPHISM
=============================================================
  - Inheritance: User inherits from BaseModel, so it gets find_by_id(), find_all(), delete_by_id() for FREE.
  - Encapsulation: Password is kept private (__password). Outside code cannot access user.__password directly.
    We use a setter method to control how it's changed.
  - Polymorphism: User defines its own 'table' property, which overrides the abstract one from BaseModel.
    Same interface, different behavior = polymorphism.
=============================================================
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.models.basemodel import BaseModel
from .database import Database


class User(BaseModel):

    @property
    def table(self):
        return "users"

    def __init__(self, name=None, email=None, password=None, role="user"):
        self.name = name
        self.email = email
        self.__password = None
        self.role = role
        if password:
            self.set_password(password)

    # ── Encapsulation: Password Methods ─────────────────────

    def set_password(self, plain_password):
        self.__password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        if self.__password is None:
            return False
        return check_password_hash(self.__password, plain_password)

    # ── Create ───────────────────────────────────────────────

    def save(self, phone=None):
        """Insert user row and return the new user_id."""
        db = Database()
        user_id = db.execute_get_id(
            "INSERT INTO users (name, email, password_hash, role, phone) VALUES (%s, %s, %s, %s, %s)",
            (self.name, self.email, self.__password, self.role, phone),
        )
        db.close()
        return user_id  # ✅ caller uses this for host_profiles

    def save_host_profile(self, user_id, id_type, id_number, property_type,
                          payout_bank, host_address, consent):
        """Insert a host_profiles row linked to the given user_id."""
        db = Database()
        db.execute(
            """INSERT INTO host_profiles
               (user_id, id_type, id_number, property_type, payout_bank, host_address, consent)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, id_type, id_number, property_type, payout_bank, host_address, consent),
        )
        db.close()

    # ── Update ───────────────────────────────────────────────

    def update(self, user_id, update_password=False):
        db = Database()
        if update_password:
            db.execute(
                "UPDATE users SET name=%s, email=%s, password_hash=%s, role=%s WHERE user_id=%s",
                (self.name, self.email, self.__password, self.role, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET name=%s, email=%s, role=%s WHERE user_id=%s",
                (self.name, self.email, self.role, user_id),
            )
        db.close()

    def update_profile(self, user_id, update_password=False):
        db = Database()
        if update_password:
            db.execute(
                "UPDATE users SET name=%s, email=%s, password_hash=%s WHERE user_id=%s",
                (self.name, self.email, self.__password, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET name=%s, email=%s WHERE user_id=%s",
                (self.name, self.email, user_id),
            )
        db.close()

    # ── Helpers ──────────────────────────────────────────────

    def email_exists(self, exclude_id=None):
        db = Database()
        if exclude_id:
            result = db.fetch_one(
                "SELECT user_id FROM users WHERE email = %s AND user_id != %s",
                (self.email, exclude_id),
            )
        else:
            result = db.fetch_one(
                "SELECT user_id FROM users WHERE email = %s", (self.email,)
            )
        db.close()
        return result is not None

    @classmethod
    def from_db(cls, data):
        if data is None:
            return None
        user = cls()
        user.name = data["name"]
        user.email = data["email"]
        user._User__password = data["password_hash"]
        user.role = data["role"]
        return user

    def __str__(self):
        return f"User(name={self.name}, email={self.email}, role={self.role})"

    def __repr__(self):
        return f"<User email={self.email}>"