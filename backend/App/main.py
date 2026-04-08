import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.middleware.sessions import SessionMiddleware

from .api import controllers
from .config import database
from .dto import StandardResponse
from .exceptions import register_exception_handlers
from .utils import setup_logger

# Initialize FastAPI app
app = FastAPI(
    title="Book Visualizer",
    description="A dynamic web platform for immersing users in their reading experience.",
    version="1.0.0"
)

# Setup Loguru Logger
setup_logger()

# Register centralized exception handlers
register_exception_handlers(app)

# Configure middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_MIDDLEWARE_SECRET", "DEFAULT_SECRET_KEY"),  # Fallback for safety
    max_age=24 * 60 * 60  # 24 hours session lifetime
)
origins_from_env = os.getenv("ORIGINS", "")
origins_list = [origin.strip() for origin in origins_from_env.split(",")] if origins_from_env else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Root endpoint for health check
@app.get("/", tags=["Health"])
async def root():
    return StandardResponse(success=True, status_code=status.HTTP_200_OK, message="Book Visualizer API is running",
                            data=None)


# Include routers
app.include_router(controllers.signup_controller.router)
app.include_router(controllers.signin_controller.router)
app.include_router(controllers.forget_controller.router)
app.include_router(controllers.user_controller.router)
app.include_router(controllers.dashboard_controller.router)
app.include_router(controllers.ai_controller.router)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Book Visualizer API")
    # Add any initialization logic here (e.g., database connection check)
    try:
        database.command("ping")  # Check MongoDB connection
        logger.info("MongoDB connection established successfully")
    except Exception as e:
        logger.error("Failed to connect to MongoDB: {error}", error=str(e), exc_info=True)
        raise  # Fail fast if DB is unavailable


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Book Visualizer API")
    try:
        # Assuming client is accessible from database.py
        database.client.close()
        logger.info("MongoDB connection closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
