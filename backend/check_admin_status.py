import sqlite3
conn = sqlite3.connect('sql_app.db')
cursor = conn.cursor()
email = "niyant214@gmail.com"
try:
    cursor.execute("SELECT email, is_admin FROM users WHERE email = ?", (email,))
    print(cursor.fetchone())
except Exception as e:
    print(e)
conn.close()
