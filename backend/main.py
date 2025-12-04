"""Main application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from events.api import router as events_router
from registration.api import router as registration_router

# Initialize FastAPI app
app = FastAPI(title="Event Management API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events_router)
app.include_router(registration_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Event Management API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Lambda handler
handler = Mangum(app)
