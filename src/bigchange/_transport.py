import httpx
from ._auth import TokenAuth
from ._constants import DEFAULT_TIMEOUT, DEFAULT_BASE_URL, DEFAULT_API_VERSION
from .exception import AuthError, NotFoundError, RateLimitError, ClientError, ServerError, TransportError

class Transport:
    def __init__(self, auth: TokenAuth, *, base_url: str = DEFAULT_BASE_URL, timeout: float = DEFAULT_TIMEOUT, api_version: str = DEFAULT_API_VERSION, customer_id: str):
        self._auth = auth
        self._customer_id = customer_id
        version_path = f"{base_url}/{api_version}" if api_version else base_url
        self._http = httpx.Client(base_url=version_path, timeout=timeout)

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
            return TransportError(f"Unexpected error: {message} (status code: {status_code})")
        
        
    # Debug in request to show successes to ensure it's not silent failing
    def request(self, method: str, path: str, **kwargs):
        headers = {"Authorization": f"Bearer {self._auth.get_token()}", "Accept": "application/json", "Customer-Id": self._customer_id}
        response = self._http.request(method, path, headers=headers, **kwargs)
        if response.status_code >= 400:
            raise self._map_error(response.status_code, response.text)
        if response.status_code in (200, 204):
            return response.json() if response.content else {}
        if not response.is_success:
            raise self._map_error(response.status_code, response.text)
        return response.json()
    
    def close(self) -> None:
        self._http.close()
        self._auth.close()
    