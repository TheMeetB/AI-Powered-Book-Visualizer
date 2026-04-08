import os

from loguru import logger

# Ensure the log directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Define the log file path
LOG_FILE = os.path.join(LOG_DIR, "book_visualizer.log")


def setup_logger():
    logger.remove()
    # Add a handler to the logger
    logger.add(
        LOG_FILE,
        level="TRACE",  # Set log level to TRACE
        rotation="00:00",  # Refresh the log every midnight
        retention="30 days",  # Retain logs for 30 days
        compression="zip",  # Compress old logs into zip files
        format="{time:DD-MM-YYYY HH:mm:ss:SSS} | {level} | {message}",  # Log format
        encoding="utf-8",
    )
