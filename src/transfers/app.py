from quart import Quart
from quart_schema import QuartSchema, Tag

from .core import extensions as ext
from .core.config import settings

from logging import getLogger, Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from .utils.LoggerColorFormatter import ColorFormatter

from .api.v1.Transactions_blueprint import bp as transactions_bp_v1

logger = getLogger()
logger.setLevel(settings.LOG_LEVEL)

console_handler = StreamHandler()
console_handler.setLevel(settings.LOG_LEVEL)
console_format = ColorFormatter(
    "%(levelname)s:     %(message)s"
)
console_handler.setFormatter(console_format)

file_handler = TimedRotatingFileHandler(
    settings.LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=settings.LOG_BACKUP_COUNT
)
file_handler.setLevel(settings.LOG_LEVEL)
file_formatter = Formatter(
    "%(asctime)s - %(levelname)s:     %(message)s"
)
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.propagate = False


def create_app():
    app = Quart("Transfers Service")

    app.config.from_object(settings)
    logger.info("Settings loaded for transfers.")

    app.register_blueprint(transactions_bp_v1)
    logger.info("Transfers routes registered")

    schema = QuartSchema()
    schema.tags = [
        Tag(name="v1", description="API version 1"),
    ]
    schema.openapi_path = "/api/openapi.json"
    schema.swagger_ui_path = "/api/docs"
    schema.init_app(app)

    @app.before_serving
    async def startup():
        logger.info("Transfers service is starting up...")
        try:
            await ext.init_db_client()
        except Exception as e:
            logger.error("Database connection failed. Shutting down...")
            logger.debug(e)
            raise e
        logger.info("Transfers service started successfully")

    @app.after_serving
    async def shutdown():
        logger.info("Transfers service is shutting down...")
        ext.close_db_client()
        logger.info("Transfers service shut down complete.")

    return app
