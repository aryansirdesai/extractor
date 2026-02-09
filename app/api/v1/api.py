from fastapi import APIRouter

# Import your route modules here
from app.api.v1.routes import documents

api_router = APIRouter()

# Mount routes
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])