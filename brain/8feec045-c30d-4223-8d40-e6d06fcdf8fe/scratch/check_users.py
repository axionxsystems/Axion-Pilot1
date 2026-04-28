import sqlite3
import os

db_path = "c:/Users/niyan/OneDrive/Desktop/pilot/backend/sql_app.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email, is_admin, is_active FROM users;")
        rows = cursor.fetchall()
        if not rows:
            print("No users found in database.")
        else:
            print("Registered Users:")
            for row in rows:
                print(f"Email: {row[0]}, Admin: {row[1]}, Active: {row[2]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
