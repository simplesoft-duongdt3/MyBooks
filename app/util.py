from loguru import logger
from dotenv import load_dotenv
load_dotenv()

logger = logger
logger.add("logs/file_log.log", format="{time} {level} {message}", rotation="12:00", level="INFO")