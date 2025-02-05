import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
    datefmt="%d-%b-%y %H:%M:%S",
)

logger = logging.getLogger(__name__)


"""
import logging

# Configure the main logger for normal logs
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log",  # Normal logs will go here
    filemode="a",  # Append mode
    datefmt="%d-%b-%y %H:%M:%S",
)

# Create a logger for the current module
logger = logging.getLogger(__name__)

# Create a separate handler for error logs
error_handler = logging.FileHandler('error.log', mode='a')  # Error logs will go here
error_handler.setLevel(logging.ERROR)  # Only log ERROR and CRITICAL messages
error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)

# Add the error handler to the logger
logger.addHandler(error_handler)

# Example log messages
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message that will go to both app.log and error.log.")
logger.critical("This is a critical message that will also go to error.log.")

"""
