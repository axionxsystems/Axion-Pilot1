from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
print("--- START USER LIST ---")
for user in users:
    print(f"EMAIL: {user.email}")
print("--- END USER LIST ---")
db.close()
