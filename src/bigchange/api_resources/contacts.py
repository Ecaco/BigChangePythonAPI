from dataclasses import dataclass, field
from typing import List
from datetime import date, datetime
from bigchange.exception import BigChangeError
from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.type_adapter import TypeAdapter
from pydantic.alias_generators import to_camel
from logging import getLogger
from ._helpers import iter_pages
from ._helpers import BulkResult

logger = getLogger(__name__)
CFG = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class Contact(BaseModel):
    model_config = CFG

    id: int
    created_at: datetime
    modified_at: datetime
    reference: str | None
    name: str
    group_id: int
    parent_id: int | None
    extra_information: str | None
    street: str | None
    town: str | None
    country: str | None
    postal_code: str | None
    country: str | None
    account_status: str         
    stop_reason: str | None
    stopped_at: date | None
    custom_fields: list[dict] = Field(default_factory=list)
    page_size: int | None = None

class ContactListResponse(BaseModel):
    model_config = CFG

    items: list[Contact]
    page_number: int
    page_item_count: int

class ContactAccessFields(BaseModel):
    model_config = CFG

    day_of_week: str
    start: str
    stop: str


class ContactAccessHours(BaseModel):
    model_config = CFG

    items: list[ContactAccessFields]
    page_number: int
    page_item_count: int


class ContactStopBody(BaseModel):
    model_config = CFG

    applies_to: str
    status: str
    stop_reason: str



class ContactsResource:
    def __init__(self, transport) -> None:
        self._transport = transport

    def get_single_contact(self, contact_id: int) -> Contact:
        data = self._transport.request("GET", f"/contacts/{contact_id}")
        return Contact.model_validate(data)
    
    def get_contacts_page(self, query_params: dict | None = None) -> ContactListResponse:
        data = self._transport.request("GET", "/contacts", params=query_params)
        
        return ContactListResponse.model_validate(data)


    def get_all_contacts(self, query_params=None, page_size=1000) -> list[Contact]:
        contacts = []
        for page_items in iter_pages(
            self._transport, "/contacts", ContactListResponse, query_params, page_size
        ):
            contacts.extend(page_items)
        return contacts


    def update_contact(self, contact_id: int, update_data: dict) -> None:
        self._transport.request("PATCH", f"/contacts/{contact_id}", json=update_data)
        logger.info(f"Updated contact {contact_id} with data: {update_data}")
    
        
    
    # There isn't a native bulk update endpoint, so this is a custom implementation to loop and update each in bulk
    def bulk_update_contacts(self, updates: dict[int, dict], stop_on_failure: bool = False) -> BulkResult: # {contact_id: {field: value, ...}}
        result = BulkResult()
        for contact_id, update_data in updates.items():
                try:
                    data = self._transport.request("PATCH", f"/contacts/{contact_id}", json=update_data)
                    result.success.append(contact_id)
                except BigChangeError as e:
                    result.failed[contact_id] = e
                    if stop_on_failure:
                        break # Social housing
        return result
    
    def list_site_hours(self, contact_id: int, query_params: dict | None = None) -> List[dict]:
        response = self._transport.request("GET", f"/contacts/{contact_id}/accessHours", params=query_params)
        return ContactAccessHours.model_validate(response)

    def update_site_hours(self, contact_id: int, update_data: dict) -> None:
        self._transport.request("PUT", f"/contacts/{contact_id}/accessHours", json=update_data)
        logger.info(f"Updated site hours for contact {contact_id} with data: {update_data}")
    
    def put_on_stop(self, contact_id: int, update_data: dict) -> None:
        self._transport.request("PUT", f"/contacts/{contact_id}/stop", json=update_data)
        logger.info(f"Put contact {contact_id} on stop with data: {update_data}")

    def unstop_contact(self, contact_id: int, update_data: dict) -> None:
        self._transport.request("PUT", f"/contacts/{contact_id}/unstop", json=update_data)
        logger.info(f"Unstopped contact {contact_id} with data: {update_data}")

    def create_contact(self, contact_data: dict) -> Contact:
        response = self._transport.request("POST", "/contacts", json=contact_data)
        logger.info(f"Created new contact with data: {contact_data}")
        return Contact.model_validate(response)
    
    def bulk_create_contacts(self, contacts_data: list[dict], stop_on_failure: bool = False) -> BulkResult:
        result = BulkResult()
        for contact_data in contacts_data:
            try:
                response = self._transport.request("POST", "/contacts", json=contact_data)
                contact_id = response.get("id")
                if contact_id is not None:
                    result.success.append(contact_id)
                else:
                    raise BigChangeError("No contact ID returned in response.")
            except BigChangeError as e:
                result.failed[contact_data.get("reference", "unknown")] = e
                if stop_on_failure:
                    break
        return result
