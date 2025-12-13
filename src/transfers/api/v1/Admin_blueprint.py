"""
Admin API Blueprint
Endpoints para gestión de capacidad y feature toggles
"""
from quart import Blueprint, jsonify, request, abort
from quart_schema import tag
from logging import getLogger

from ...core.feature_toggles import get_feature_manager, Feature
from ...core.throttling import get_throttling_manager

logger = getLogger(__name__)

bp = Blueprint("admin_v1", __name__, url_prefix="/v1/admin")


@bp.get("/health")
@tag(["admin"])
async def health_check():
    """
    Health check avanzado con métricas del sistema
    
    Retorna:
        - Estado del servicio
        - Métricas de CPU y memoria
        - Nivel de throttling actual
        - Requests activas
        - Estado de features
    """
    try:
        throttle_manager = get_throttling_manager()
        feature_manager = get_feature_manager()
        
        metrics = throttle_manager.get_metrics_summary()
        features = await feature_manager.get_all_features()
        
        return jsonify({
            "status": metrics["status"],
            "service": "transfers",
            "metrics": {
                "cpu_percent": metrics["cpu_percent"],
                "memory_percent": metrics["memory_percent"],
                "active_requests": metrics["active_requests"],
                "throttle_level": metrics["throttle_level"],
                "throttle_reason": metrics["throttle_reason"],
                "throttle_delay_seconds": metrics["throttle_delay_seconds"],
            },
            "features": features,
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@bp.get("/features")
@tag(["admin"])
async def get_features():
    """
    Obtiene el estado de todos los feature toggles
    
    Returns:
        Diccionario con el estado (enabled/disabled) de cada feature
    """
    try:
        feature_manager = get_feature_manager()
        features = await feature_manager.get_all_features()
        
        return jsonify({
            "features": features
        }), 200
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        abort(500, description=str(e))


@bp.post("/features/<feature_name>/enable")
@tag(["admin"])
async def enable_feature(feature_name: str):
    """
    Activa un feature toggle
    
    Body (opcional):
        {
            "ttl": 3600  // Tiempo en segundos (omitir para permanente)
        }
    
    Returns:
        Estado actualizado del feature
    """
    try:
        feature = Feature(feature_name)
    except ValueError:
        abort(400, description=f"Invalid feature name: {feature_name}")
    
    try:
        feature_manager = get_feature_manager()
        
        body = await request.get_json(silent=True) or {}
        ttl = body.get("ttl")
        
        success = await feature_manager.set_feature(feature, True, ttl)
        
        if not success:
            abort(500, description="Failed to enable feature")
        
        return jsonify({
            "feature": feature_name,
            "enabled": True,
            "ttl": ttl
        }), 200
    except Exception as e:
        logger.error(f"Error enabling feature {feature_name}: {e}")
        abort(500, description=str(e))


@bp.post("/features/<feature_name>/disable")
@tag(["admin"])
async def disable_feature(feature_name: str):
    """
    Desactiva un feature toggle
    
    Body (opcional):
        {
            "ttl": 3600  // Tiempo en segundos (omitir para permanente)
        }
    
    Returns:
        Estado actualizado del feature
    """
    try:
        feature = Feature(feature_name)
    except ValueError:
        abort(400, description=f"Invalid feature name: {feature_name}")
    
    try:
        feature_manager = get_feature_manager()
        
        body = await request.get_json(silent=True) or {}
        ttl = body.get("ttl")
        
        success = await feature_manager.set_feature(feature, False, ttl)
        
        if not success:
            abort(500, description="Failed to disable feature")
        
        return jsonify({
            "feature": feature_name,
            "enabled": False,
            "ttl": ttl
        }), 200
    except Exception as e:
        logger.error(f"Error disabling feature {feature_name}: {e}")
        abort(500, description=str(e))


@bp.post("/emergency/disable-non-critical")
@tag(["admin"])
async def emergency_mode():
    """
    🚨 MODO EMERGENCIA 🚨
    
    Desactiva todas las funcionalidades no críticas para reducir carga
    
    Mantiene activas:
        - transaction_create (crítico)
        - cache
        - circuit_breaker
    
    Desactiva:
        - transaction_revert
        - transaction_delete
        - bulk_operations
        - external_api_calls
    """
    try:
        feature_manager = get_feature_manager()
        await feature_manager.disable_all_non_critical()
        
        features = await feature_manager.get_all_features()
        
        logger.critical("🚨 EMERGENCY MODE ACTIVATED 🚨")
        
        return jsonify({
            "status": "emergency_mode_activated",
            "message": "Non-critical features have been disabled",
            "features": features
        }), 200
    except Exception as e:
        logger.error(f"Error activating emergency mode: {e}")
        abort(500, description=str(e))


@bp.post("/emergency/restore")
@tag(["admin"])
async def restore_normal_mode():
    """
    Restaura todas las funcionalidades a sus valores por defecto
    
    Desactiva el modo emergencia y vuelve a operación normal
    """
    try:
        feature_manager = get_feature_manager()
        await feature_manager.restore_defaults()
        
        features = await feature_manager.get_all_features()
        
        logger.info("✅ Normal mode restored")
        
        return jsonify({
            "status": "normal_mode_restored",
            "message": "All features restored to defaults",
            "features": features
        }), 200
    except Exception as e:
        logger.error(f"Error restoring normal mode: {e}")
        abort(500, description=str(e))


@bp.get("/metrics")
@tag(["admin"])
async def get_metrics():
    """
    Obtiene métricas detalladas del sistema
    
    Returns:
        - CPU usage
        - Memory usage
        - Active requests
        - Throttling status
        - Feature toggles status
    """
    try:
        throttle_manager = get_throttling_manager()
        feature_manager = get_feature_manager()
        
        metrics = throttle_manager.get_metrics_summary()
        features = await feature_manager.get_all_features()
        
        return jsonify({
            "timestamp": metrics.get("timestamp"),
            "system": {
                "cpu_percent": metrics["cpu_percent"],
                "memory_percent": metrics["memory_percent"],
            },
            "requests": {
                "active": metrics["active_requests"],
            },
            "throttling": {
                "level": metrics["throttle_level"],
                "reason": metrics["throttle_reason"],
                "delay_seconds": metrics["throttle_delay_seconds"],
                "status": metrics["status"],
            },
            "features": features,
        }), 200
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        abort(500, description=str(e))
