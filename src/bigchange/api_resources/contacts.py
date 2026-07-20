from dataclasses import dataclass, field
from typing import List
from datetime import date, datetime
from bigchange.exception import BigChangeError
from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.type_adapter import TypeAdapter
from pydantic.alias_generators import to_camel


class Contact(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

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
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    items: list[dict]
    page_number: int
    page_item_count: int


#up to here. Broken. Need to fix this 
class ContactAccessHours(ContactListResponse):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ContactStopBody(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    applies_to: str
    status: str
    stop_reason: str



class ContactsResource:
    def __init__(self, transport) -> None:
        self._transport = transport

    def get_single_contact(self, contact_id: int) -> Contact:
        data = self._transport.request("GET", f"/contacts/{contact_id}")
        return Contact.model_validate(data)
    
    def get_list_of_contacts(self, query_params: dict | None = None) -> ContactListResponse:
        data = self._transport.request("GET", "/contacts", params=query_params)
        
        return ContactListResponse.model_validate(data)
    
    def iter_page(self, query_params: dict | None = None, page_size: int = 100):
        page = 1
        seen_first_ids: set[int] = set()
        while True:
            params = query_params.copy() if query_params else {}
            params["pageNumber"] = page
            params["pageSize"] = page_size
            response = self.get_list_of_contacts(params)
            items = response.items
            if not items:
                break
            first_id = items[0].id
            if first_id in seen_first_ids:
                raise RuntimeError(
                    f"Pagination is not advancing: page {page} returned the same "
                    f"records as an earlier page. The 'page'/'pageSize' query params "
                    f"may be wrong for this endpoint."
                )
            seen_first_ids.add(first_id)
            yield items
            if response.page_item_count < page_size:
                break
            page += 1

    def get_all_contacts(self, query_params: dict | None = None, page_size: int = 1000) -> List[Contact]:
        all_contacts = []
        for page_items in self.iter_page(query_params, page_size=page_size):
            all_contacts.extend(page_items)
        return all_contacts

    def update_contact(self, contact_id: int, update_data: dict) -> Contact:
        self._transport.request("PATCH", f"/contacts/{contact_id}", json=update_data)
        print(f"Updated contact {contact_id} with data: {update_data}")
    
    @dataclass
    class BulkUpdateResult:
        successful_updates: list[int] = field(default_factory=list)
        failed: dict[int, BigChangeError] = field(default_factory=dict)

        @property
        def all_successful(self) -> bool:
            return not self.failed
        
    
    # There isn't a native bulk update endpoint, so this is a custom implementation to loop and update each in bulk
    def bulk_update_contacts(self, updates: dict[int, dict], stop_on_failure: bool = False) -> BulkUpdateResult: # {contact_id: {field: value, ...}}
        result = self.BulkUpdateResult()
        results = []
        for contact_id, update_data in updates.items():
                try:
                    data = self._transport.request("PATCH", f"/contacts/{contact_id}", json=update_data)
                    result.successful_updates.append(contact_id)
                    results.append(data)
                except BigChangeError as e:
                    result.failed[contact_id] = e
                    if stop_on_failure:
                        break # Social housing
        return result
    
    def list_site_hours(self, contact_id: int, query_params: dict | None = None) -> List[dict]:
        response = self._transport.request("GET", f"/contacts/{contact_id}/accessHours", params=query_params)
        return ContactAccessHours.model_validate(response)

    def update_site_hours(self, contact_id: int, update_data: dict) -> List[dict]:
        self._transport.request("PUT", f"/contacts/{contact_id}/accessHours", json=update_data)
        print(f"Updated site hours for contact {contact_id} with data: {update_data}")
    
    def put_on_stop(self, contact_id: int, update_data: dict) -> ContactStopBody:
        self._transport.request("PUT", f"/contacts/{contact_id}/stop", json=update_data)
        print(f"Put contact {contact_id} on stop with data: {update_data}")

    def unstop_contact(self, contact_id: int, update_data: dict) -> ContactStopBody:
        self._transport.request("PUT", f"/contacts/{contact_id}/unstop", json=update_data)
        print(f"Unstopped contact {contact_id} with data: {update_data}")
