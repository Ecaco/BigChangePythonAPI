from datetime import datetime
from enum import StrEnum
from ._helpers import iter_pages

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class JobType(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    name: str
    description: str | None
    planned_duration: int | None # In minutes
    category_id : int | None
    is_archived: bool | None
    is_order_number_required: bool | None
    is_tasks_enabled: bool | None
    positive_results : list[str] | None
    negative_results : list[str] | None
    custom_fields: list[dict] = Field(default_factory=list)

class JobTypeListResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    items: list[JobType]
    page_number: int
    page_size: int
    page_item_count: int

class JobTypeResource:
    def __init__(self, transport):
        self._transport = transport

    def get_job_types(self, query_params=None, page_size=100):
        return list(iter_pages(self._transport, "/jobTypes", JobTypeListResponse, query_params=query_params, page_size=page_size))


    def get_job_type(self, job_type_id: int) -> JobType:
        data = self._transport.request("GET", f"/jobTypes/{job_type_id}")
        return JobType.model_validate(data)
