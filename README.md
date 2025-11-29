# 📋 Microservicio de Transferencias

## 🏗️ Información General

**Base URL:** `http://localhost:8001/v1/transactions`  
**Documentación Swagger:** `http://localhost:8001/api/docs`  
**Versión API:** v1  
**Protocolo:** HTTP/HTTPS  

---

## 📊 Modelos de Datos

### 🔵 **TransactionCreate** (Request - Crear Transacción)
```json
{
  "sender": "user123",
  "receiver": "user456", 
  "quantity": 100
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `sender` | string | ✅ | ID del usuario que envía la transferencia |
| `receiver` | string | ✅ | ID del usuario que recibe la transferencia |
| `quantity` | integer | ✅ | Cantidad a transferir |

### 🟢 **TransactionView** (Response - Respuesta Completa)
```json
{
  "id": "675a12345678abcd",
  "sender": "user123",
  "receiver": "user456",
  "quantity": 100,
  "status": "completed",
  "currency": "USD",
  "sender_balance": 500.0,
  "receiver_balance": 600.0,
  "gmt_time": "2025-11-29T10:30:00Z"
}
```

| Campo | Tipo | Opcional | Descripción |
|-------|------|----------|-------------|
| `id` | string | ❓ | ID único de la transacción |
| `sender` | string | ✅ | ID del usuario que envía la transferencia |
| `receiver` | string | ✅ | ID del usuario que recibe la transferencia |
| `quantity` | integer | ✅ | Cantidad transferida |
| `status` | string | ✅ | Estado actual (default: "pending") |
| `currency` | string | ✅ | Moneda de la transacción (default: "USD") |
| `sender_balance` | float | ❓ | Balance del remitente después de la transacción |
| `receiver_balance` | float | ❓ | Balance del receptor después de la transacción |
| `gmt_time` | string | ❓ | Fecha y hora de la transacción en GMT |

### 🔴 **ErrorResponse** (Response - Errores)
```json
{
  "error": "Transaction not found",
  "status": "error"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `error` | string | ✅ | Descripción del error |
| `status` | string | ✅ | Estado de la respuesta |

### 🟡 **StatusUpdateRequest** (Request - Actualizar Estado)
```json
{
  "status": "completed"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `status` | string | ✅ | Nuevo estado de la transacción |

---

## 🛠️ Endpoints Disponibles

### 1. **POST** `/v1/transactions` - Crear Transacción
**Descripción:** Crea una nueva transacción entre dos cuentas.

**Request Body:**
- Modelo: `TransactionCreate`

**Responses:**
- `202` ✅ **Transacción creada** → `TransactionView`
- `400` ❌ **Error en datos** → `ErrorResponse` 
- `503` 🚫 **Servicio no disponible** → `ErrorResponse`

**Ejemplo:**
```bash
curl -X POST http://localhost:8001/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "user123",
    "receiver": "user456",
    "quantity": 100
  }'
