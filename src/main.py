"""
Main Application Entry Point

PURPOSE:
    Initializes the FastAPI application, middleware, and routes.
    Serves as the central hub for the backend API.

USAGE:
    uvicorn src.main:app
"""

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.monitoring.core.monitor_manager import MonitorManager
from src.monitoring.logging.request_logger import RequestLogger
from src.config import ALLOWED_ORIGINS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fracture_ai")

# Initialize Monitoring
monitor_manager = MonitorManager()
request_logger = RequestLogger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: startup and shutdown
    """
    # Startup
    logger.info("Starting Fracture Detection AI API...")
    monitor_manager.start()
    yield
    # Shutdown
    logger.info("Shutting down...")
    monitor_manager.stop()

app = FastAPI(
    title="Fracture Detection AI",
    description="AI-powered X-ray analysis and fracture detection system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for monitoring
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """
    Middleware to log requests and track metrics
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Record metrics
    monitor_manager.record_metric("api_latency", process_time)
    monitor_manager.record_metric("api_requests", 1)
    
    # Log request
    # Note: request_logger implementation handles accessing request details
    # This is simplified for the middleware hook
    
    return response

# Import and include routers
# from src.api.routes import analysis, feedback, health
# app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
# app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Feedback"])
# app.include_router(health.router, tags=["Health"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Fracture Detection AI API",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "uptime_check": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
