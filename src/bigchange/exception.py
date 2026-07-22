class BigChangeError(Exception):
    """Base class for all BigChange exceptions."""
    
class APIError(BigChangeError):
    """Exception raised for API errors."""
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        return f"[{self.status_code}] {self.message}" if self.message else f"[{self.status_code}]"

class AuthError(APIError):
    """Exception raised for authentication errors."""
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message, status_code)

class NotFoundError(APIError):
    """Exception raised for resource not found errors."""
    def __init__(self, message: str, status_code: int = 404):
        super().__init__(message, status_code)

class RateLimitError(APIError):
    """Exception raised for rate limit errors."""
    def __init__(self, message: str, status_code: int = 429):
        super().__init__(message, status_code)

class ClientError(APIError):
    """Exception raised for client-side errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)

class ServerError(APIError):
    """Exception raised for server-side errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code)

class TransportError(BigChangeError):
    """Exception raised for transport errors."""
    def __init__(self, message: str):
        super().__init__(message)

class NetworkError(TransportError):
    """Exception raised for network-related errors."""
    def __init__(self, message: str):
        super().__init__(message)