```

---

### 2. **GET** `/v1/transactions/{id}` - Obtener Transacción
**Descripción:** Obtiene los detalles de una transacción específica.

**Path Parameters:**
- `id` (string): ID único de la transacción

**Responses:**
- `200` ✅ **Transacción encontrada** → `TransactionView`
- `404` 🔍 **No encontrada** → `ErrorResponse`

**Ejemplo:**
```bash
curl -X GET http://localhost:8001/v1/transactions/675a12345678abcd
```

---

### 3. **GET** `/v1/transactions/user/{id}` - Transacciones de Usuario
**Descripción:** Obtiene todas las transacciones donde el usuario aparece como remitente o receptor.

**Path Parameters:**
- `id` (string): ID del usuario

**Responses:**
- `200` ✅ **Lista obtenida** → `List[TransactionView]`
- `404` 🔍 **Sin transacciones** → `ErrorResponse`

**Ejemplo:**
```bash
curl -X GET http://localhost:8001/v1/transactions/user/user123
```

---

### 4. **GET** `/v1/transactions/user/{id}/sent` - Transacciones Enviadas
**Descripción:** Obtiene las transacciones enviadas por un usuario.

**Path Parameters:**
- `id` (string): ID del usuario

**Responses:**
- `200` ✅ **Lista obtenida** → `List[TransactionView]`
- `404` 🔍 **Sin transacciones enviadas** → `ErrorResponse`

**Ejemplo:**
```bash
curl -X GET http://localhost:8001/v1/transactions/user/user123/sent
```

---

### 5. **GET** `/v1/transactions/user/{id}/received` - Transacciones Recibidas
**Descripción:** Obtiene las transacciones recibidas por un usuario.

**Path Parameters:**
- `id` (string): ID del usuario

**Responses:**
- `200` ✅ **Lista obtenida** → `List[TransactionView]`
- `404` 🔍 **Sin transacciones recibidas** → `ErrorResponse`

**Ejemplo:**
```bash
curl -X GET http://localhost:8001/v1/transactions/user/user456/received
```

---

### 6. **PATCH** `/v1/transactions/{id}` - Revertir Transacción
**Descripción:** Revierte una transacción completada, devolviendo los fondos al remitente.

**Path Parameters:**
- `id` (string): ID de la transacción

**Responses:**
- `200` ✅ **Revertida exitosamente** → `TransactionView`
- `400` ❌ **No se puede revertir** → `ErrorResponse`
- `404` 🔍 **No encontrada** → `ErrorResponse`
- `503` 🚫 **Servicio no disponible** → `ErrorResponse`

**Ejemplo:**
```bash
curl -X PATCH http://localhost:8001/v1/transactions/675a12345678abcd
```

---

### 7. **DELETE** `/v1/transactions/{id}` - Eliminar Transacción
**Descripción:** Elimina una transacción del sistema. Solo aplicable a transacciones en estado "pending" o "failed".

**Path Parameters:**
- `id` (string): ID de la transacción

**Responses:**
- `200` ✅ **Eliminada exitosamente** → `TransactionView`
- `400` ❌ **No se puede eliminar** → `ErrorResponse`
- `404` 🔍 **No encontrada** → `ErrorResponse`

**Ejemplo:**
```bash
curl -X DELETE http://localhost:8001/v1/transactions/675a12345678abcd
```

---

### 8. **PUT** `/v1/transactions/{id}/status` - Actualizar Estado
**Descripción:** Actualiza manualmente el estado de una transacción.

**Path Parameters:**
- `id` (string): ID de la transacción

**Request Body:**
- Modelo: `StatusUpdateRequest`

**Responses:**
- `200` ✅ **Estado actualizado** → `TransactionView`
- `400` ❌ **Estado inválido** → `ErrorResponse`
- `404` 🔍 **No encontrada** → `ErrorResponse`

**Ejemplo:**
```bash
curl -X PUT http://localhost:8001/v1/transactions/675a12345678abcd/status \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

---

## 📋 Estados de Transacción

| Estado | Descripción |
|--------|-------------|
| `pending` | Transacción pendiente de procesamiento |
| `completed` | Transacción completada exitosamente |
| `failed` | Transacción falló en el procesamiento |
| `reverted` | Transacción revertida (fondos devueltos) |

---

## 🎯 Códigos de Respuesta HTTP

| Código | Significado | Descripción |
|--------|-------------|-------------|
| `200` | ✅ **OK** | Operación exitosa |
| `202` | ✅ **Accepted** | Transacción creada y procesada |
| `400` | ❌ **Bad Request** | Error en los datos enviados |
| `404` | 🔍 **Not Found** | Recurso no encontrado |
| `503` | 🚫 **Service Unavailable** | Servicio de cuentas no disponible |

---

## 🔧 Configuración de Desarrollo

### Docker Compose
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f ms_transfers_api

# Reiniciar servicio
docker-compose restart ms_transfers_api
```


*Documento generado el 29 de Noviembre de 2025*