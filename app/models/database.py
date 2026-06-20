import pymysql
import config


class Database:

    def __init__(self):
        """Open a database connection when object is created."""
        try:
            self.__connection = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
            )
            print("Database connected successfully!")
        except pymysql.MySQLError as e:
            print("Database connection failed!")
            print("Error:", e)

    def fetch_one(self, query, params=None):
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results

    def execute(self, query, params=None):
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        self.__connection.commit()
        cursor.close()

    def execute_get_id(self, query, params=None):
        """Execute an INSERT and return the new row's auto-increment ID."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        self.__connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def close(self):
        self.__connection.close()

    @staticmethod
    def create_tables():
        db = Database()

        # ── USERS ─────────────────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       INT AUTO_INCREMENT PRIMARY KEY,
                name          VARCHAR(100)  NOT NULL,
                email         VARCHAR(100)  NOT NULL UNIQUE,
                password_hash VARCHAR(255)  NOT NULL,
                role          VARCHAR(20)   NOT NULL DEFAULT 'user',
                registered_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── PASSWORD RESETS ──────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id         INT AUTO_INCREMENT PRIMARY KEY,
                email      VARCHAR(100) NOT NULL,
                code       VARCHAR(6)   NOT NULL,
                expires_at DATETIME     NOT NULL,
                used       BOOLEAN      NOT NULL DEFAULT FALSE,
                created_at DATETIME     DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email)
            )
        """)

        # ── AMENITIES ─────────────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS amenities (
                amenity_id INT AUTO_INCREMENT PRIMARY KEY,
                name       VARCHAR(100) NOT NULL UNIQUE
            )
        """)

        # ── PROPERTIES ────────────────────────────────────────────────────────
        # All columns included – no need for later ALTER TABLE
        db.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                property_id         INT AUTO_INCREMENT PRIMARY KEY,
                host_id             INT            NOT NULL,
                title               VARCHAR(200)   NOT NULL,
                region              VARCHAR(100)   NOT NULL,
                type                VARCHAR(50)    NOT NULL,
                price_per_night     DECIMAL(10,2)  NOT NULL,
                max_guests          INT            NOT NULL DEFAULT 1,
                status              VARCHAR(20)    NOT NULL DEFAULT 'active',
                approval_status     VARCHAR(20)    DEFAULT 'pending',
                description         TEXT,
                description_2       TEXT,
                tagline             VARCHAR(255),
                address             TEXT,
                checkin_time        TIME,
                checkout_time       TIME,
                prepayment_amount   DECIMAL(10,2),
                free_cancellation_days INT DEFAULT 7,
                nonrefundable_hours INT DEFAULT 72,
                breakfast_time      TIME,
                map_embed_url       TEXT,
                latitude            DECIMAL(10,8),
                longitude           DECIMAL(11,8),
                bedrooms            INT DEFAULT 1,
                bathrooms           INT DEFAULT 1,
                amenities           TEXT,
                highlights          TEXT,
                inclusions          TEXT,
                rules               TEXT,
                additional_rules    TEXT,
                images              TEXT,
                host_bio            TEXT,
                host_languages      VARCHAR(100),
                years_hosting       INT,
                response_rate       INT,
                response_time       VARCHAR(50),
                host_avatar         VARCHAR(255),
                CONSTRAINT fk_property_host
                    FOREIGN KEY (host_id) REFERENCES users(user_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

        # ── HOST_PROFILES ─────────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS host_profiles (
                host_profile_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id         INT          NOT NULL UNIQUE,
                id_type         VARCHAR(50)  NOT NULL,
                id_number       VARCHAR(100) NOT NULL,
                property_type   VARCHAR(50)  NOT NULL,
                payout_bank     VARCHAR(200) NOT NULL,
                host_address    TEXT         NOT NULL,
                consent         BOOLEAN      NOT NULL DEFAULT FALSE,
                verified        BOOLEAN      NOT NULL DEFAULT FALSE,
                created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_hp_user
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

        # ── PROPERTY_AMENITIES ────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS property_amenities (
                property_id INT NOT NULL,
                amenity_id  INT NOT NULL,
                PRIMARY KEY (property_id, amenity_id),
                CONSTRAINT fk_pa_property
                    FOREIGN KEY (property_id) REFERENCES properties(property_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_pa_amenity
                    FOREIGN KEY (amenity_id) REFERENCES amenities(amenity_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

        # ── WISHLIST ──────────────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                user_id     INT NOT NULL,
                property_id INT NOT NULL,
                PRIMARY KEY (user_id, property_id),
                CONSTRAINT fk_wl_user
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_wl_property
                    FOREIGN KEY (property_id) REFERENCES properties(property_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

        # ── COUPONS ───────────────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_id   INT AUTO_INCREMENT PRIMARY KEY,
                code        VARCHAR(50)    NOT NULL UNIQUE,
                type        VARCHAR(20)    NOT NULL,
                value       DECIMAL(10,2)  NOT NULL,
                expiry_date DATE           NOT NULL,
                active      BOOLEAN        NOT NULL DEFAULT TRUE
            )
        """)

        # ── BOOKINGS ──────────────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id    VARCHAR(30)   NOT NULL PRIMARY KEY,
                guest_id      INT           NOT NULL,
                property_id   INT           NOT NULL,
                coupon_id     INT           DEFAULT NULL,
                checkin_date  DATE          NOT NULL,
                checkout_date DATE          NOT NULL,
                guests_count  INT           NOT NULL DEFAULT 1,
                total_amount  DECIMAL(10,2) NOT NULL,
                status        VARCHAR(20)   NOT NULL DEFAULT 'pending',
                created_at    DATETIME      DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_bk_guest
                    FOREIGN KEY (guest_id) REFERENCES users(user_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_bk_property
                    FOREIGN KEY (property_id) REFERENCES properties(property_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_bk_coupon
                    FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id)
                    ON DELETE SET NULL ON UPDATE CASCADE
            )
        """)

        # ── REVIEWS ───────────────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id   INT AUTO_INCREMENT PRIMARY KEY,
                booking_id  VARCHAR(30)  NOT NULL,
                guest_id    INT          NOT NULL,
                property_id INT          NOT NULL,
                rating      INT          NOT NULL CHECK (rating BETWEEN 1 AND 5),
                comment     TEXT,
                created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_rv_booking
                    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_rv_guest
                    FOREIGN KEY (guest_id) REFERENCES users(user_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_rv_property
                    FOREIGN KEY (property_id) REFERENCES properties(property_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

        # ── SUPPORT_QUERIES ───────────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS support_queries (
                query_id   INT AUTO_INCREMENT PRIMARY KEY,
                name       VARCHAR(100) NOT NULL,
                email      VARCHAR(100) NOT NULL,
                subject    VARCHAR(200) NOT NULL,
                message    TEXT,
                status     VARCHAR(20)  NOT NULL DEFAULT 'open',
                created_at DATETIME     DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── SEED: default admin user ──────────────────────────────────────────
        admin = db.fetch_one(
            "SELECT * FROM users WHERE email = %s", ("admin@admin.com",)
        )
        if not admin:
            from werkzeug.security import generate_password_hash

            db.execute(
                """INSERT INTO users (name, email, password_hash, role)
                   VALUES (%s, %s, %s, %s)""",
                (
                    "Admin",
                    "admin@admin.com",
                    generate_password_hash("admin123"),
                    "admin",
                ),
            )
            print("Default admin user created.")

        db.close()
        print("All tables created successfully.")