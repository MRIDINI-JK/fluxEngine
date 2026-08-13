from backend.config import settings
from backend.common.logger import logger

logger.info(settings.APP_NAME)
logger.info(settings.DATABASE_URL)
logger.info(settings.RABBITMQ_URL)
logger.info(settings.REDIS_URL)