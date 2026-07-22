from datetime import datetime
from enum import StrEnum
from ._helpers import iter_pages

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class JobStatus(StrEnum):
    NEW = "new"
    SCHEDULED = "scheduled"
    UNSCHEDULED = "unscheduled"
    SENT = "sent"
    READ = "read"
    ACCEPTED = "accepted"
    REFUSED = "refused"
    ON_THE_WAY = "onTheWay"
    STARTED = "started"
    SUSPENDED = "suspended"
    COMPLETED_OK = "completedOk"
    COMPLETED_WITH_ISSUES = "completedWithIssues"
    CANCELLED = "cancelled"
    LATE_START = "lateStart"
    LATE_FINISH = "lateFinish"
    RESCHEDULED = "rescheduled"


class GeoLocation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    latitude: float
    longitude: float


class Job(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    uid: str | None = None
    type_id: int
    type_name: str
    contact_id: int
    contact_name: str
    contact_address: str
    contact_location: GeoLocation | None = None
    status: JobStatus
    status_modified_at: datetime | None = None
    planned_duration: int
    due_at: datetime | None = None
    reference: str | None = None
    description: str
    created_at: datetime
    order_number: str | None = None
    person_id: str | None = None
    person_name: str | None = None
    is_confirmed: bool
    category_id: int | None = None
    category_name: str | None = None
    resource_id: int | None = None
    resource_name: str | None = None
    vehicle_id: int | None = None
    vehicle_registration: str | None = None
    planned_start_at: datetime | None = None
    planned_end_at: datetime | None = None
    actual_start_at: datetime | None = None
    actual_end_at: datetime | None = None
    actual_duration: int | None = None
    internal_comment: str | None = None
    resources_comment: str | None = None
    contact_comment: str | None = None
    result: str | None = None
    job_group_id: int | None = None
    is_financially_complete: bool
    is_actioned: bool
    office_notes: str | None = None
    contract_id: int | None = None
    recurrence_id: int | None = None
    custom_fields: list[dict] = Field(default_factory=list)
    site_contact_ids: list[int] = Field(default_factory=list)

class JobListResponse(BaseModel):
    model_config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    )

    items: list[Job]
    page_number: int
    page_item_count: int


