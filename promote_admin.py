import sqlite3
import os

db_path = 'backend/sql_app.db'
if not os.path.exists(db_path):
    print(f'DB NOT found at {db_path}')
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if user exists
cursor.execute("SELECT id, email, is_admin FROM users WHERE email = 'admin@example.com'")
user = cursor.fetchone()

if user:
    print(f"Found User: {user[1]} (ID: {user[0]}) | Current Admin Status: {user[2]}")
    print("Promoting to Super Admin...")
    cursor.execute("UPDATE users SET is_admin = 1 WHERE email = 'admin@example.com'")
    conn.commit()
    print("✅ Successfully promoted admin@example.com to Super Admin.")
else:
    print("❌ User admin@example.com not found in the 'users' table.")
    print("Check other users:")
    cursor.execute("SELECT email FROM users")
    for row in cursor.fetchall():
        print(f" - {row[0]}")

conn.close()
