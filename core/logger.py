import logging
import os

def setup_logger():
    # Create logs folder if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Configure logging format
    logging.basicConfig(
        level = logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # print to terminal
            logging.StreamHandler(),
            # save to file
            logging.FileHandler("logs/bot.py")
        ]
    )

    return logging.getLogger(__name__)

logger = setup_logger()