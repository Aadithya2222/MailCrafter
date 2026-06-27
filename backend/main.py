"""
FastAPI application entry point for Speech-to-Email Assistant.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import audio, email, contacts
from config import settings

app = FastAPI(
    title="MailCrafter API",
    description="Speech-to-Email Assistant using Gemini API",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audio.router, prefix="/api/v1", tags=["audio"])
app.include_router(email.router, prefix="/api/v1", tags=["email"])
app.include_router(contacts.router, prefix="/api/v1", tags=["contacts"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "MailCrafter API"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "MailCrafter API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
