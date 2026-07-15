import httpx

class TokenAuth: 
    def __init__(self, client_id: str, client_secret: str, grant_type: str = "client_credentials",
                 *, token_url: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._grant_type = grant_type
        self._token_url = token_url
        self._token: str | None = None
    
    def get_token(self) -> str:
        if self._token is None:
            self._token = self._fetch_token()
        return self._token
    
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
    
    def close(self):
        """Close the underlying HTTP client."""
        self.http.close()

    
