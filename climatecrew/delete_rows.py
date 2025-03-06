import sqlite3

conn = sqlite3.connect('user_auth.db')
cursor = conn.cursor()

# Replace 'your_table' with the actual table name
cursor.execute("DELETE FROM users;")  
conn.commit()  # Save changes

print("Database cleared successfully!")
conn.close()
