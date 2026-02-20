from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import whatsapp, mentor, auth, admin
from app.db.database import engine
import app.db.models as models

# Initialize SQLite Database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kenyan GBV & Mental Health Chatbot API")

# Register webhook router
app.include_router(whatsapp.router, prefix="/api/v1/whatsapp", tags=["whatsapp"])

# Register mentor dashboard API routers
app.include_router(mentor.router, prefix="/api/v1/mentor", tags=["mentor"])

# Register Authentication router
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# Register Admin router
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

# Serve Static Dashboard & Assets
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def serve_landing_page():
    return FileResponse("app/static/index.html")

@app.get("/mentor")
async def serve_mentor_dashboard():
    return FileResponse("app/static/dashboard.html")

@app.get("/admin")
async def serve_admin_dashboard():
    return FileResponse("app/static/admin.html")

@app.get("/")
def read_root():
    return {"message": "GBV & Mental Health Support Chatbot API is running."}
