"""
Dynamic Throttling Manager
Controla la capacidad del sistema dinámicamente basado en métricas
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from logging import getLogger
import psutil
import time

logger = getLogger(__name__)


@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    cpu_percent: float
    memory_percent: float
    active_requests: int
    timestamp: float


@dataclass
class ThrottleConfig:
    """Configuración de throttling"""
    # Umbrales de CPU
    cpu_warning: float = 70.0  # % CPU para empezar a throttle
    cpu_critical: float = 85.0  # % CPU para throttle agresivo
    
    # Umbrales de memoria
    memory_warning: float = 75.0  # % Memoria para empezar a throttle
    memory_critical: float = 90.0  # % Memoria para throttle agresivo
    
    # Límites de requests concurrentes
    max_concurrent_requests: int = 100
    warning_concurrent_requests: int = 75
    
    # Delays de throttling (segundos)
    throttle_delay_low: float = 0.1  # Throttle suave
    throttle_delay_medium: float = 0.5  # Throttle moderado
    throttle_delay_high: float = 1.0  # Throttle agresivo


class ThrottlingLevel:
    """Niveles de throttling"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ThrottlingManager:
    """
    Gestiona el throttling dinámico del sistema
    
    Ajusta automáticamente la capacidad basándose en:
    - Uso de CPU
    - Uso de memoria
    - Número de requests concurrentes
    """
    
    def __init__(self, config: Optional[ThrottleConfig] = None):
        self.config = config or ThrottleConfig()
        self.active_requests = 0
        self._metrics_history: list[SystemMetrics] = []
        self._max_history = 60  # Mantener últimos 60 segundos
    
    def get_current_metrics(self) -> SystemMetrics:
        """Obtiene las métricas actuales del sistema"""
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=psutil.virtual_memory().percent,
            active_requests=self.active_requests,
            timestamp=time.time()
        )
    
    def calculate_throttle_level(self) -> tuple[int, str]:
        """
        Calcula el nivel de throttling necesario
        
        Returns:
            (nivel, razón) - Nivel de throttling y descripción de la razón
        """
        metrics = self.get_current_metrics()
        
        # Almacenar en historial
        self._metrics_history.append(metrics)
        if len(self._metrics_history) > self._max_history:
            self._metrics_history.pop(0)
        
        reasons = []
        level = ThrottlingLevel.NONE
        
        # Verificar CPU
        if metrics.cpu_percent >= self.config.cpu_critical:
            level = max(level, ThrottlingLevel.CRITICAL)
            reasons.append(f"CPU crítico ({metrics.cpu_percent:.1f}%)")
        elif metrics.cpu_percent >= self.config.cpu_warning:
            level = max(level, ThrottlingLevel.MEDIUM)
            reasons.append(f"CPU alto ({metrics.cpu_percent:.1f}%)")
        
        # Verificar Memoria
        if metrics.memory_percent >= self.config.memory_critical:
            level = max(level, ThrottlingLevel.CRITICAL)
            reasons.append(f"Memoria crítica ({metrics.memory_percent:.1f}%)")
        elif metrics.memory_percent >= self.config.memory_warning:
            level = max(level, ThrottlingLevel.MEDIUM)
            reasons.append(f"Memoria alta ({metrics.memory_percent:.1f}%)")
        
        # Verificar requests concurrentes
        if metrics.active_requests >= self.config.max_concurrent_requests:
            level = max(level, ThrottlingLevel.HIGH)
            reasons.append(f"Max requests concurrentes ({metrics.active_requests})")
        elif metrics.active_requests >= self.config.warning_concurrent_requests:
            level = max(level, ThrottlingLevel.LOW)
            reasons.append(f"Alto nº requests concurrentes ({metrics.active_requests})")
        
        reason = "; ".join(reasons) if reasons else "Sistema operando normalmente"
        
        return level, reason
    
    def get_throttle_delay(self) -> tuple[float, str]:
        """
        Obtiene el delay que debe aplicarse
        
        Returns:
            (delay_segundos, razón) - Delay a aplicar y descripción
        """
        level, reason = self.calculate_throttle_level()
        
        delay_map = {
            ThrottlingLevel.NONE: 0.0,
            ThrottlingLevel.LOW: self.config.throttle_delay_low,
            ThrottlingLevel.MEDIUM: self.config.throttle_delay_medium,
            ThrottlingLevel.HIGH: self.config.throttle_delay_high,
            ThrottlingLevel.CRITICAL: self.config.throttle_delay_high * 2,
        }
        
        delay = delay_map.get(level, 0.0)
        
        if delay > 0:
            logger.warning(f"⚠️ Throttling aplicado: {delay}s - {reason}")
        
        return delay, reason
    
    def should_reject_request(self) -> tuple[bool, str]:
        """
        Determina si se debe rechazar una request por sobrecarga
        
        Returns:
            (rechazar, razón) - True si debe rechazarse, False si no
        """
        level, reason = self.calculate_throttle_level()
        
        if level >= ThrottlingLevel.CRITICAL:
            return True, f"Sistema sobrecargado: {reason}"
        
        return False, reason
    
    def increment_active_requests(self):
        """Incrementa el contador de requests activas"""
        self.active_requests += 1
    
    def decrement_active_requests(self):
        """Decrementa el contador de requests activas"""
        if self.active_requests > 0:
            self.active_requests -= 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de las métricas del sistema"""
        metrics = self.get_current_metrics()
        level, reason = self.calculate_throttle_level()
        delay, _ = self.get_throttle_delay()
        
        return {
            "cpu_percent": round(metrics.cpu_percent, 2),
            "memory_percent": round(metrics.memory_percent, 2),
            "active_requests": metrics.active_requests,
            "throttle_level": level,
            "throttle_reason": reason,
            "throttle_delay_seconds": delay,
            "status": "healthy" if level < ThrottlingLevel.HIGH else "degraded",
        }


# Instancia global (se inicializa en app.py)
throttling_manager: Optional[ThrottlingManager] = None


def get_throttling_manager() -> ThrottlingManager:
    """Obtiene la instancia global del throttling manager"""
    global throttling_manager
    if throttling_manager is None:
        raise RuntimeError("ThrottlingManager not initialized")
    return throttling_manager


def init_throttling_manager(config: Optional[ThrottleConfig] = None) -> ThrottlingManager:
    """Inicializa el throttling manager global"""
    global throttling_manager
    throttling_manager = ThrottlingManager(config)
    return throttling_manager
