import unittest
import sqlite3
import main  # your kivy main app
from kivy.uix.screenmanager import ScreenManager
from kivy.base import EventLoop
import hashlib


class TestAppUI(unittest.TestCase):
    def setUp(self):
        EventLoop.ensure_window()
        self.conn = sqlite3.connect("user_auth.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM users")  # Clean DB before each test
        self.conn.commit()

    def hash_password(self, password):
        # Simple password hashing using SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def tearDown(self):
        self.conn.close()

    def test_successful_user_registration(self):
        conn = sqlite3.connect("user_auth.db")
        cursor = conn.cursor()

        email, password = "testuser@example.com", "mypassword123"
        password = self.hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        self.assertIsNotNone(user, "User should be registered successfully")
        self.assertEqual(user[1], email)

        conn.close()

    def test_login_success(self):
        email, password = "loginuser@example.com", "securepass"
        password = self.hash_password(password)
        self.cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password))
        self.conn.commit()

        self.cursor.execute(
            "SELECT * FROM users WHERE email=? AND password_hash=?", (email, password))
        user = self.cursor.fetchone()
        self.assertIsNotNone(
            user, "User should be able to log in with correct credentials")
        self.assertEqual(user[1], email)
        self.assertEqual(user[2], password)

    def test_duplicate_registration(self):
        email = "dup@example.com"
        password = "pass123"
        password = self.hash_password(password)
        self.cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password))
        self.conn.commit()

        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password))
            self.conn.commit()


if __name__ == '__main__':
    unittest.main()
