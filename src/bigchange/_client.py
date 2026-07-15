import httpx

from src.bigchange._constants import DEFAULT_TIMEOUT, DEFAULT_BASE_URL, DEFAULT_API_VERSION
from src.bigchange._transport import Transport

class BigChange:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, default_api_version: str = DEFAULT_API_VERSION, 
                 timeout: float = DEFAULT_TIMEOUT, transport: Transport | None = None):
        
        self._transport = transport or Transport(api_key=api_key, base_url=base_url, api_version=default_api_version, timeout=timeout)
        
    def _fetch_token(self) -> str:
        response = httpx.post(
            self._token_url,
            data={
                "grant_type": self._grant_type,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    
    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "BigChange":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