class JobConstraint(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    created_at: datetime
    status: str
    type: str
    constraint_at: datetime | None = None
    entity_id: int | None = None
    entity_name: str | None = None


class JobConstraintListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[JobConstraint]
    page_number: int
    page_item_count: int

class JobActiveFlag(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    history_id: int
    flag_id: int
    flag_name: str
    job_id: int
    applied_at: datetime
    owner_name: str
    comment: str | None = None

class JobFlagHistory(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[JobActiveFlag]
    page_number: int
    page_size: int
    page_item_count: int

class LineItemType(StrEnum):
    FREE_TEXT = "freeText"
    PREDEFINED = "predefined"
    STOCK_ITEM = "stockItem"
    WORKSHEET = "worksheet"
    DRIVING_PLANNED = "drivingPlanned"
    DRIVING_ACTUAL = "drivingActual"
    WORK_PLANNED = "workPlanned"
    WORK_ACTUAL = "workActual"
    EXPENSE = "expense"
    INVOICE = "invoice"
    STOCK = "stock"
    RATING_TABLE = "ratingTable"


class JobLineItem(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    job_id: int | None = None
    job_group_id: int | None = None
    contact_id: int | None = None
    created_at: datetime
    line_item_type: LineItemType
    quantity: float | None = None
    description: str | None = None
    tax_id: int | None = None
    tax_percentage: float | None = None
    unit_cost: float | None = None
    unit_selling_price: float | None = None
    tax_amount: float | None = None
    gross_amount: float | None = None
    nominal_code_id: int | None = None
    department_code_id: int | None = None


class JobLineItemListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[JobLineItem]
    page_number: int
    page_size: int
    page_item_count: int


class JobStatusItem(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    status: JobStatus
    created_at: datetime
    comment: str | None = None

class JobStatusHistory(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[JobStatusItem]
    page_number: int
    page_size: int
    page_item_count: int


class JobStockActionFilter(StrEnum):
    NO_MOVEMENT = "noMovement"
    BROUGHT_AND_LEFT = "broughtAndLeft"
    BROUGHT_AND_TAKEN_BACK = "broughtAndTakenBack"
    BROUGHT_TO_SWAP = "broughtToSwap"
    ON_SITE_AND_TAKEN_BACK = "onSiteAndTakenBack"
    ON_SITE_AND_LEFT = "onSiteAndLeft"
    USED_IN_STOCK = "usedInStock"


class JobStockWorksheet(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    worksheet_id: int
    worksheet_answers_entity_id: int


class JobStock(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    job_id: int
    stock_details_id: int | None = None
    stock_item_id: int | None = None
    action: str | None = None
    quantity_planned: float | None = None
    pickup_contact_id: int | None = None
    drop_off_contact_id: int | None = None
    is_delivered_to_be_sold: bool | None = None
    is_equipment_at_drop_off: bool | None = None
    quantity_actual: float | None = None
    make: str | None = None
    model: str | None = None
    serial_number: str | None = None
    drop_off_stock_item_id: int | None = None
    worksheets: list[JobStockWorksheet] = Field(default_factory=list)


class JobStockListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[JobStock]
    page_number: int
    page_size: int
    page_item_count: int


class JobWorksheetLink(StrEnum):
    LINKEDTOJOB = "linkedToJob"
    BRANCHEDFROMWORKSHEET = "branchedFromWorksheetQuestion"


class JobWorksheet(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    link_type: JobWorksheetLink

class JobWorksheetListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[JobWorksheet]
    page_number: int
    page_size: int
    page_item_count: int


class JobFlagPostBody(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    flag_id: int
    owner: str
    comment: str | None

class JobPostBody(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    type_id: int
    contact_id: int
    planned_duration: int | None = None
    reference: str | None = None
    description: str | None = None
    person_id: str | None = None
    order_number: str | None = None
    job_group_id: int | None = None
    category_id: int | None = None
    custom_fields: list[dict] = Field(default_factory=list)
    site_contact_id: int | None = None


class JobResource:
    def __init__(self, transport):
        self._transport = transport



    def get_job(self, job_id: int) -> Job:
        response = self._transport.request("GET", f"/jobs/{job_id}")
        return Job.model_validate(response)
    
    def get_jobs_page(self, query_params: dict | None = None, page_size: int = 1000) -> list[Job]:
        """Fetches a single page of jobs based on the provided query parameters.
        
        NOTE: This endpoint requires atleast one filter. An infiltered request will return
        a 422. This is enforced server side and is not stated in the documentation.
        You must supply atleast one of the following:
        - id (list, max of 50)
        - reference (list, max of 50)
        a complete date range both ends set:
        - createdAtFrom and createdAtTo
        - startedAtFrom and startedAtTo
        - statusModifiedAtFrom and statusModifiedAtTo

        Other filters can be combined but are actually optional. 
        """
        response = self._transport.request("GET", "/jobs", params=query_params)
        jobs_data = response.get("items", [])
        return [Job.model_validate(job) for job in jobs_data]
    
    def get_all_jobs(self, query_params: dict | None = None, page_size: int = 1000) -> list[Job]:
        """Fetches a single page of jobs based on the provided query parameters.
        
        NOTE: This endpoint requires atleast one filter. An infiltered request will return
        a 422. This is enforced server side and is not stated in the documentation.
        You must supply atleast one of the following:
        - id (list, max of 50)
        - reference (list, max of 50)
        a complete date range both ends set:
        - createdAtFrom and createdAtTo
        - startedAtFrom and startedAtTo
        - statusModifiedAtFrom and statusModifiedAtTo

        Other filters can be combined but are actually optional. 
        """
        jobs = []
        for page_items in iter_pages(
            self._transport, "/jobs", JobListResponse, query_params, page_size
        ):
            jobs.extend(page_items)
            print(f"Retrieved {len(page_items)} jobs from page {page_items[0].id if page_items else 'N/A'}")
        return jobs
    
    def get_job_constraints(self, job_id: int) -> JobConstraintListResponse:
        """Fetches the constraints for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/constraints")
        return JobConstraintListResponse.model_validate(response)
    
    def get_active_flag(self, job_id: int) -> JobActiveFlag:
        """Fetches the active flag for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/flags")
        return JobActiveFlag.model_validate(response)

    def get_flag_history(self, job_id: int) -> JobFlagHistory:
        """Fetches the flag history for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/flags/history")
        return JobFlagHistory.model_validate(response)

    def get_job_line_items(self, job_id: int, query_params: dict | None = None) -> JobLineItemListResponse:
        """Fetches a page of line items for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/lineItems", params=query_params)
        return JobLineItemListResponse.model_validate(response)

    def get_job_line_item(self, job_id: int, line_item_id: int) -> JobLineItem:
        """Fetches a single line item for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/lineItems/{line_item_id}")
        return JobLineItem.model_validate(response)

    def get_job_stocks(self, job_id: int, query_params: dict | None = None) -> JobStockListResponse:
        """Fetches a page of stock records for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/stock", params=query_params)
        return JobStockListResponse.model_validate(response)

    def get_job_stock(self, job_id: int, job_stock_id: int) -> JobStock:
        """Fetches a single stock record for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/stock/{job_stock_id}")
        return JobStock.model_validate(response)

    def get_jobStatus_history(self, job_id: int) -> JobStatusHistory:
        """Fetches the status history for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/status/history")
        return JobStatusHistory.model_validate(response)

    def get_job_worksheet(self, job_id: int, worksheet_id: int) -> JobWorksheet:
        """Fetches a single worksheet for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/worksheets/{worksheet_id}")
        return JobWorksheet.model_validate(response)

    def get_job_worksheets(self, job_id: int, query_params: dict | None = None) -> JobWorksheetListResponse:
        """Fetches a page of worksheets for a specific job."""
        response = self._transport.request("GET", f"/jobs/{job_id}/worksheets", params=query_params)
        return JobWorksheetListResponse.model_validate(response)

    def get_all_job_worksheets(self, job_id: int, query_params: dict | None = None, page_size: int = 1000) -> list[JobWorksheet]:
        """Fetches all worksheets for a specific job."""
        worksheets = []
        for page_items in iter_pages(
            self._transport, f"/jobs/{job_id}/worksheets", JobWorksheetListResponse, query_params, page_size
        ):
            worksheets.extend(page_items)
        return worksheets


    ############## POSTS    

    def post_job_flag(self, group_id: int, flag_data: JobFlagPostBody | dict) -> None:
        """
        Posts a flag for a specific job group.
        I think this technically falls under JobGroups,
        but this is how the docs have it, so I am following the docs.
        """
        body = JobFlagPostBody.model_validate(flag_data)
        self._transport.request(
            "POST",
            f"/jobGroups/{group_id}/jobFlags",
            json=body.model_dump(by_alias=True, exclude_unset=True),
        )

    def create_job(self, job_data: JobPostBody | dict) -> Job:
        """
        Creates a new job.
        """
        body = JobPostBody.model_validate(job_data)
        response = self._transport.request(
            "POST",
            "/jobs",
            json=body.model_dump(by_alias=True, exclude_unset=True),
        )
        return Job.model_validate(response)

    

    

    

    

    

    

