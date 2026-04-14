from fastapi import FastAPI
from app.database.database import db_manager
from app.api import admin_auth, institute
from app.logger.logger import get_logger
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger(__name__)

app = FastAPI(title="Institute Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting up...")
    db_manager.initialize()
    
    # Log pool status
    stats = await db_manager.get_pool_stats()
    logger.info(f"Connection pool stats: {stats}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    logger.info("Shutting down...")
    await db_manager.close_all()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    is_healthy = await db_manager.health_check()
    stats = await db_manager.get_pool_stats()
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": "connected" if is_healthy else "disconnected",
        "pool_stats": stats
    }

@app.get("/pool-stats")
async def pool_stats():
    """Get connection pool statistics"""
    return await db_manager.get_pool_stats()

# Include routers
app.include_router(admin_auth.router, prefix="/api/auth")
app.include_router(institute.router, prefix="/api/institutes")
