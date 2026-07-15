import httpx
import pytest
import respx

from bigchange._transport import Transport
from bigchange.exception import AuthError, NotFoundError, RateLimitError, ClientError, ServerError, TransportError


class FakeAuth:
    """Stub — no OAuth, no network. The composition payoff."""
    def get_token(self) -> str:
        return "fake-token"
    def close(self) -> None:
        pass


@pytest.fixture
def transport():
    return Transport(FakeAuth(), base_url="https://api.test", api_version="v1", timeout=5.0, customer_id="test-customer")


@respx.mock
def test_200_returns_parsed_json(transport):
    respx.get("https://api.test/v1/ping").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    assert transport.request("GET", "/ping") == {"ok": True}


@respx.mock
def test_401_raises_auth_error(transport):
    respx.get("https://api.test/v1/ping").mock(
        return_value=httpx.Response(401, json={"message": "bad credentials"})
    )
    with pytest.raises(AuthError) as exc_info:
        transport.request("GET", "/ping")
    assert exc_info.value.status_code == 401

@respx.mock
def test_404_raises_not_found_error(transport):
    respx.get("https://api.test/v1/ping").mock(
        return_value=httpx.Response(404, json={"message": "not found"})
    )
    with pytest.raises(NotFoundError) as exc_info:
        transport.request("GET", "/ping")
    assert exc_info.value.status_code == 404

@respx.mock
def test_429_raises_rate_limit_error(transport):
    respx.get("https://api.test/v1/ping").mock(
        return_value=httpx.Response(429, json={"message": "rate limit exceeded"})
    )
    with pytest.raises(RateLimitError) as exc_info:
        transport.request("GET", "/ping")
    assert exc_info.value.status_code == 429

@respx.mock
def test_500_raises_server_error(transport):
    respx.get("https://api.test/v1/ping").mock(
        return_value=httpx.Response(500, json={"message": "internal server error"})
    )
    with pytest.raises(ServerError) as exc_info:
        transport.request("GET", "/ping")
    assert exc_info.value.status_code == 500

@respx.mock
def test_204_returns_none(transport):
    respx.get("https://api.test/v1/ping").mock(
        return_value=httpx.Response(204)
    )
    assert transport.request("GET", "/ping") is None
