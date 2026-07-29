import httpx
import pytest
import respx

from bigchange._transport import Transport
from bigchange.exception import AuthError, NotFoundError, RateLimitError, ClientError, ServerError, TransportError, BigChangeError
from bigchange.api_resources.jobs import JobResource

class FakeAuth:
    def get_token(self) -> str:
        return "fake-token"
    def close(self) -> None:
        pass

@pytest.fixture
def jobs():
    transport = Transport(FakeAuth(), base_url="https://api.test", customer_id="test-customer", api_version="v1", timeout=5.0)
    return JobResource(transport)


@respx.mock
def test_get_job_returns_job(jobs):
    job_id = 12345
    job_payload = {
        "id": job_id,
        "reference": "JOB-12345",
        "status": "in_progress",
        "customerId": 67890,
        "assignedToId": 54321,
        # Add other fields as necessary
    }

    respx.get(f"https://api.test/v1/jobs/{job_id}").mock(
        return_value=httpx.Response(200, json=job_payload)
    )

    job = jobs.get_job(job_id)

    assert job.id == job_id
    assert job.reference == "JOB-12345"
    assert job.status == "in_progress"

@respx.mock
