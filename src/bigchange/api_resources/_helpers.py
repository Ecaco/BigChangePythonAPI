

from dataclasses import dataclass, field

from bigchange.exception import BigChangeError


@dataclass 
class BulkResult: 
    success: list = field(default_factory=list)
    failed: dict[int | str , BigChangeError] = field(default_factory=dict)

    @property
    def all_successful(self) -> bool:
        return not self.failed
    


def iter_pages(transport, path, response_model, query_params=None, page_size=100):
    page = 1
    seen_first_ids = set()
    while True:
        params = dict(query_params or {})
        params["pageNumber"] = page
        params["pageSize"] = page_size

        data = transport.request("GET", path, params=params)
        response = response_model.model_validate(data)

        items = response.items
        if not items:
            break

        first_id = items[0].id
        if first_id in seen_first_ids:
            raise RuntimeError(f"Pagination is not advancing on {path} at page {page}.")
        seen_first_ids.add(first_id)

        yield items

        if response.page_item_count < page_size:
            break
        page += 1