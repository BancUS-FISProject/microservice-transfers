from datetime import datetime, timezone, timezone
import httpx
from aiobreaker import CircuitBreaker
from logging import getLogger
from ..core.config import settings
import os

TRANSFERS_SERVICE_URL = os.getenv("TRANSFERS_SERVICE_URL", "http://localhost:8001")
FRAUD_SERVICE_URL = os.getenv("FRAUD_SERVICE")

logger = getLogger(__name__)


class ServiceClient:
    def __init__(
        self,
        base_url: str,
        breaker_fail_max: int = settings.BREAKER_FAILS,
        breaker_timeout: int = settings.BREAKER_TIMEOUT,
        jwt: str = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.breaker = CircuitBreaker(
            fail_max=breaker_fail_max,
            timeout_duration=breaker_timeout,
        )
        self.jwt = jwt

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                http_method = getattr(client, method.lower())
                kwargs = {}
                if json is not None:
                    kwargs['json'] = json
                if params is not None:
                    kwargs['params'] = params
                
                # Propagar JWT a otros microservicios
                request_headers = headers.copy() if headers else {}
                if self.jwt and 'Authorization' not in request_headers:
                    request_headers['Authorization'] = self.jwt
                if request_headers:
                    kwargs['headers'] = request_headers

                return await self.breaker.call_async(
                    http_method,
                    url,
                    **kwargs
                )
            except Exception as exc:
                logger.error(f"HTTP {method.upper()} request to {url} failed: {exc}")
                raise

    async def patch(self, path: str, *, json: dict | None = None, headers: dict | None = None) -> httpx.Response:
        return await self.request("PATCH", path, json=json, headers=headers)

    async def debit_account(self, iban: str, amount: float) -> httpx.Response:
        return await self.patch(f"/v1/accounts/operation/{iban}/USD", json={"balance": -amount})
        #return await self.patch(f"/v1/accounts/operation/{iban}", json={"balance": -amount})

    async def credit_account(self, iban: str, amount: float) -> httpx.Response:
        return await self.patch(f"/v1/accounts/operation/{iban}/USD", json={"balance": amount})
        #return await self.patch(f"/v1/accounts/operation/{iban}", json={"balance": amount})

    async def get_account(self, iban: str) -> httpx.Response:
        return await self.request("GET", f"/v1/accounts/{iban}")
        
    async def get_sent_transactions(self, iban: str) -> httpx.Response:
        url = f"{TRANSFERS_SERVICE_URL}/v1/transactions/user/{iban}/sent"
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": self.jwt} if self.jwt else None
            return await client.get(url, headers=headers)

    async def get_fraud_check(self, sender: str, receiver: str, quantity: float) -> httpx.Response:
        url = f"{FRAUD_SERVICE_URL}/v1/antifraud/transaction-check"
        # Obtener fecha GMT de API externa
        transaction_date_iso = None
        gmt_time = await self.get_gmt_time()
        if gmt_time:
            # Convertir el string ISO a formato estándar ISO 8601 (como new Date().toISOString() en JS)
            try:
                dt = datetime.fromisoformat(gmt_time.replace('Z', '+00:00'))
                # Formato ISO 8601 estándar: YYYY-MM-DDTHH:mm:ss.sssZ
                transaction_date_iso = dt.strftime('%Y-%m-%dT%H:%M:%S.') + f'{dt.microsecond // 1000:03d}Z'
            except:
                dt = datetime.now(timezone.utc)
                transaction_date_iso = dt.strftime('%Y-%m-%dT%H:%M:%S.') + f'{dt.microsecond // 1000:03d}Z'
        else:
            # Fallback a hora local UTC si falla la API
            dt = datetime.now(timezone.utc)
            transaction_date_iso = dt.strftime('%Y-%m-%dT%H:%M:%S.') + f'{dt.microsecond // 1000:03d}Z'
        body = {
            "origin": sender,
            "destination": receiver,
            "amount": quantity,
            "transactionDate": transaction_date_iso
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": self.jwt} if self.jwt else None
            return await client.post(url, json=body, headers=headers)

    async def get_gmt_time(self) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:  # Reducido a 2 segundos
                resp = await client.get("https://timeapi.io/api/Time/current/zone?timeZone=UTC")
                logger.info(f"GMT Time API response: {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    logger.info(f"GMT Time API data: {data}")
                    return data.get("dateTime")
                else:
                    logger.warning(f"GMT Time API returned non-200 status: {resp.status_code} - {resp.text}")
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout fetching GMT time (using local UTC fallback)")
        except httpx.RequestError as e:
            logger.error(f"Request error fetching GMT time: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching GMT time: {type(e).__name__} - {e}")
        return None
