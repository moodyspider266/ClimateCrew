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
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        # Create users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def hash_password(self, password):
        # Simple password hashing using SHA-256
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, email):
        try:
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