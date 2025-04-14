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
        # self.reset_user_points()  # Only run this once to fix existing data

    def connect(self):
        """Connect to database"""
        try:
            # Close any existing connection first
            if self.conn:
                try:
                    self.conn.close()
                except:
                    pass  # Ignore errors when closing already closed connection

            # Create new connection
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("Database connected successfully")
            return self.conn
        except Exception as e:
            print(f"Database connection error: {e}")
            self.conn = None
            self.cursor = None
            return None

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

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_management (
                user_id INTEGER PRIMARY KEY,
                current_task TEXT,
                points INTEGER DEFAULT 0,
                num_tasks_completed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_text TEXT NOT NULL,
                image BLOB,
                latitude REAL,
                longitude REAL,
                location_text TEXT,
                description TEXT,
                submission_date TEXT,
                upvotes INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
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
        try:
            self.cursor.execute(
                "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            return self.cursor.fetchone()  # Returns (id, username, email) or None if not found
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    def get_user_profile(self, user_id):
        """Get user profile data"""
        try:
            # Check if connection is closed and reconnect if needed
            if self.conn is None or not hasattr(self.conn, 'cursor'):
                print("Database connection is closed. Attempting to reconnect...")
                self.connect()

            # Use existing connection
            cursor = self.conn.cursor()

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
                    self.conn.commit()
                    # Return the new profile
                    profile = (user_id, "", username,
                               email, "", "", "", "", None)

            # Don't close cursor or connection
            return profile

        except Exception as e:
            print(f"Error getting user profile: {e}")
            # Try to reconnect for next time
            try:
                self.connect()
            except:
                pass
            return None

    def update_user_profile(self, user_id, contact, city, country, occupation, profile_image=None):
        """Update user profile data"""
        try:
            # Use existing connection instead of creating new one
            cursor = self.conn.cursor()

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
                return False

            # Add user_id to values list
            values.append(user_id)

            query = f'''
                UPDATE user_profiles 
                SET {', '.join(update_fields)}
                WHERE user_id = ?
            '''

            print("Profile updated successfully for user_id:", user_id)

            cursor.execute(query, values)
            self.conn.commit()  # Commit on self.conn

            success = cursor.rowcount > 0

            # Don't close the cursor or connection
            return success

        except Exception as e:
            print(f"Error updating profile: {e}")
            return False

    def initialize_user_task(self, user_id, task="Start your climate journey by measuring your carbon footprint using an online calculator.", task_points=20):
        """Initialize a new user's task after registration"""
        try:
            # Check if user already has task data
            self.cursor.execute(
                'SELECT user_id FROM task_management WHERE user_id = ?', (user_id,))
            if self.cursor.fetchone():
                print(f"User {user_id} already has task data")
                return True

            # Create new task entry WITH ZERO ACCUMULATED POINTS
            self.cursor.execute(
                'INSERT INTO task_management (user_id, current_task, points, num_tasks_completed) VALUES (?, ?, ?, ?)',
                (user_id, task, 0, 0)  # Initialize points to 0
            )
            self.conn.commit()
            print(f"Task initialized for user {user_id}")
            return True
        except Exception as e:
            print(f"Error initializing user task: {e}")
            return False

    def get_user_task(self, user_id):
        """Get a user's current task data"""
        try:
            self.cursor.execute(
                'SELECT current_task, points, num_tasks_completed FROM task_management WHERE user_id = ?',
                (user_id,)
            )
            task_data = self.cursor.fetchone()

            if not task_data:
                # If no task exists, initialize one
                default_task = "Start your climate journey by measuring your carbon footprint using an online calculator."
                self.initialize_user_task(user_id, default_task)
                # Return 0 points as accumulated points
                return (default_task, 0, 0)

            # Return task, accumulated points, and completed tasks count
            return task_data
        except Exception as e:
            print(f"Error getting user task: {e}")
            return (None, 0, 0)

    def update_user_task(self, user_id, new_task, task_points=20):
        """Update a user's current task without changing points"""
        try:
            # Only update the task, not the points
            self.cursor.execute(
                'UPDATE task_management SET current_task = ? WHERE user_id = ?',
                (new_task, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user task: {e}")
            return False

    def complete_task(self, user_id, task_points=20):
        """Mark a task as completed, update points and task count"""
        try:
            # Get current values
            self.cursor.execute(
                'SELECT points, num_tasks_completed FROM task_management WHERE user_id = ?',
                (user_id,)
            )
            task_data = self.cursor.fetchone()

            if not task_data:
                print(f"No task data found for user {user_id}")
                return False

            current_points, completed_count = task_data

            # Add task points to the accumulated points
            new_points = current_points + task_points

            # Update counters and generate new task
            new_task = "You've completed the task! Generate a new one with the Change Task button."

            self.cursor.execute(
                '''UPDATE task_management 
                   SET points = ?,
                       num_tasks_completed = ?, 
                       current_task = ? 
                   WHERE user_id = ?''',
                (new_points, completed_count + 1, new_task, user_id)
            )
            self.conn.commit()
            print(
                f"Task completed for user {user_id}. Total points: {new_points}, Tasks: {completed_count + 1}")

            return True
        except Exception as e:
            print(f"Error completing task: {e}")
            return False

    def get_user_stats(self, user_id):
        """Get user's points and completed task count"""
        try:
            self.cursor.execute(
                'SELECT points, num_tasks_completed FROM task_management WHERE user_id = ?',
                (user_id,)
            )
            stats = self.cursor.fetchone()

            if not stats:
                return (0, 0)

            return stats
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return (0, 0)

    def reset_user_points(self):
        """Reset points for all users to fix existing data"""
        try:
            self.cursor.execute('UPDATE task_management SET points = 0')
            self.conn.commit()
            print("All user points have been reset")
            return True
        except Exception as e:
            print(f"Error resetting user points: {e}")
            return False

    def add_submission(self, user_id, task_text, image=None, latitude=None, longitude=None,
                       location_text=None, description=None, submission_date=None):
        """Add a new task submission from a user"""
        try:
            # Use existing connection
            cursor = self.conn.cursor()

            cursor.execute('''
                INSERT INTO user_submissions (
                    user_id, task_text, image, latitude, longitude, 
                    location_text, description, submission_date, upvotes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, task_text, image, latitude, longitude,
                location_text, description, submission_date, 0
            ))

            self.conn.commit()

            print(f"Submission added for user {user_id}")
            return True
        except Exception as e:
            print(f"Error adding submission: {e}")
            return False

    def get_user_submissions(self, user_id=None, limit=10):
        """Get user submissions, optionally filtered by user_id"""
        try:
            # Use existing connection
            cursor = self.conn.cursor()

            if user_id:
                cursor.execute('''
                    SELECT id, user_id, task_text, image, latitude, longitude, 
                           location_text, description, submission_date, upvotes
                    FROM user_submissions 
                    WHERE user_id = ?
                    ORDER BY submission_date DESC
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT id, user_id, task_text, image, latitude, longitude, 
                           location_text, description, submission_date, upvotes
                    FROM user_submissions 
                    ORDER BY submission_date DESC
                    LIMIT ?
                ''', (limit,))

            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting submissions: {e}")
            return []

    def upvote_submission(self, submission_id):
        """Increase the upvote count for a submission"""
        try:
            # Use existing connection
            cursor = self.conn.cursor()

            cursor.execute('''
                UPDATE user_submissions 
                SET upvotes = upvotes + 1
                WHERE id = ?
            ''', (submission_id,))

            self.conn.commit()

            # Return the new upvote count
            cursor.execute('SELECT upvotes FROM user_submissions WHERE id = ?',
                           (submission_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error upvoting submission: {e}")
            return 0
