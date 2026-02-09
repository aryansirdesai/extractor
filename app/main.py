from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="Document AI Agent",
    description="FastAPI AI agent for document extraction with Gemini Flash",
    version="0.1.0",
)

# Optional: CORS middleware (useful if frontend will call this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Service is running"}