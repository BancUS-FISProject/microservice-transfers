"""
Feature Toggles Manager
Permite activar/desactivar funcionalidades dinámicamente para gestión de capacidad
"""
from typing import Dict, Any, Optional
from enum import Enum
from logging import getLogger
import redis.asyncio as redis

logger = getLogger(__name__)


class Feature(str, Enum):
    """Funcionalidades que pueden ser toggled"""
    TRANSACTION_CREATE = "transaction_create"
    TRANSACTION_REVERT = "transaction_revert"
    TRANSACTION_DELETE = "transaction_delete"
    BULK_OPERATIONS = "bulk_operations"
    EXTERNAL_API_CALLS = "external_api_calls"  # GMT Time API
    CACHE = "cache"
    CIRCUIT_BREAKER = "circuit_breaker"


class FeatureToggleManager:
    """
    Gestiona feature toggles con persistencia en Redis
    
    Permite activar/desactivar funcionalidades en caliente para:
    - Reducir carga durante picos de tráfico
    - Desactivar funcionalidades problemáticas
    - A/B testing
    - Rollout gradual de features
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self._local_cache: Dict[str, bool] = {}
        
        # Estados por defecto (si Redis no está disponible)
        self.defaults = {
            Feature.TRANSACTION_CREATE: True,
            Feature.TRANSACTION_REVERT: True,
            Feature.TRANSACTION_DELETE: True,
            Feature.BULK_OPERATIONS: True,
            Feature.EXTERNAL_API_CALLS: True,
            Feature.CACHE: True,
            Feature.CIRCUIT_BREAKER: True,
        }
    
    async def is_enabled(self, feature: Feature) -> bool:
        """
        Verifica si una funcionalidad está habilitada
        
        Args:
            feature: Feature a verificar
            
        Returns:
            True si está habilitada, False si no
        """
        # Intentar obtener de Redis primero
        if self.redis_client:
            try:
                key = f"feature_toggle:{feature.value}"
                value = await self.redis_client.get(key)
                
                if value is not None:
                    enabled = value.lower() in ('true', '1', 'yes', 'on')
                    self._local_cache[feature.value] = enabled
                    return enabled
            except Exception as e:
                logger.warning(f"Redis error checking feature toggle {feature.value}: {e}")
        
        # Fallback a caché local
        if feature.value in self._local_cache:
            return self._local_cache[feature.value]
        
        # Fallback a default
        return self.defaults.get(feature, True)
    
    async def set_feature(self, feature: Feature, enabled: bool, ttl: Optional[int] = None) -> bool:
        """
        Activa o desactiva una funcionalidad
        
        Args:
            feature: Feature a modificar
            enabled: True para activar, False para desactivar
            ttl: Tiempo de vida en segundos (None = permanente)
            
        Returns:
            True si se actualizó correctamente
        """
        self._local_cache[feature.value] = enabled
        
        if self.redis_client:
            try:
                key = f"feature_toggle:{feature.value}"
                value = "true" if enabled else "false"
                
                if ttl:
                    await self.redis_client.setex(key, ttl, value)
                else:
                    await self.redis_client.set(key, value)
                
                logger.info(f"Feature toggle {feature.value} set to {enabled}" + 
                           (f" (TTL: {ttl}s)" if ttl else ""))
                return True
            except Exception as e:
                logger.error(f"Failed to set feature toggle {feature.value}: {e}")
                return False
        
        logger.warning(f"Redis not available. Feature toggle {feature.value} only in memory")
        return True
    
    async def get_all_features(self) -> Dict[str, bool]:
        """
        Obtiene el estado de todas las funcionalidades
        
        Returns:
            Diccionario con el estado de cada feature
        """
        result = {}
        for feature in Feature:
            result[feature.value] = await self.is_enabled(feature)
        return result
    
    async def disable_all_non_critical(self) -> None:
        """
        Desactiva todas las funcionalidades no críticas
        Útil durante emergencias o sobrecarga extrema
        """
        logger.warning("🚨 EMERGENCY MODE: Disabling non-critical features")
        
        await self.set_feature(Feature.TRANSACTION_REVERT, False)
        await self.set_feature(Feature.TRANSACTION_DELETE, False)
        await self.set_feature(Feature.BULK_OPERATIONS, False)
        await self.set_feature(Feature.EXTERNAL_API_CALLS, False)
        
        # Mantener críticas activas
        await self.set_feature(Feature.TRANSACTION_CREATE, True)
        await self.set_feature(Feature.CACHE, True)
        await self.set_feature(Feature.CIRCUIT_BREAKER, True)
    
    async def restore_defaults(self) -> None:
        """Restaura todos los feature toggles a sus valores por defecto"""
        logger.info("Restoring all feature toggles to defaults")
        
        for feature, enabled in self.defaults.items():
            await self.set_feature(feature, enabled)


# Instancia global (se inicializa en app.py)
feature_manager: Optional[FeatureToggleManager] = None


def get_feature_manager() -> FeatureToggleManager:
    """Obtiene la instancia global del feature manager"""
    global feature_manager
    if feature_manager is None:
        raise RuntimeError("FeatureToggleManager not initialized")
    return feature_manager


def init_feature_manager(redis_client: Optional[redis.Redis] = None) -> FeatureToggleManager:
    """Inicializa el feature manager global"""
    global feature_manager
    feature_manager = FeatureToggleManager(redis_client)
    return feature_manager
