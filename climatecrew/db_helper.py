import sqlite3
import os
import hashlib


class DatabaseHelper:
    def __init__(self, db_name="user_auth.db"):
        # Get the app directory for database storage
        self.db_path = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

        return self.conn  # Return the connection

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        # Create users table (if not already created)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create user_profiles table linked to users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                email TEXT,
                contact TEXT,
                city TEXT,
                country TEXT,
                occupation TEXT,
                profile_image BLOB,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        self.conn.commit()

    def hash_password(self, password):
        # Simple password hashing using SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, email):
        try:
            print(username)
            password_hash = self.hash_password(password)
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Username or email already exists
            return False

    def authenticate_user(self, username, password):
        password_hash = self.hash_password(password)
        self.cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = self.cursor.fetchone()
        return user is not None

    def get_user_profile(self, user_id):
        """Get user profile data"""
        conn = self.connect()
        cursor = conn.cursor()

        # First try to get from user_profiles
        cursor.execute('''
            SELECT user_id, full_name, username, email, contact, city, country, occupation, profile_image 
            FROM user_profiles WHERE user_id = ?
        ''', (user_id,))

        profile = cursor.fetchone()

        if not profile:
            # Profile doesn't exist, get basic info from users table
            cursor.execute(
                'SELECT id, "", username, email FROM users WHERE id = ?', (user_id,))
            basic_info = cursor.fetchone()

            if basic_info:
                # Create empty profile with basic info
                user_id, _, username, email = basic_info
                cursor.execute('''
                    INSERT INTO user_profiles (user_id, full_name, username, email)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, "", username, email))
                conn.commit()
                # Return the new profile
                profile = (user_id, "", username, email, "", "", "", "", None)

        cursor.close()
        conn.close()

        return profile

    def update_user_profile(self, user_id, contact=None, city=None, country=None, occupation=None, profile_image=None):
        """Update user profile data"""
        conn = self.connect()
        cursor = conn.cursor()

        # Build the update query dynamically based on provided fields
        update_fields = []
        values = []

        if contact is not None:
            update_fields.append("contact = ?")
            values.append(contact)

        if city is not None:
            update_fields.append("city = ?")
            values.append(city)

        if country is not None:
            update_fields.append("country = ?")
            values.append(country)

        if occupation is not None:
            update_fields.append("occupation = ?")
            values.append(occupation)

        if profile_image is not None:
            update_fields.append("profile_image = ?")
            values.append(profile_image)

        if not update_fields:
            cursor.close()
            conn.close()
            return False

        # Add user_id to values list
        values.append(user_id)

        query = f'''
            UPDATE user_profiles 
            SET {', '.join(update_fields)}
            WHERE user_id = ?
        '''

        cursor.execute(query, values)
        conn.commit()

        success = cursor.rowcount > 0

        cursor.close()
        conn.close()

        return success
