from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from contextlib import asynccontextmanager

from .config import settings
from .database import create_db_and_tables, get_session
from .services import PackageService
from .routers import auth, packages, payments, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    create_db_and_tables()
    
    # Create default packages
    with next(get_session()) as session:
        PackageService.create_default_packages(session)
    
    yield
    
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="Affiliate Learning Platform API",
    description="Backend API for the affiliate learning platform with course management and commission tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(packages.router)
app.include_router(payments.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Affiliate Learning Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)