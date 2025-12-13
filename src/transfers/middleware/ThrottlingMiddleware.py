"""
Throttling Middleware
Aplica throttling dinámico a todas las requests
"""
from quart import Request, Response, abort, jsonify
import asyncio
from logging import getLogger
from ..core.throttling import get_throttling_manager, ThrottlingLevel

logger = getLogger(__name__)


class ThrottlingMiddleware:
    """
    Middleware que aplica throttling dinámico
    
    - Rechaza requests cuando el sistema está sobrecargado
    - Aplica delays cuando hay carga moderada
    - Permite requests normalmente cuando hay capacidad
    """
    
    def __init__(self, app):
        self.app = app
        self.app.before_request(self.check_throttle)
        self.app.after_request(self.record_request_end)
        logger.info("✅ Throttling Middleware initialized")
    
    async def check_throttle(self):
        """Verifica si se debe aplicar throttling"""
        try:
            manager = get_throttling_manager()
        except RuntimeError:
            # Si no está inicializado, permitir request
            return
        
        # Incrementar contador de requests activas
        manager.increment_active_requests()
        
        # Verificar si se debe rechazar la request
        should_reject, reason = manager.should_reject_request()
        
        if should_reject:
            manager.decrement_active_requests()
            logger.error(f"🚫 Request rejected: {reason}")
            abort(503, description=f"Service temporarily overloaded: {reason}")
        
        # Aplicar delay si es necesario
        delay, reason = manager.get_throttle_delay()
        
        if delay > 0:
            logger.debug(f"⏱️ Applying throttle delay: {delay}s - {reason}")
            await asyncio.sleep(delay)
    
    async def record_request_end(self, response: Response):
        """Registra el fin de una request"""
        try:
            manager = get_throttling_manager()
            manager.decrement_active_requests()
        except RuntimeError:
            pass
        
        return response
