import logging

logging.basicConfig(
    filename="pipeline.log", 
    filemode="a",
    level=logging.INFO,
    format = "%(asctime)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

def log_info(msg):
    logger.info(msg)

def log_warning(msg):
    logger.warning(msg)

def log_error(msg):
    logger.error(msg)
