# Documentación 

| **Autores**                    | **Microservicios Implementados**           |
| :----------------------------- | :----------------------------------------- |
| **Ariza Pomares, Jesús**       | Microservicio transferencias/transacciones |
| **Caballero Hernández, Jaime** | Microservicio transferencias/transacciones |

---

## Índice

1. [Nivel de Acabado](#1-nivel-de-acabado)
2. [Descripción de la Aplicación](#2-descripción-de-la-aplicación)
3. [Descomposición y Arquitectura](#3-descomposición-y-arquitectura)
4. [Consumo y Acuerdos de Servicio](#4-consumo)
5. [Descripción del API REST](#5-descripción-del-api-rest)
6. [Justificación de Requisitos y Evidencias](#6-justificación-de-requisitos-y-evidencias)
7. [Cumplimiento de metodología The Twelve-Factor App](#7-cumplimiento-de-metodología-the-twelve-factor-app)
8. [Análisis de Esfuerzos](#8-análisis-de-esfuerzos)
9. [Uso de Inteligencia Artificial](#9-uso-de-inteligencia-artificial)

---

## 1. Nivel de Acabado

El nivel de acabado del microservicio de transferencias/transacciones presentado es el del **10**. El microservicio incluye **6 características del microservicio avanzado** implementadas y **4 características de la aplicación basada en microservicios avanzada** implementadas (en conjunto).

### Desglose por Niveles

*   **NIVEL 5 (BÁSICO):** Microservicio básico implementado. [Ver detalles](#61-requisitos-básicos)
*   **NIVEL 7:**
    *   **Aplicación basada en microservicios básica implementada:** Interacción completa evidenciada. [Ver detalles](#aplicación-básica)
    *   **Análisis justificativo de suscripción óptima:** Realizado. [Ver detalles](#43-análisis-justificativo-de-la-suscripción-óptima-de-las-apis-del-proyecto)
    *   **3 Características avanzadas:** Superado (tiene 6).
*   **NIVEL 9:**
    *   **Mínimo 20 pruebas de componente:** Implementadas más de 20 pruebas cubriendo casos positivos y negativos. [Ver detalles](#pruebas)
    *   **API REST documentada con Swagger:** Integración automática con QuartSchema. [Ver swagger](#documentación-api)
    *   **5 Características avanzadas:** Superado (tiene 6).
    *   **3 Características de App avanzada:** Superado (tiene 4).
*   **NIVEL 10:**
    *   **6 Características avanzadas:** Implementadas. [Ver detalles](#62-microservicio-avanzado)
    *   **4 Características de App avanzada:** Implementadas. [Ver detalles](#63-aplicación-avanzada)

### Resumen de Características Implementadas

*   **MICROSERVICIO BÁSICO QUE GESTIONE UN RECURSO** - **Completo**
    *   **API REST completa:** Implementada con Quart. [Ver justificación](#api-rest-completa)
    *   **Mecanismo de Autenticación:** Implementado y funcional aprovechando nuestro API Gateway. [Ver justificación](#mecanismo-de-autenticación)
    *   **Frontend:** Realizado en el frontend genérico y final de la aplicación (además del que genera Swagger). [Ver justificación](#frontend)
    *   **Versionado API:** Accesible bajo `/v1/transactions`. [Ver justificación](#versionado-api)
    *   **Despliegue en la nube:** (Falta incluir dirección pero para el día de defensa ya estará).
    *   **Documentación API:** OpenAPI + este archivo. [Ver justificación](#documentación-api)
    *   **Persistencia NoSQL (MongoDB):** Operaciones asíncronas con Motor. [Ver justificación](#persistencia-nosql)
    *   **Validación de Datos (Pydantic):** Validación estricta de payloads. [Ver justificación](#validación-de-datos)
    *   **Imagen Docker:** [Enlace a Docker Hub](https://hub.docker.com/repository/docker/jearpo/microservice-transfers). [Ver justificación](#imagen-docker)
    *   **Gestión de Código (Github Flow):** Ramas `main`, `develop` y `fix-and-refactor` en uso. [Ver justificación](#gestión-del-código)
    *   **Integración Continua (CI/CD):** Pipeline de testing y build. [Ver justificación](#integración-continua)
    *   **Pruebas (Locales y Externas):** Tests de componente e integración. [Ver justificación](#pruebas)

*   **MICROSERVICIO AVANZADO QUE GESTIONE UN RECURSO (6 características):**
    *   **Frontend con rutas y navegación:** Repositorio de frontend. [Ver justificación](#frontend)
    *   **Caché (Redis):** Optimización de lecturas. [Ver justificación](#caché)
    *   **Consumo API Externa (TimeAPI):** Obtención de hora en formato GMT. [Ver justificación](#consumo-api-externa)
    *   **Rate Limit (Servicios Externos):** Protección de dependencias con otros microservicios. [Ver justificación](#rate-limit)
    *   **Circuit Breaker:** Resiliencia ante fallos. [Ver justificación](#circuit-breaker)
    *   **Throttling/Feature Toggles:** Gestión de capacidad. [Ver justificación](#throttling-y-feature-toggles)

*   **APLICACIÓN BASADA EN MICROSERVICIOS AVANZADA (4 características):**
    *   **Mecanismo de Autenticación JWT:** Implementado en conjunto. [Ver justificación](#mecanismo-de-autenticación)
    *   **Límites de uso por plan:** Según el costumer agreement. [Ver justificación](#límites-por-plan)
    *   **API Gateway Inteligente:** Throttling/Auth en repositorio Gateway. [Ver justificación](#api-gateway-avanzado)
    *   **Logs Comunes (Grafana):** Visualización centralizada de los logs de todos los microservicios. [Ver justificación](#logs-comunes)

---

## 2. Descripción de la Aplicación

El sistema consiste en una arquitectura de microservicios para una entidad bancaria (**BancUS**). Permite la gestión integral de cuentas bancarias, incluyendo la creación de usuarios, consultas de saldo, creación de tarjetas, transacciones, actualizaciones de estado, operaciones monetarias multidivisa y, en función del plan elegido, notificaciones, pagos programados y servicio antifraude.

---

## 3. Descomposición y Arquitectura

El proyecto se presenta con la arquitectura base y los microservicios totalmente operativos:

*   **Microservicio Transfers (este repositorio):** Funcionalidad completa CRUD y endpoints dependientes de otros microservicios. Encargado de la persistencia de transacciones, orquestación de movimientos de saldo y validación de fraude (por la conexión con otros microservicio).
*   **API Gateway**
*   **Microservicio Accounts**
*   **Microservicio User Auth**
*   **Microservicio Bank Statements**
*   **Microservicio Anti Fraud**
*   **Microservicio Scheduled Payments**
*   **Microservicio Notifications**
*   **Microservicio Currencies**
*   **Microservicio Cards**

## 4. Consumo

### 4.1. Customer Agreement

**Semántica HTTP**
*   `200 OK`: Operaciones de lectura y modificación síncronas exitosas.
*   `202 Accepted`: Transferencias creadas correctamente.
*   `400 Bad Request`: Errores de validación de esquema o lógica de negocio (ej: saldo insuficiente).
*   `401 Unauthorized`: Token JWT faltante o inválido.
*   `403 Forbidden`: Token válido pero operación no permitida (ej: usuario intentando ver transacciones de otro).
*   `503 Service Unavailable`: Fallo en dependencias críticas (Accounts, Redis) gestionado por Circuit Breaker.

### 4.2. Planes de precios

| Plan            | Precio     | Límites y características funcionales                          |
| :-------------- | :--------- | :------------------------------------------------------------- |
| **Básico**      | 0 €/mes    | 5 operaciones/mes. Sin pagos programados ni antifraude.        |
| **Estudiante**  | 4,99 €/mes | 20 operaciones/mes. Notificaciones y antifraude.               |
| **Profesional** | 9,99 €/mes | Operaciones ilimitadas. Pagos programados, historial completo. |

### 4.3. Análisis justificativo de la suscripción óptima de las APIs del proyecto

La suscripción óptima se define como la de menor coste que mantiene un margen de seguridad suficiente para la carga prevista en la demostración y para un escenario realista de crecimiento, evitando sobredimensionar gasto.

En el caso de este microservicio (**Transfers**) y su ecosistema, las necesidades de APIs externas se concentran en: la **sincronización horaria inmutable** (TimeAPI) y, a nivel de aplicación, la **mensajería de notificaciones** (SendGrid).

#### Sincronización Horaria: TimeAPI

Para garantizar la integridad y trazabilidad de las transacciones con una fuente de tiempo inmutable, se utiliza **TimeAPI**.

*   **Plan Actual:** Gratuito (Público).
*   **Justificación:** TimeAPI es un servicio abierto que no requiere clave de API para uso estándar moderado. El volumen de transacciones de para este proyecto es perfecto para su uso. Se implementa además un fallback a hora local en caso de fallo.

#### Notificaciones por email: Twilio SendGrid Email API (Nivel de Aplicación)

Aunque este microservicio delega el envío, la aplicación utiliza **SendGrid** para notificar eventos.

*   **Plan Actual:** **Free Trial**.
*   **Justificación:** Ofrece **100 correos/día**. Aún asumiendo un flujo conservador de eventos operativos, el límite diario cubre holgadamente la ejecución sin problemas para el proyecto.

#### Relación con otros Microservicios (Dependencias Internas)

Además de las APIs externas, este microservicio orquesta operaciones con otros servicios del ecosistema **BancUS**:

*   **Microservice Accounts:**
    *   **Suscripción/Uso:** Síncrono (Crítico).
    *   **Endpoints:** `GET /v1/accounts/{iban}` (validación), `PATCH /v1/accounts/operation/{iban}/USD` (cargo/abono).
    *   **Justificación:** Delegación de la gestión de saldo y consistencia de cuentas.
*   **Microservice Anti Fraud:**
    *   **Suscripción/Uso:** Síncrono (Validación previa).
    *   **Endpoint:** `POST /v1/fraud-alerts/check`.
    *   **Justificación:** Análisis de riesgo en tiempo real.
*   **Microservice Notifications:**
    *   **Suscripción/Uso:** Asíncrono.
    *   **Endpoint:** `POST /v1/notifications/events`.
    *   **Justificación:** Envío de correos transaccionales sin bloquear el flujo principal de respuesta al usuario.

---

## 5. Descripción del API REST

**Microservicio Transfers (Python / Quart)**
Generación automática de documentación OpenAPI mediante `QuartSchema`.

**Prefijo:** `/v1/transactions`

### Detalles de la API y Ejemplos de uso

El API se ha diseñado utilizando recursos RESTful estándar. A continuación se detallan las operaciones principales y el formato de datos esperado.

**Modelo de Creación de Transacción (`TransactionCreate`)**
```json
{
  "sender": "ES1234567890",
  "receiver": "ES0987654321",
  "quantity": 150.50
}
```

**Ejemplo de Transacción Creada (Respuesta Completa)**
```json
{
  "id": "64f9c32a1b2c3d4e5f6a7b8c",
  "sender": "ES1234567890",
  "receiver": "ES0987654321",
  "quantity": 150.50,
  "status": "completed",
  "currency": "USD",
  "date": "2023-10-27T10:00:00Z",
  "gmt_time": "2023-10-27T10:00:00+00:00",
  "sender_balance": 1500.00,
  "receiver_balance": 2500.50
}
```

| Método   | Endpoint                | Descripción                                                                                               | Payload / Params         | Respuestas                                                 |
| :------- | :---------------------- | :-------------------------------------------------------------------------------------------------------- | :----------------------- | :--------------------------------------------------------- |
| `POST`   | `/`                     | **Crear Transacción:** Inicia una transferencia de fondos. Valida saldo y actualiza cuentas atómicamente. | JSON `TransactionCreate` | `202` (Éxito), `400` (Error Saldo), `503` (Error Accounts) |
| `GET`    | `/<iban>`               | **Detalle:** Obtiene información completa de una transacción por su IBAN.                                 | IBAN en URL              | `200` (JSON `TransactionView`), `404`                      |
| `GET`    | `/user/<iban>/sent`     | **Historial Enviadas:** Lista transacciones donde el usuario es remitente.                                | IBAN Usuario             | `200` (Array `TransactionView`)                            |
| `GET`    | `/user/<iban>/received` | **Historial Recibidas:** Lista transacciones donde el usuario es receptor.                                | IBAN Usuario             | `200` (Array `TransactionView`)                            |
| `PATCH`  | `/<iban>`               | **Revertir:** Deshace una transacción completada (devolución de fondos).                                  | IBAN en URL              | `200`, `400` (Si no es reversible)                         |
| `DELETE` | `/<iban>`               | **Borrar:** Eliminación lógica de transacciones fallidas o pendientes.                                    | IBAN en URL              | `200`, `400` (Si ya completada)                            |
| `PUT`    | `/<iban>/status`        | **Actualizar Estado:** Cambio manual de estado (Admin/Sistema).                                           | JSON `{"status": "..."}` | `200`                                                      |

### API de Administración y Health Check

Además de la API transaccional, el microservicio expone endpoints de gestión para monitorización y operación avanzada.

**Prefijo:** `/v1/admin`

| Método | Endpoint                          | Descripción                                                                                                            |
| :----- | :-------------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| `GET`  | `/health`                         | **Health Check:** Estado vital del servicio, métricas de CPU/Memoria y nivel de throttling. Necesario para Kubernetes. |
| `GET`  | `/metrics`                        | **Métricas del Sistema:** Información detallada para monitorización (Prometheus/Grafana).                              |
| `GET`  | `/features`                       | **Feature Toggles:** Lista el estado (ON/OFF) de todas las funcionalidades.                                            |
| `POST` | `/features/<name>/enable`         | **Activar Feature:** Habilita una feature toggle en caliente.                                                          |
| `POST` | `/features/<name>/disable`        | **Desactivar Feature:** Deshabilita una feature toggle en caliente.                                                    |
| `POST` | `/emergency/disable-non-critical` | **Modo Emergencia:** Desactiva todas las funciones no críticas para recuperar estabilidad.                             |
| `POST` | `/emergency/restore`              | **Restaurar:** Vuelve al funcionamiento normal desactivando el modo emergencia.                                        |

### API Auxiliar Integrada: TimeAPI (Consumo interno)

El servicio consume la siguiente API externa para obtener la hora GMT precisa:

| Método | Endpoint                                                | Descripción                                                                         |
| :----- | :------------------------------------------------------ | :---------------------------------------------------------------------------------- |
| `GET`  | `https://timeapi.io/api/Time/current/zone?timeZone=UTC` | Obtiene la fecha y hora actual en zona UTC. Usada para sellado de tiempo inmutable. |

---

## 6. Justificación de Requisitos y Evidencias

### 6.1. Requisitos Básicos

#### API REST Completa
**Justificación:** Se han implementado todos los verbos HTTP necesarios para la gestión del ciclo de vida del recurso `Transaction`. Se usa el decorador `@bp` de Quart para mapear rutas a funciones asíncronas.
*   **Código:** `src/transfers/api/v1/Transactions_blueprint.py`
    ```python
    @bp.post("/")  # POST: Creación
    async def create_transaction(data: TransactionCreate): ...
    
    @bp.get("/<string:id>") # GET: Lectura
    async def get_transaction(id: str): ...

    @bp.delete("/<string:id>") # DELETE: Borrado
    async def delete_transaction(id: str): ...
    
    @bp.put("/<string:id>/status") # PUT: Actualización completa/estado
    async def put_status(id: str, data: StatusUpdateRequest): ...
    ```

#### Mecanismo de Autenticación
**Justificación:** Aunque la validación principal ocurre en el API Gateway, este microservicio requiere conocer la identidad del usuario para autorizar operaciones. Decodifica el JWT y lo propaga a microservicios dependientes.
*   **Código:** `src/transfers/clients/ServiceClient.py` (Propagación)
    ```python
    # Propagar JWT a otros microservicios para mantener la sesión
    if self.jwt and 'Authorization' not in request_headers:
        request_headers['Authorization'] = self.jwt
    ```
*   **Código:** `src/transfers/api/v1/Transactions_blueprint.py` (Validación de propiedad)
    ```python
    _, token = auth_header.split(" ")
    jwt_data = decode_jwt(token) # Decodifica payload
    if jwt_iban != data.sender: # Verifica ownership
        abort(403, description="Unauthorized access")
    ```

#### Frontend
**Justificación:** El frontend se ha desarrollado en React dentro del repositorio *BancUS-frontend*. Aunque es externo a este repo, su existencia es requisito.
*   [Enlace al Repositorio Frontend](https://github.com/BancUS-FISProject/BancUS-frontend)

#### Versionado API
**Justificación:** Se utiliza un prefijo `/v1` en todas las rutas para un correcto versionado y cambios futuros.
*   **Código:** `src/transfers/api/v1/Transactions_blueprint.py`
    ```python
    bp = Blueprint("transfers_v1", __name__, url_prefix="/v1/transactions")
    ```

#### Documentación API
**Justificación:** La documentación OpenAPI (Swagger) se genera automáticamente gracias a `quart-schema` y esta cuenta con los esquemas y códigos necesarios.
*   **Código:** `src/transfers/app.py`
    ```python
    schema = QuartSchema()
    # ... Configuración de Swagger UI en /api/docs
    schema.init_app(app)
    ```

#### Persistencia NoSQL
**Justificación:** Se utiliza MongoDB por su flexibilidad de esquema.
*   **Código:** `src/transfers/db/TransfersRepository.py`
    ```python
    class TransfersRepository:
        def __init__(self, db):
            self.collection = db["transactions"] # Colección MongoDB
        
        async def create_transaction(self, transaction: dict) -> str:
            result = await self.collection.insert_one(transaction) # Insert asíncrono
            return str(result.inserted_id)
    ```

#### Validación de Datos
**Justificación:** Se utilizan modelos **Pydantic** para garantizar la integridad de los datos.
*   **Código:** `src/transfers/models/Transactions.py`
    ```python
    class TransactionCreate(BaseModel):
        sender: str
        receiver: str
        quantity: float # Pydantic validará tipos automáticamente
    ```

#### Imagen Docker
**Justificación:** El servicio se empaqueta en una imagen Docker que se actualiza gracias al flujo de trabajo y despliegue con GitHub.
*   [Hub: jearpo/microservice-transfers](https://hub.docker.com/repository/docker/jearpo/microservice-transfers)

#### Gestión del Código
**Justificación:** Se sigue Github Flow con ramas protegidas (`main`, `develop`, `fix-and-refactor`).

#### Integración Continua
**Justificación:** Se utiliza **GitHub Actions** para automatizar el ciclo de vida del software.
El flujo incluye:
1.  **Service Containers:** Levanta instancias efímeras de MongoDB y Redis para pruebas reales.
2.  **API Testing:** Arrancamos el microservicio en *background* y ejecutamos la suite de tests.
3.  **Build & Push:** Si los tests pasan, construye la imagen Docker y la sube a Docker Hub.
*   **Código:** `.github/workflows/cicd-test-docker-pipeline.yml`
*    **Ejemplo del Job de Testing:**

        ```yaml
        jobs:
            api-test:
                services:
                redis:
                    image: redis
                mongo:
                    image: mongo:latest
                steps:
                - name: Init API in background
                    run: |
                    uvicorn src.transfers.app:create_app --factory --host 0.0.0.0 --port 8000 &
                    sleep 5
                - name: Exec Pytest
                    run: pytest -v

*    **Ejemplo del Job de Build & Push:**

        ```yaml
        build-and-push:
            needs: api-test  # Solo si los tests pasan
            steps:
            - name: Build and push image
                uses: docker/build-push-action@v5
                with:
                push: true
                tags: |
                    ${{ env.IMAGE_NAME }}:latest
                    ${{ env.IMAGE_NAME }}:${{ github.sha }}

#### Pruebas
**Justificación:** Se han implementado **más de 20 pruebas automatizadas (39)** que cubren no solo la lógica básica (CRUD), sino también escenarios complejos de resiliencia y gestión de capacidad (Nivel 10). Usamos `pytest` y `httpx` para tests de integración asíncronos reales.
*   **Código:** `test_capacity_management.py` (Suite de pruebas de integración)
    **Ejemplo: Test de Feature Toggles (Activar/Desactivar funcionalidad en caliente)**
    Verifica que podemos apagar el endpoint de borrado dinámicamente sin reiniciar el servidor.
    ```python
    async def test_feature_toggles():
        async with httpx.AsyncClient() as client:
            # 1. Desactivar 'transaction_delete' vía API Admin
            await client.post(f"{API_V1}/admin/features/transaction_delete/disable")
            
            # 2. Intentar borrar una transacción (Debe fallar con 503)
            response = await client.delete(f"{API_V1}/transactions/test123")
            assert response.status_code == 503  # Service Unavailable
            
            # 3. Reactivar funcionalidad
            await client.post(f"{API_V1}/admin/features/transaction_delete/enable")
    ```
### 6.2. Microservicio Avanzado

#### 1. Caché (Redis)
**Implementación:** Primero consulta Redis: si hay acierto (**HIT**), se devuelve el JSON inmediato. Si falla (**MISS**), se busca en MongoDB y se actualiza la caché (**Lazy Loading**).

**Código (`src/transfers/db/RedisCachedTransfersRepository.py`):**
```python
class RedisCachedTransfersRepository(TransfersRepository):
    # Patrón Decorator: Hereda del repositorio base
    async def find_transaction_by_id(self, id_str: str) -> dict | None:
        key = self._get_transaction_key(id_str)
        
        # 1. READ-THROUGH: Intentar leer de caché (Rápido)
        if cached_data := await self.redis.get(key):
            logger.info("Cache HIT")
            return json.loads(cached_data)

        # 2. FALLBACK: Leer de base de datos (Lento)
        transaction = await super().find_transaction_by_id(id_str)
        
        # 3. CACHE-ASIDE: Refrescar caché para futuras lecturas
        if transaction:
            await self.redis.set(key, json.dumps(transaction), ex=self.ttl)
            
        return transaction
```

#### 2. Consumo API Externa (TimeAPI)
**Implementación:**
El cliente HTTP implementa un **Timeout estricto de 2.0 segundos** para la llamada externa. Si el servicio externo no responde en ese tiempo, se captura la excepción `httpx.TimeoutException` y se degradan las funcionalidades usando la hora local (Fallback), garantizando que el microservicio no se bloquee.

**Explicación:**
La función `get_gmt_time` demuestra un diseño defensivo:
1.  **Context Manager Asíncrono (`async with httpx.AsyncClient...`):** Se crea un cliente HTTP efímero que garantiza el cierre de conexiones al terminar el bloque.
2.  **Timeout Explícito (`timeout=2.0`):** Se justifica para evitar que la API externa lo deje en espera indefinida.
3.  **Manejo de Excepciones Específico:** Se capturan errores concretos (`httpx.TimeoutException`, `httpx.RequestError`) en lugar de un `Exception` genérico al principio. Esto permite diferenciar entre un servicio lento (timeout) y uno caído o inaccesible (request error).
4.  **Graceful Degradation:** En caso de fallo, la función devuelve `None` (o hace fallback en el uso), permitiendo que el flujo  de la transacción continúe con la hora local, priorizando la disponibilidad del servicio.

**Código (`src/transfers/clients/ServiceClient.py`):**
```python
async def get_gmt_time(self) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:  # Reducido a 2 segundos
            resp = await client.get("https://timeapi.io/api/Time/current/zone?timeZone=UTC")
            logger.info(f"GMT Time API response: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                return data.get("dateTime")
            else:
                logger.warning(f"GMT Time API returned non-200 status: {resp.status_code}")
    except httpx.TimeoutException as e:
        logger.warning(f"Timeout fetching GMT time (using local UTC fallback)")
    except httpx.RequestError as e:
        logger.error(f"Request error fetching GMT time: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching GMT time: {type(e).__name__} - {e}")
    return None
```

#### 3. Rate Limit
**Implementación:**
Middleware personalizado (`RateLimiter`) inyectado en el ciclo de vida de `Quart`. Utiliza Redis para mantener contadores atómicos por ventana de tiempo. Si el contador supera el umbral configurado, se aborta la petición con `429 Too Many Requests`.

**Explicación:**
La clase `RateLimiter` se engancha al hook `before_request` de Quart, ejecutándose antes de cada vista:
1.  **Identificación (`client_ip`):** Se extrae la IP del origen de la petición.
2.  **Clave Temporal (`rate_limit:{ip}:{minuto}`):** Se genera una clave única en Redis que combina la IP del usuario y el minuto actual (ventana de tiempo).
3.  **Atomicidad (`await redis.incr(key)`):** Se utiliza la operación atómica `INCR` de Redis. Esto es crítico en entornos distribuidos para evitar condiciones de carrera si dos peticiones llegan al mismo instante exacto; Redis garantiza la cuenta correcta.
4.  **Expiración Automática (`expire`):** Se establece un TTL a la clave del contador igual a la ventana de tiempo, asegurando que Redis no se llene de claves antiguas de IPs que ya no visitan el sitio (limpieza automática).

**Código Completo (`src/transfers/middleware/RateLimiter.py`):**
```python
class RateLimiter:
    def __init__(self, app, limit=50, window=60):
        self.app = app
        self.limit = limit
        self.window = window
        self.app.before_request(self.check_limit)

    async def check_limit(self):
        redis = getattr(self.app, 'redis_client', None)
        # ... (código de obtención de IP) ...
        current_minute = int(time.time() // self.window)
        key = f"rate_limit:{client_ip}:{current_minute}"

        current_count = 0
        try:
            current_count = await redis.incr(key)
            if current_count == 1:
                await redis.expire(key, self.window)
        except Exception as e:
            logger.error(f"Rate limiter Redis error: {e}")
            return

        if current_count > self.limit:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            abort(429, description="Too Many Requests")
```

#### 4. Circuit Breaker (Resiliencia entre Servicios)
**Implementación:**
Se configura un Circuit Breaker con `fail_max=5` y `timeout=60s`. Si se detectan 5 fallos consecutivos de conexión, el breaker pasa al estado abierto, rechazando nuevas llamadas durante 60 segundos.

**Explicación:**
Se utiliza la librería `aiobreaker`, diseñada para `asyncio`:
1.  **Decoración/Wrap (`self.breaker.call_async`):** En lugar de llamar directamente a HTTP, envolvemos la llamada en el objeto `breaker`. Esto centraliza la lógica de control de fallos.
2.  **Detección de "Servicio Caído":** Si la petición a `url` lanza una excepción (como `ConnectionError` o `Timeout`), el breaker incrementa su contador interno de fallos.
3.  **Apertura del Circuito (Fail Fast):** Al llegar a `fail_max`, el breaker deja de intentar la petición real y lanza inmediatamente una excepción `CircuitBreakerError`. Esto justifica el principio de *Resiliencia*: mejor fallar rápido y liberar recursos locales que mantener hilos bloqueados esperando a un servicio muerto.

**Código Completo (`src/transfers/clients/ServiceClient.py`):**
```python
class ServiceClient:
    def __init__(self, base_url: str, breaker_fail_max: int = 5, breaker_timeout: int = 60, ...):
        self.breaker = CircuitBreaker(
            fail_max=breaker_fail_max,
            timeout_duration=breaker_timeout,
        )

    async def request(self, method: str, path: str, ...):
        # ... (preparación de request) ...
        return await self.breaker.call_async(
            http_method,
            url,
            **kwargs
        )
```

#### 5. Throttling y Feature Toggles (Gestión de Capacidad)
**Implementación:**
Se implementa un `ThrottlingManager` que monitoriza métricas del sistema. Si se superan los umbrales críticos, el sistema rechaza nuevas peticiones.

**Explicación del Código:**
1.  **Throttling Dinámico:** La función `calculate_throttle_level` evalúa el estado actual del servidor (CPU/Memoria). No usa valores estáticos, sino que se adapta en tiempo real (`psutil.cpu_percent`). Esto justifica una autoprotección del sistema: si estamos al 90% de RAM, es irresponsable aceptar más peticiones de escritura.
2.  **Feature Toggles en Redis:** El método `is_enabled` consulta una clave externa (`feature_toggle:transaction_create`). Esto desacopla el despliegue de la configuración.

**Código (`src/transfers/core/throttling.py` - Lógica de Decisión):**
```python
def calculate_throttle_level(self) -> tuple[int, str]:
    metrics = self._current_metrics
    level = ThrottlingLevel.NONE
    
    # Verificar CPU
    if metrics.cpu_percent >= self.config.cpu_critical:
        level = max(level, ThrottlingLevel.CRITICAL)
    elif metrics.cpu_percent >= self.config.cpu_warning:
        level = max(level, ThrottlingLevel.MEDIUM)
    
    # Verificar Memoria y Requests Concurrentes...
    return level, reason

def should_reject_request(self) -> tuple[bool, str]:
    level, reason = self.calculate_throttle_level()
    if level >= ThrottlingLevel.CRITICAL:
        return True, f"Sistema sobrecargado: {reason}"
    return False, reason
```

**Código (`src/transfers/core/feature_toggles.py` - Gestión Redis):**
```python
async def is_enabled(self, feature: Feature) -> bool:
    if self.redis_client:
        try:
            key = f"feature_toggle:{feature.value}"
            value = await self.redis_client.get(key)
            if value is not None:
                return value.lower() in ('true', '1', 'yes', 'on')
        except Exception as e:
            logger.warning(f"Redis error checking toggle: {e}")
    return self.defaults.get(feature, True)
```

#### 6. Frontend
**Justificación:** El frontend se puede encontrar en el repositorio ya mencionado del mismo donde se implementa en el apartado de transacciones las funcionalidades lógicas y necesarias para poder usar la aplicación desde el punto de vista al usuario.

Se excluyen algunas funcionalidades/endpoints como las administrativas o las de borrado permanente.

### 6.3. Aplicación Avanzada

*   **Implementar un mecanismo de autenticación basado en JWT o equivalente.**
    Como se acordó en el último seguimiento, al ser realizado por todas las parejas (delegado en el Servidor de Auth pero validado aquí), esta característica se considera de "Aplicación basada en microservicios avanzada".
    
    *   **Código (`src/transfers/api/v1/Transactions_blueprint.py`):**
        ```python
        # Extracción y decodificación del JWT para obtener el 'iban' del usuario autenticado
        # y asegurar que coincide con el remitente de la transacción (Evitar suplantación).
        auth_header = request.headers.get('Authorization')
        _, token = auth_header.split(" ")
        jwt_data = decode_jwt(token)
        
        if jwt_data.get('iban') != data.sender:
             abort(403, description="Unauthorized access")
        ```

*   **Incluir en el plan de precios límites de uso y aplicarlos automáticamente según la suscripción del usuario.**
    Se limitan las transacciones según el plan del usuario (Básico: 5, Estudiante: 10, Pro: Infinito).
    
    *   **Código (`src/transfers/services/Transfers_service.py`):**
        ```python
        subscription_limits = {
            "basico": 5,
            "estudiante": 10,
            "pro": float('inf')
        }
        
        # Validación mensual de operaciones
        limit = subscription_limits.get(sender_subscription, 0)
        if completed_this_month >= limit:
            raise ValueError(f"Monthly transaction limit reached for {sender_subscription}")
        ```

*   **Hacer uso de un API Gateway con funcionalidad avanzada como un mecanismo de throttling o de autenticación.**
    [Ver configuración API Gateway](https://github.com/BancUS-FISProject/api-gateway/blob/main/nginx.conf). Tanto el API Gateway como el microservicio implementan Throttling.

    * **Código:** https://github.com/BancUS-FISProject/api-gateway

*   **Cualquier otra extensión a la aplicación basada en microservicios básica acordada previamente con el profesor.**
    Sistema de logs comunes con Grafana (ver en contenedor de Grafana). Todos los servicios emiten logs estructurados que Promtail puede ingerir.
    
    *   **Código (`src/transfers/core/logging_config.py`):**
        ```python
        # --- Console Handler (STDOUT) ---
        # Fundamental para que Docker/Kubernetes capturen los logs
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(settings.LOG_LEVEL)

        file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s:     %(message)s"
        )
        logger.addHandler(console_handler)
        ```
---

## 7. Cumplimiento de metodología The Twelve-Factor App

A continuación se detalla cómo la arquitectura del microservicio **Transfers** cumple con los doce factores estándar para aplicaciones nativas de nube:

### 1. Codebase (Código Base)
*   **Principio:** Un repositorio, múltiples despliegues.
*   **Implementación:** El código de este microservicio se gestiona en un único repositorio Git. Se utiliza el mismo código base para los despliegues en local (Docker Compose) y en producción (si se diera el caso), inyectando las diferencias únicamente mediante variables de entorno.

### 2. Dependencies (Dependencias)
*   **Principio:** Declarar y aislar dependencias explícitamente.
*   **Implementación:**
    *   **Transfers (Python):** Las dependencias se declaran explícitamente en `requirements.txt` (quart, motor, pydantic, etc.).
    *   El uso de imágenes Docker garantiza que el entorno de ejecución sea idéntico y esté aislado, sin depender de librerías del sistema del host.

### 3. Config (Configuración)
*   **Principio:** Guardar la configuración en el entorno.
*   **Implementación:** Se mantiene separación estricta de configuración y código usando `pydantic-settings`.
    *   Datos sensibles (Mongo URI, Redis Host, URLs de microservicios, Docker Hub) se inyectan mediante variables de entorno (`.env` en local, Secrets en CI/CD).

### 4. Backing Services (Servicios de Respaldo)
*   **Principio:** Tratar los servicios de respaldo como recursos conectables.
*   **Implementación:**
    *   **Persistencia:** MongoDB se consume vía URI de conexión configurable.
    *   **Caché:** Redis se conecta mediante host/puerto configurables.
    *   **Dependencias:** El microservicio *Accounts* se trata como un recurso externo accesible vía URL.
    *   El código no distingue si estos servicios son locales o gestionados en la nube; solo necesita la configuración de conexión.

### 5. Build, Release, Run (Construir, Desplegar, Ejecutar)
*   **Principio:** Separación estricta de etapas.
*   **Implementación:**
    *   **Build:** GitHub Actions construye la imagen Docker a partir del código.
    *   **Release:** La imagen versionada se combina con la configuración del entorno (docker-compose).
    *   **Run:** Se ejecutan los contenedores instanciando la imagen inmutable. No se hacen cambios de código en caliente en el contenedor en ejecución.

### 6. Processes (Procesos)
*   **Principio:** Ejecutar la aplicación como uno o más procesos sin estado (Stateless).
*   **Implementación:**
    *   El servicio **Transfers** es *stateless*. No guarda estado de sesión en memoria local.
    *   Cualquier persistencia o estado compartido se delega a **MongoDB** o **Redis**. Esto permite escalar horizontalmente añadiendo más réplicas del contenedor sin problemas de coherencia.

### 7. Port Binding (Asignación de Puertos)
*   **Principio:** Exportar servicios mediante asignación de puertos.
*   **Implementación:**
    *   La aplicación Python (Quart) no depende de un servidor de aplicaciones externo inyectado (como Apache/Tomcat).
    *   Utiliza **Uvicorn** para exportar el servicio en el puerto configurado.

### 8. Concurrencia (Concurrency)
*   **Principio:** Escalar mediante el modelo de procesos.
*   **Implementación:**
    *   El modelo asíncrono de Quart permite manejar alta concurrencia con un solo proceso.

### 9. Disposability (Desechabilidad)
*   **Principio:** Maximizar la robustez con un arranque rápido y un cierre elegante.
*   **Implementación:**
    *   Los contenedores arrancan en segundos.
    *   El diseño es tolerante a fallos (Circuit Breakers) si otras piezas desaparecen repentinamente.

### 10. Dev/Prod Parity (Paridad Desarrollo/Producción)
*   **Principio:** Mantener desarrollo, preproducción y producción lo más parecidos posible.
*   **Implementación:**
    *   Se utiliza `docker-compose` en local para replicar la arquitectura distribuida.

### 11. Logs (Traza)
*   **Principio:** Tratar los logs como flujos de eventos.
*   **Implementación:**
    *   La aplicación escribe logs estructurados a `stdout` (salida estándar).
    *   No gestiona archivos de log internos. La infraestructura (Docker) captura estos flujos para su centralización y visualización (ej. Grafana).

### 12. Admin Processes (Procesos Administrativos)
*   **Principio:** Ejecutar las tareas de gestión/administración como procesos puntuales.
*   **Implementación:**
    *   Expuestos de forma controlada a través de endpoints seguros en los endpoints de administración.

---

## 8. Análisis de Esfuerzos

A continuación se detalla la estimación de horas dedicadas por cada integrante:

| Integrante                    | Actividad Principal                               | Horas (Aprox.) |
| :---------------------------- | :------------------------------------------------ | :------------- |
| **Jesús Ariza Pomares**       | Diseño Arquitectura, Docker, CI/CD, Documentación | XX h           |
| **Jaime Caballero Hernández** | Frontend, Lógica Negocio, Integración, Tests      | XX h           |
| **TOTAL**                     |                                                   | **XX h**       |

---

## 9. Uso de Inteligencia Artificial

Se ha utilizado la inteligencia artificial **Gemini 3 Pro** como herramienta de apoyo durante el desarrollo. Su uso se ha limitado estrictamente a:

1.  **Consulta Técnica:** Resolución de dudas específicas o errores oscuros que no se encontraban con claridad en documentación convencional.
2.  **Código Boilerplate:** Generación de estructuras repetitivas (modelos Pydantic, esqueletos de rutas) para agilizar el desarrollo.
3.  **Scripting de Pruebas:** Generación de scripts auxiliares para verificar funcionalidades locales y tests de integración.
4.  **Debugging y Corrección:** Detección de errores sutiles en el código y sugerencias de corrección.

Todas las decisiones de diseño y lógica de negocio compleja son autoría del equipo.