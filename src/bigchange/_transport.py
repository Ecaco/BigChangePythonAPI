import time
import random
import logging

import httpx
from ._auth import TokenAuth
from ._constants import DEFAULT_TIMEOUT, DEFAULT_BASE_URL, DEFAULT_API_VERSION, RETRYABLE_STATUS_CODES, IDEMPOTENT_METHODS
from .exception import AuthError, NotFoundError, RateLimitError, ClientError, ServerError, TransportError, NetworkError

logger = logging.getLogger(__name__)

class Transport:
    def __init__(
        self,
        auth: TokenAuth,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        api_version: str = DEFAULT_API_VERSION,
        customer_id: str,
        retryable_status_codes: set[int] = RETRYABLE_STATUS_CODES,
        idempotent_methods: set[str] = IDEMPOTENT_METHODS,
        max_attempts: int = 3,
        backoff_base: float = 0.5,
        backoff_cap: float = 30.0,
        deadline: float = 120.0,
        sleep=time.sleep,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self._auth = auth
        self._customer_id = customer_id
        version_path = f"{base_url}/{api_version}" if api_version else base_url
        self._http = httpx.Client(base_url=version_path, timeout=timeout)

        self._retryable_status_codes = retryable_status_codes
        self._idempotent_methods = idempotent_methods
        self._max_attempts = max_attempts
        self._backoff_base = backoff_base
        self._backoff_cap = backoff_cap
        self._deadline = deadline
        self._sleep = sleep


    def _send(self, method: str, path: str, **kwargs) -> httpx.Response:
        headers = {
            "Authorization": f"Bearer {self._auth.get_token()}",
            "Accept": "application/json",
            "Customer-Id": self._customer_id,
        }
        try:
            return self._http.request(method, path, headers=headers, **kwargs)
        except httpx.RequestError as exc:
            raise NetworkError(str(exc)) from exc

    def _handle_response(self, response: httpx.Response):
        if response.status_code >= 400:
            raise self._map_error(response.status_code, response.text)
        if not response.content:
            return None
        return response.json()


    def _parse_retry_after(self, response: httpx.Response) -> float | None:
        raw = response.headers.get("Retry-After")
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError:
            return None 

    def _backoff(self, attempt: int, retry_after: float | None = None) -> float:
        if retry_after is not None:
            return retry_after
        ceiling = min(self._backoff_cap, self._backoff_base * 2 ** attempt)
        return random.uniform(0, ceiling)

    def _map_error(self, status_code: int, message: str):
        if status_code == 401:
            return AuthError(message, status_code)
        elif status_code == 404:
            return NotFoundError(message, status_code)
        elif status_code == 429:
            return RateLimitError(message, status_code)
        elif 400 <= status_code < 500:
            return ClientError(message, status_code)
        elif 500 <= status_code < 600:
            return ServerError(message, status_code)
        else:
            return TransportError(
                f"Unexpected error: {message} (status code: {status_code})"
            )


    def request(self, method: str, path: str, **kwargs):
        can_retry = method.upper() in self._idempotent_methods
        started = time.monotonic()
        last_error = None

        for attempt in range(self._max_attempts):
            retry_after = None

            try:
                response = self._send(method, path, **kwargs)
            except NetworkError as exc:
                last_error = exc
            else:
                if response.status_code not in self._retryable_status_codes:
                    return self._handle_response(response)
                retry_after = self._parse_retry_after(response)
                last_error = self._map_error(response.status_code, response.text)

            if not can_retry:
                raise last_error

            if attempt == self._max_attempts - 1:
                break

            delay = self._backoff(attempt, retry_after)
            if time.monotonic() - started + delay > self._deadline:
                logger.warning(
                    "Retry deadline reached for %s %s after %d attempt(s)",
                    method, path, attempt + 1,
                )
                break

            logger.warning(
                "Retrying %s %s after %s (attempt %d/%d, sleeping %.2fs)",
                method, path, last_error, attempt + 1,
                self._max_attempts, delay,
            )
            self._sleep(delay)

        raise last_error

    def close(self) -> None:
        self._http.close()
        self._auth.close()