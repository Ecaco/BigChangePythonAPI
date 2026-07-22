import httpx
import pytest
import respx

from bigchange._transport import Transport
from bigchange.api_resources.contacts import Contact, ContactsResource


class FakeAuth:
    def get_token(self) -> str:
        return "fake-token"
    def close(self) -> None:
        pass


CONTACT_PAYLOAD = {
    "id": 5514123,
    "createdAt": "2022-11-29T16:50:16.0000000+00:00",
    "modifiedAt": "2023-09-12T11:24:23.0000000+00:00",
    "reference": "5514123",
    "name": "Example Company",
    "groupId": 5514123,
    "parentId": None,
    "extraInformation": "Loyal customer for many years",
    "street": "3150 Century Way",
    "town": "Leeds",
    "postalCode": "LS15 6HU",
    "country": "England",
    "accountStatus": "normal",
    "stopReason": None,
    "stoppedAt": None,
    "customFields": [],
}


@pytest.fixture
def contacts():
    transport = Transport(FakeAuth(), base_url="https://api.test", customer_id="test-customer", api_version="v1", timeout=5.0)
    return ContactsResource(transport)


@respx.mock
def test_get_returns_typed_contact(contacts):
    respx.get("https://api.test/v1/contacts/5514123").mock(
        return_value=httpx.Response(200, json=CONTACT_PAYLOAD)
    )

    contact = contacts.get(5514123)

    assert isinstance(contact, Contact)
    assert contact.id == 5514123
    assert contact.postal_code == "LS15 6HU"         
    assert contact.created_at.year == 2022           
    assert contact.stopped_at is None


@respx.mock
def test_get_list_returns_typed_contact_list(contacts):
    respx.get("https://api.test/v1/contacts").mock(
        return_value=httpx.Response(200, json={"items": [CONTACT_PAYLOAD], "pageNumber": 1, "pageItemCount": 1})
    )

    contact_list = contacts.get_list_of_contacts()

    assert isinstance(contact_list, ContactsResource.ContactListResponse)
    assert len(contact_list.items) == 1
    assert isinstance(contact_list.items[0], Contact)
    assert contact_list.items[0].id == 5514123