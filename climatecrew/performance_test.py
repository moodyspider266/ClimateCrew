import sqlite3
import time
import requests
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
import hashlib


# # 1. Database Performance Test
# def test_database_performance():
#     conn = sqlite3.connect("user_auth.db")
#     cursor = conn.cursor()

#     def hash_password(password):
#         # Simple password hashing using SHA-256
#         return hashlib.sha256(password.encode()).hexdigest()

#     password = "test123"
#     password = hash_password(password)
#     # Insert performance test
#     start_time = time.time()
#     cursor.execute("INSERT INTO users (username ,email, password_hash) VALUES (?, ?, ?)",
#                    ("moodyspider266", "performancetest@example.com", password))
#     conn.commit()
#     insert_time = time.time() - start_time

#     # Fetch performance test
#     start_time = time.time()
#     cursor.execute("SELECT * FROM users WHERE email = ?",
#                    ("performancetest@example.com",))
#     user = cursor.fetchone()
#     fetch_time = time.time() - start_time

#     conn.close()
#     print(
#         f"[DB Test] Insert Time: {insert_time:.4f} sec | Fetch Time: {fetch_time:.4f} sec")


# # 2. UI Performance Test
# class TestScreen(Screen):
#     def on_enter(self):
#         start_time = time.time()

#         def on_complete(dt):
#             render_time = time.time() - start_time
#             print(f"[UI Test] UI Render Time: {render_time:.4f} sec")

#         Clock.schedule_once(on_complete, 0)


# class TestApp(App):
#     def build(self):
#         sm = ScreenManager()
#         sm.add_widget(TestScreen(name="test_screen"))
#         return sm


# 3. API Performance Test
def test_api_performance():
    print("[API Test] Sending request...")
    start_time = time.time()
    try:
        # Replace with your app's API if applicable
        response = requests.get("http://127.0.0.1:5000/api/climate-news")
        response_time = time.time() - start_time
        print(f"[API Test] Response Time: {response_time:.4f} sec")
    except requests.exceptions.RequestException as e:
        print(f"[API Test] Request failed: {e}")


if __name__ == "__main__":
    # test_database_performance()
    test_api_performance()
    # TestApp().run()
