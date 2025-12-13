from quart import Quart
from quart_schema import QuartSchema, Tag

from .core import extensions as ext
from .core.config import settings
from .core.feature_toggles import init_feature_manager
from .core.throttling import init_throttling_manager, ThrottleConfig

from logging import getLogger, Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from .utils.LoggerColorFormatter import ColorFormatter
import redis.asyncio as redis

from .api.v1.Transactions_blueprint import bp as transactions_bp_v1
from .api.v1.Admin_blueprint import bp as admin_bp_v1

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
    from quart_cors import cors
    app = Quart("Transfers Service")
    app = cors(app, allow_origin="*")

    app.config.from_object(settings)
    logger.info("Settings loaded for transfers.")

    app.register_blueprint(transactions_bp_v1)
    app.register_blueprint(admin_bp_v1)
    logger.info("Transfers routes registered")

    schema = QuartSchema()
    schema.tags = [
        Tag(name="v1", description="API version 1"),
    ]
    schema.openapi_path = "/api/openapi.json"
    schema.swagger_ui_path = "/api/docs"
    schema.init_app(app)

    from .middleware.RateLimiter import RateLimiter
    from .middleware.ThrottlingMiddleware import ThrottlingMiddleware
    
    RateLimiter(app, limit=50, window=60)
    ThrottlingMiddleware(app)

    @app.before_serving
    async def startup():
        logger.info("Transfers service is starting up...")
        try:
            await ext.init_db_client()
            
            app.redis_client = redis.Redis(
                host=settings.REDIS_HOST, 
                port=settings.REDIS_PORT, 
                decode_responses=True
            )
            await app.redis_client.ping()
            logger.info("Connected to Redis")
            
            # Inicializar Feature Toggles
            init_feature_manager(app.redis_client)
            logger.info("✅ Feature Toggles initialized")
            
            # Inicializar Throttling Manager
            throttle_config = ThrottleConfig(
                cpu_warning=settings.THROTTLE_CPU_WARNING,
                cpu_critical=settings.THROTTLE_CPU_CRITICAL,
                memory_warning=settings.THROTTLE_MEMORY_WARNING,
                memory_critical=settings.THROTTLE_MEMORY_CRITICAL,
                max_concurrent_requests=settings.THROTTLE_MAX_CONCURRENT,
                warning_concurrent_requests=settings.THROTTLE_WARNING_CONCURRENT,
            )
            init_throttling_manager(throttle_config)
            logger.info("✅ Throttling Manager initialized")
            
        except Exception as e:
            logger.error("Startup failed. Shutting down...")
            logger.debug(e)
            raise e
        logger.info("Transfers service started successfully")

    @app.after_serving
    async def shutdown():
        logger.info("Transfers service is shutting down...")
        ext.close_db_client()
        if hasattr(app, 'redis_client'):
            await app.redis_client.close()
            logger.info("Redis connection closed")
        logger.info("Transfers service shut down complete.")

    return app
