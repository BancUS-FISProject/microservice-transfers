# Tests del Microservicio de Transferencias

Este directorio contiene las pruebas completas para el microservicio de transferencias, incluyendo tanto pruebas **out-of-process** (mediante el test client de Quart) como **in-process** (llamadas directas al servicio).

## 📋 Resumen de Tests

Total de pruebas implementadas: **33 tests**

### Out-of-Process Tests (API HTTP) - 31 tests

#### Creación de Transacciones (8 tests)
- ✅ `test_create_transaction_success` - Crear transacción exitosa
- ❌ `test_create_transaction_missing_params` - Parámetros faltantes
- ❌ `test_create_transaction_invalid_quantity_zero` - Cantidad cero
- ❌ `test_create_transaction_invalid_quantity_negative` - Cantidad negativa
- ❌ `test_create_transaction_same_sender_receiver` - Mismo remitente y receptor
- ❌ `test_create_transaction_insufficient_funds` - Fondos insuficientes
- ❌ `test_create_transaction_sender_not_found` - Remitente no encontrado
- ❌ `test_create_transaction_receiver_not_found` - Receptor no encontrado

#### Consulta de Transacciones (12 tests)
- ✅ `test_get_transaction_by_id` - Obtener transacción por ID
- ❌ `test_get_transaction_not_found` - Transacción no encontrada
- ❌ `test_get_transaction_invalid_id` - ID inválido
- ✅ `test_get_transactions_by_user` - Transacciones de un usuario
- ❌ `test_get_transactions_by_user_not_found` - Usuario sin transacciones
- ✅ `test_get_transactions_sent_by_user` - Transacciones enviadas
- ❌ `test_get_transactions_sent_not_found` - Sin transacciones enviadas
- ✅ `test_get_transactions_received_by_user` - Transacciones recibidas
- ❌ `test_get_transactions_received_not_found` - Sin transacciones recibidas

#### Reversión de Transacciones (4 tests)
- ✅ `test_revert_transaction_success` - Reversión exitosa
- ❌ `test_revert_transaction_not_found` - Transacción no encontrada
- ❌ `test_revert_transaction_not_completed` - No se puede revertir transacción no completada
- ❌ `test_revert_transaction_insufficient_funds` - Fondos insuficientes para revertir

#### Actualización de Estado (4 tests)
- ✅ `test_update_transaction_status_success` - Actualización exitosa
- ❌ `test_update_transaction_status_missing_param` - Parámetro faltante
- ❌ `test_update_transaction_status_invalid_transition` - Transición inválida
- ❌ `test_update_transaction_status_not_found` - Transacción no encontrada

#### Eliminación de Transacciones (3 tests)
- ✅ `test_delete_transaction_success` - Eliminación exitosa
- ❌ `test_delete_transaction_not_found` - Transacción no encontrada
- ✅ `test_verify_transaction_deleted` - Verificar eliminación

### In-Process Tests (Capa de Servicio) - 5 tests

- ✅ `test_service_create_transaction_validation_positive_quantity` - Validación de cantidad positiva
- ✅ `test_service_create_transaction_validation_different_accounts` - Validación de cuentas diferentes
- ✅ `test_service_update_status_valid_transitions` - Transiciones de estado válidas
- ❌ `test_service_update_status_invalid_transitions` - Transiciones de estado inválidas
- ✅ `test_service_get_transactions_by_user_filters_correctly` - Filtrado correcto por usuario

## 🚀 Instalación

Primero, instala las dependencias necesarias (si no lo has hecho ya):

```powershell
pip install -r requirements.txt
```

Las dependencias de testing ya están incluidas en `requirements.txt`:
- `pytest==9.0.1`
- `pytest-asyncio==1.3.0`
- `pytest-dependency==0.6.0`

## ▶️ Ejecutar Tests

### Ejecutar todos los tests:
```powershell
pytest test/test_api_v1.py -v
```

### Ejecutar con coverage:
```powershell
pytest test/test_api_v1.py --cov=src/transfers --cov-report=html
```

### Ejecutar un test específico:
```powershell
pytest test/test_api_v1.py::test_create_transaction_success -v
```

### Ejecutar solo tests de un tipo:
```powershell
# Solo out-of-process
pytest test/test_api_v1.py -v -k "not service"

# Solo in-process
pytest test/test_api_v1.py -v -k "service"
```

### Ejecutar tests con salida detallada:
```powershell
pytest test/test_api_v1.py -vv -s
```

## 📊 Estructura de los Tests

### Out-of-Process Tests
Estos tests utilizan el `test_client` de Quart para realizar peticiones HTTP sin necesidad de un servidor:
- Prueban los endpoints completos incluyendo validación de Quart
- Utilizan mocks para simular respuestas del servicio y base de datos
- Verifican códigos de estado HTTP y estructura de respuestas JSON
- No requieren que el servidor esté corriendo (modo testing)

### In-Process Tests
Estos tests llaman directamente a los métodos del servicio:
- Prueban la lógica de negocio sin la capa HTTP
- Verifican validaciones y transiciones de estado
- Utilizan mocks del repositorio para aislar la lógica de servicio

### Fixtures (conftest.py)
- `app`: Crea una instancia de prueba de la aplicación Quart con mocks de DB
- `client`: Proporciona un cliente de test para hacer peticiones HTTP

## 🔧 Configuración

El archivo `pytest.ini` en la raíz del proyecto configura:
- `pythonpath = .` - Permite importar módulos desde la raíz
- `testpaths = tests` - Define el directorio de tests
- `asyncio_mode = auto` - Manejo automático de tests asíncronos

## 📝 Notas

- Los tests utilizan `pytest-dependency` para gestionar dependencias entre tests
- Se utilizan mocks extensivamente para evitar dependencias de servicios externos y BD
- Los tests cubren tanto escenarios positivos (✅) como negativos (❌)
- No se requiere servidor corriendo ni MongoDB activo (todo mockeado)
- El fixture `app` en `conftest.py` maneja la configuración de testing automáticamente

## 🎯 Cobertura de Tests

Los tests cubren:
- ✅ Todas las rutas del API (POST, GET, PATCH, PUT, DELETE)
- ✅ Validaciones de entrada (cantidad positiva, cuentas diferentes)
- ✅ Manejo de errores (404, 400, 403)
- ✅ Lógica de negocio (transiciones de estado, reversiones)
- ✅ Integración con servicios externos (mocks de httpx)
- ✅ Operaciones del repositorio (mediante mocks)
