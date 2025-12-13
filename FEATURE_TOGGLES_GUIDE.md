# 🎛️ Feature Toggles y Throttling - Guía

## 📖 Introducción

Hemos implementado un sistema de **gestión de capacidad** para controlar el rendimiento y disponibilidad del microservicio. Esto incluye:

1. **Feature Toggles**: Activar o desactivar funcionalidades sin reiniciar el servicio
2. **Throttling**: Controlar automáticamente la carga cuando el sistema está sobrecargado

### ¿Por qué es útil?

- **Sin reinicio**: Activa/desactiva funciones en tiempo real
- **Protección**: El sistema se protege automáticamente cuando hay sobrecarga
- **Emergencias**: Desactiva funciones no críticas si el sistema está colapsando
- **Testing**: Prueba nuevas funciones gradualmente

---

## 🔧 Librería y Configuración

### Librerías Utilizadas

```python
# Redis para persistir el estado de los toggles
redis.asyncio  # Ya instalado

# psutil para monitorear CPU y memoria
psutil==6.1.0  # Agregado en requirements.txt
```

### Configuración de Toggles

Los toggles se configuran en `src/transfers/core/feature_toggles.py`:

```python
class Feature(str, Enum):
    """Features que se pueden activar/desactivar"""
    TRANSACTION_CREATE = "transaction_create"      # Crear transacciones
    TRANSACTION_REVERT = "transaction_revert"      # Revertir transacciones
    TRANSACTION_DELETE = "transaction_delete"      # Eliminar transacciones
    BULK_OPERATIONS = "bulk_operations"            # Operaciones masivas
    EXTERNAL_API_CALLS = "external_api_calls"      # Llamadas a API GMT
    CACHE = "cache"                                # Sistema de caché
    CIRCUIT_BREAKER = "circuit_breaker"            # Circuit breaker

# Features críticas que NO se desactivan en modo emergencia
CRITICAL_FEATURES = {
    Feature.TRANSACTION_CREATE,
    Feature.CACHE,
    Feature.CIRCUIT_BREAKER
}
```

---

## 🔌 Integración con el Microservicio

### Ejemplo Real: Endpoint de Eliminar Transacción

**Antes** (sin feature toggle):
```python
@bp.delete("/<string:transaction_id>")
async def delete_transaction(transaction_id: str):
    service = TransferService()
    result = await service.delete_transaction_by_id(transaction_id)
    return result
```

**Después** (con feature toggle):
```python
@bp.delete("/<string:transaction_id>")
async def delete_transaction(transaction_id: str):
    # ✅ VERIFICAR si el feature está activo
    feature_manager = get_feature_manager()
    if not await feature_manager.is_enabled(Feature.TRANSACTION_DELETE):
        abort(503, description="Transaction deletion is temporarily disabled")
    
    # Si está activo, proceder normalmente
    service = TransferService()
    result = await service.delete_transaction_by_id(transaction_id)
    return result
```

### Endpoints que tienen Feature Toggles

1. **POST /v1/transactions** → `Feature.TRANSACTION_CREATE`
2. **PATCH /v1/transactions/{id}** → `Feature.TRANSACTION_REVERT`
3. **DELETE /v1/transactions/{id}** → `Feature.TRANSACTION_DELETE`

---

## ✅ Pasos para Probar 

### Paso 1: Iniciar el docker

### Paso 2: Verificar el Estado Inicial

```powershell
# Ver todas las features (deberían estar todas en true)
curl http://localhost:8001/v1/admin/features
```

Deberías ver:
```json
{
  "features": {
    "transaction_create": true,
    "transaction_revert": true,
    "transaction_delete": true,
    ...
  }
}
```

### Paso 3: Desactivar un Feature

```powershell
# Desactivar la función de ELIMINAR transacciones
curl -X POST http://localhost:8001/v1/admin/features/transaction_delete/disable `
  -H "Content-Type: application/json" `
  -d '{}'
```

### Paso 4: Probar que el Feature está Desactivado

```powershell
# Intentar eliminar una transacción (debería fallar)
curl -X DELETE http://localhost:8001/v1/transactions/test123
```

**Resultado esperado**: Error 503
```json
{
  "error": "Transaction deletion is temporarily disabled"
}
```

### Paso 5: Reactivar el Feature

```powershell
# Activar de nuevo
curl -X POST http://localhost:8001/v1/admin/features/transaction_delete/enable `
  -H "Content-Type: application/json" `
  -d '{}'
```

### Paso 6: Verificar que Funciona de Nuevo

```powershell
# Ahora DELETE debería funcionar normalmente
curl -X DELETE http://localhost:8001/v1/transactions/test123
```

---

## 🚨 Modo Emergencia (Bonus)

Si el sistema está colapsando, puedes desactivar todas las funciones **NO críticas** de un golpe:

```powershell
# Activar modo emergencia
curl -X POST http://localhost:8001/v1/admin/emergency/disable-non-critical
```

Esto desactiva automáticamente:
- ❌ Revertir transacciones
- ❌ Eliminar transacciones
- ❌ Operaciones masivas
- ❌ Llamadas a APIs externas

Pero **mantiene activas** las críticas:
- ✅ Crear transacciones
- ✅ Caché
- ✅ Circuit breaker

Para volver a la normalidad:
```powershell
curl -X POST http://localhost:8001/v1/admin/emergency/restore
```

---

## 📊 Ver el Estado del Sistema

### Health Check Completo

```powershell
curl http://localhost:8001/v1/admin/health
```

Te muestra:
- **CPU y memoria** del servidor
- **Requests activos** en este momento
- **Nivel de throttling** (0-4)
- **Estado de todas las features**

Ejemplo de respuesta:
```json
{
  "status": "healthy",
  "service": "transfers",
  "metrics": {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "active_requests": 3,
    "throttle_level": 0
  },
  "features": {
    "transaction_create": true,
    "transaction_revert": false,
    "transaction_delete": true,
    ...
  }
}
```

---

## 🎯 Resumen Rápido

### Para activar/desactivar un feature:

```powershell
# Desactivar
curl -X POST http://localhost:8001/v1/admin/features/{nombre_feature}/disable `
  -H "Content-Type: application/json" -d '{}'

# Activar
curl -X POST http://localhost:8001/v1/admin/features/{nombre_feature}/enable `
  -H "Content-Type: application/json" -d '{}'

# Ver estado
curl http://localhost:8001/v1/admin/features
```

### Features disponibles:
- `transaction_create`
- `transaction_revert`
- `transaction_delete`
- `bulk_operations`
- `external_api_calls`
- `cache`
- `circuit_breaker`

---

## ✅ Checklist Final

Para verificar que todo funciona:

- [ ] El servicio arranca correctamente
- [ ] `/v1/admin/health` devuelve 200 OK
- [ ] `/v1/admin/features` muestra todas las features
- [ ] Puedo desactivar un feature con `/disable`
- [ ] El endpoint protegido devuelve 503 cuando el feature está desactivado
- [ ] Puedo reactivar con `/enable`
- [ ] El endpoint vuelve a funcionar después de reactivar
- [ ] El modo emergencia funciona correctamente

¡Listo! 🚀 Ahora tienes control total sobre las funcionalidades del microservicio sin necesidad de reiniciarlo.
