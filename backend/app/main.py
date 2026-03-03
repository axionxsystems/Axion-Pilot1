from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import auth, users, projects, viva

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Project Gen API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, verify this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(viva.router, prefix="/api/viva", tags=["Viva"])

@app.get("/")
async def root():
    return {"message": "AI Project Generator API is running"}
