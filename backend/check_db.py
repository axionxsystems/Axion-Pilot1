from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Connect to the database
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("-" * 50)
print("🔍 DATABASE USER INSPECTOR")
print("-" * 50)

try:
    users = session.query(User).all()
    if not users:
        print("No users found in database.")
    else:
        print(f"Found {len(users)} registered users:\n")
        print(f"{'ID':<5} | {'Email':<30} | {'Plan':<10} | {'Active'}")
        print("-" * 60)
        for user in users:
            print(f"{user.id:<5} | {user.email:<30} | {user.plan:<10} | {user.is_active}")
            
    print("-" * 50)
    print("\n✅ Verification Complete.")
    
except Exception as e:
    print(f"❌ Error accessing database: {e}")

finally:
    session.close()
