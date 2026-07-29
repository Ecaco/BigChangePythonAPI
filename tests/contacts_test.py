import json

import httpx
import pytest
import respx

from bigchange._transport import Transport
from bigchange.api_resources.contacts import (
    Contact,
    ContactAccessFields,
    ContactAccessHours,
    ContactListResponse,
    ContactsResource,
)


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
    transport = Transport(
        FakeAuth(),
        base_url="https://api.test",
        customer_id="test-customer",
        api_version="v1",
        timeout=5.0,
        sleep=lambda _seconds: None,  # never really sleep on a retry
    )
    return ContactsResource(transport)


# --- reads ----------------------------------------------------------------

@respx.mock
def test_get_single_contact(contacts):
    respx.get("https://api.test/v1/contacts/5514123").mock(
        return_value=httpx.Response(200, json=CONTACT_PAYLOAD)
    )

    contact = contacts.get_single_contact(5514123)

    assert isinstance(contact, Contact)
    assert contact.id == 5514123
    assert contact.postal_code == "LS15 6HU"
    assert contact.created_at.year == 2022
    assert contact.stopped_at is None


@respx.mock
def test_get_contacts_page(contacts):
    respx.get("https://api.test/v1/contacts").mock(
        return_value=httpx.Response(
            200, json={"items": [CONTACT_PAYLOAD], "pageNumber": 1, "pageItemCount": 1}
        )
    )

    page = contacts.get_contacts_page()

    assert isinstance(page, ContactListResponse)
    assert len(page.items) == 1
    assert isinstance(page.items[0], Contact)
    assert page.items[0].id == 5514123


@respx.mock
def test_list_site_hours(contacts):
    respx.get("https://api.test/v1/contacts/5514123/accessHours").mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [{"dayOfWeek": "monday", "start": "09:00", "stop": "17:00"}],
                "pageNumber": 1,
                "pageItemCount": 1,
            },
        )
    )

    hours = contacts.list_site_hours(5514123)

    assert isinstance(hours, ContactAccessHours)
    assert len(hours.items) == 1
    assert isinstance(hours.items[0], ContactAccessFields)
    assert hours.items[0].day_of_week == "monday"
    assert hours.items[0].start == "09:00"


@respx.mock
def test_get_all_contacts_paginates(contacts):
    # Two full pages then a short page => three requests, generator stops on the short one.
    def make_contact(i):
        return {**CONTACT_PAYLOAD, "id": i}

    page1 = {"items": [make_contact(1), make_contact(2)], "pageNumber": 1, "pageItemCount": 2}
    page2 = {"items": [make_contact(3)], "pageNumber": 2, "pageItemCount": 1}

    route = respx.get("https://api.test/v1/contacts").mock(
        side_effect=[
            httpx.Response(200, json=page1),
            httpx.Response(200, json=page2),
        ]
    )

    all_contacts = contacts.get_all_contacts(page_size=2)

    assert [c.id for c in all_contacts] == [1, 2, 3]
    assert route.call_count == 2
    # page number advanced on the second request
    assert route.calls[1].request.url.params["pageNumber"] == "2"


# --- single writes --------------------------------------------------------

@respx.mock
def test_update_contact_sends_patch(contacts):
    route = respx.patch("https://api.test/v1/contacts/5514123").mock(
        return_value=httpx.Response(200, json={})
    )

    result = contacts.update_contact(5514123, {"town": "Sheffield"})

    assert result is None
    assert route.calls.last.request.method == "PATCH"
    assert json.loads(route.calls.last.request.content) == {"town": "Sheffield"}


@respx.mock
def test_put_on_stop_sends_put(contacts):
    route = respx.put("https://api.test/v1/contacts/5514123/stop").mock(
        return_value=httpx.Response(204)
    )

    contacts.put_on_stop(5514123, {"appliesTo": "contactOnly", "status": "contactOnStop"})

    assert route.calls.last.request.method == "PUT"
    assert json.loads(route.calls.last.request.content)["appliesTo"] == "contactOnly"


@respx.mock
def test_unstop_contact_sends_put(contacts):
    route = respx.put("https://api.test/v1/contacts/5514123/unstop").mock(
        return_value=httpx.Response(204)
    )

    contacts.unstop_contact(5514123, {"appliesTo": "contactOnly"})

    assert route.calls.last.request.method == "PUT"


@respx.mock
def test_update_site_hours_sends_put(contacts):
    route = respx.put("https://api.test/v1/contacts/5514123/accessHours").mock(
        return_value=httpx.Response(204)
    )

    contacts.update_site_hours(5514123, [{"dayOfWeek": "Monday", "start": "09:00", "stop": "17:00"}])

    assert route.calls.last.request.method == "PUT"
    assert json.loads(route.calls.last.request.content)[0]["dayOfWeek"] == "Monday"


@respx.mock
def test_create_contact_returns_typed_contact(contacts):
    route = respx.post("https://api.test/v1/contacts").mock(
        return_value=httpx.Response(201, json=CONTACT_PAYLOAD)
    )

    contact = contacts.create_contact({"name": "Example Company", "groupId": 5514123})

    assert isinstance(contact, Contact)
    assert contact.id == 5514123
    assert route.calls.last.request.method == "POST"


# --- bulk writes ----------------------------------------------------------

@respx.mock
def test_bulk_update_all_succeed(contacts):
    respx.patch("https://api.test/v1/contacts/1").mock(return_value=httpx.Response(200, json={}))
    respx.patch("https://api.test/v1/contacts/2").mock(return_value=httpx.Response(200, json={}))

    result = contacts.bulk_update_contacts({1: {"town": "A"}, 2: {"town": "B"}})

    assert result.all_successful
    assert result.success == [1, 2]
    assert result.failed == {}


@respx.mock
def test_bulk_update_partial_failure(contacts):
    respx.patch("https://api.test/v1/contacts/1").mock(return_value=httpx.Response(200, json={}))
    respx.patch("https://api.test/v1/contacts/2").mock(
        return_value=httpx.Response(400, json={"message": "bad request"})
    )

    result = contacts.bulk_update_contacts({1: {"town": "A"}, 2: {"town": "B"}})

    assert not result.all_successful
    assert result.success == [1]
    assert 2 in result.failed


@respx.mock
def test_bulk_update_stop_on_failure(contacts):
    respx.patch("https://api.test/v1/contacts/1").mock(
        return_value=httpx.Response(400, json={"message": "bad request"})
    )
    patch2 = respx.patch("https://api.test/v1/contacts/2").mock(
        return_value=httpx.Response(200, json={})
    )

    result = contacts.bulk_update_contacts(
        {1: {"town": "A"}, 2: {"town": "B"}}, stop_on_failure=True
    )

    assert result.success == []
    assert 1 in result.failed
    assert not patch2.called  # loop broke before reaching contact 2


@respx.mock
def test_bulk_create_failure_keyed_by_reference(contacts):
    respx.post("https://api.test/v1/contacts").mock(
        return_value=httpx.Response(400, json={"message": "bad request"})
    )

    result = contacts.bulk_create_contacts([{"reference": "REF-1", "name": "X"}])

    assert not result.all_successful
    assert "REF-1" in result.failed
