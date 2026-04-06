import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env
load_dotenv()

database_url = os.environ.get("DATABASE_URL", "")
if not database_url:
    print("ERROR: DATABASE_URL not set in .env")
    exit(1)

print("Connecting to database...")
engine = create_engine(database_url)

with engine.connect() as conn:
    print("Adding missing columns to 'projects' table...")
    
    columns_to_add = [
        ("topic", "VARCHAR"),
        ("tech_stack", "VARCHAR"),
        ("complexity", "VARCHAR"),
        ("status", "VARCHAR DEFAULT 'active'")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            print(f"Adding column '{col_name}'...")
            conn.execute(text(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}"))
            print(f"DONE: Added {col_name}.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print(f"NOTE: Column '{col_name}' already exists.")
            else:
                print(f"ERROR: Error adding '{col_name}': {e}")
    
    conn.commit()
    print("\nDONE: Migration complete.")
