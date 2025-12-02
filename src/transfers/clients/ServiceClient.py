import httpx
from aiobreaker import CircuitBreaker
from logging import getLogger
from ..core.config import settings

logger = getLogger(__name__)


class ServiceClient:
    def __init__(
        self,
        base_url: str,
        breaker_fail_max: int = settings.BREAKER_FAILS,
        breaker_timeout: int = settings.BREAKER_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.breaker = CircuitBreaker(
            fail_max=breaker_fail_max,
            timeout_duration=breaker_timeout,
        )

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
                if headers is not None:
                    kwargs['headers'] = headers

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

    async def debit_account(self, iban: str, amount: int) -> httpx.Response:
        return await self.patch(f"/v1/accounts/operation/{iban}", json={"balance": -amount})

    async def credit_account(self, iban: str, amount: int) -> httpx.Response:
        return await self.patch(f"/v1/accounts/operation/{iban}", json={"balance": amount})

    async def get_account(self, iban: str) -> httpx.Response:
        return await self.request("GET", f"/v1/accounts/{iban}")

    async def get_gmt_time(self) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("https://timeapi.io/api/Time/current/zone?timeZone=UTC")
                logger.info(f"GMT Time API Resp: {resp.status_code} - {resp.text}")
                if resp.status_code == 200:
                    return resp.json().get("dateTime")
        except Exception as e:
            logger.error(f"Failed to fetch GMT time: {e}")
        return None
