# Test Checklist

Methods needing mocked (`respx`) test coverage.

Run: `pytest tests/ --ignore=tests/live_test_get.py --ignore=tests/auth_test.py -q`

---

## _transport.py

- [x] 200 returns parsed JSON
- [x] 401 raises AuthError
- [x] 404 raises NotFoundError
- [x] 429 raises RateLimitError
- [x] 500 raises ServerError
- [x] 204 returns None
- [ ] 429 then 200 -> retries and succeeds
- [ ] `Retry-After` header honoured over computed backoff
- [ ] 503 then 200 -> retries and succeeds
- [ ] retries exhausted -> raises last error
- [ ] POST (non-idempotent) is NOT retried
- [ ] `httpx.ConnectError` -> NetworkError
- [ ] 201 with empty body -> None
- [ ] `max_attempts=0` -> ValueError

## _helpers.py

- [ ] `iter_pages` — single page
- [ ] `iter_pages` — multiple pages, correct `pageNumber` per request
- [ ] `iter_pages` — stops when `pageItemCount < page_size`
- [ ] `iter_pages` — empty first page
- [ ] `iter_pages` — raises RuntimeError when pagination doesn't advance
- [ ] `BulkResult.all_successful`

---

## contacts.py

- [ ] `get_single_contact`
- [ ] `get_contacts_page`  *(existing test references old name `get_list_of_contacts` — currently failing)*
- [ ] `get_all_contacts`
- [ ] `update_contact`
- [ ] `bulk_update_contacts`
- [ ] `bulk_update_contacts` — partial failure populates `failed`
- [ ] `bulk_update_contacts` — `stop_on_failure=True` halts
- [ ] `list_site_hours`
- [ ] `update_site_hours`
- [ ] `put_on_stop`
- [ ] `unstop_contact`
- [ ] `create_contact`
- [ ] `bulk_create_contacts`
- [ ] `bulk_create_contacts` — failure keyed by `reference`

## job_types.py

- [ ] `get_job_types`
- [ ] `get_job_type`

---

## jobs.py — reads

- [ ] `get_job`
- [ ] `get_jobs_page`
- [ ] `get_all_jobs`
- [ ] `get_job_constraints`
- [ ] `get_active_flag`
- [ ] `get_flag_history`
- [ ] `get_job_line_items`
- [ ] `get_job_line_item`
- [ ] `get_job_stocks`
- [ ] `get_job_stock`
- [ ] `get_jobStatus_history`
- [ ] `get_job_worksheet`
- [ ] `get_job_worksheets`
- [ ] `get_all_job_worksheets`

## jobs.py — writes

Assert the **outbound request body** (`route.calls.last.request.content`), not just the return value.

- [ ] `post_job_flag`
- [ ] `create_job`
- [ ] `create_job_constraint`
- [ ] `create_job_flag`
- [ ] `create_job_line_item`
- [ ] `create_job_stock`
- [ ] `update_job`
- [ ] `update_job_line_item`
- [ ] `cancel_job`
- [ ] `set_job_result`
- [ ] `schedule_job`
- [ ] `start_job`
- [ ] `set_worksheet_answers`
- [ ] `set_worksheet_answers` — partial failure populates `failed`

---

## Model validation

- [ ] `JobResultBody` — `result` required when status is `completedOk`
- [ ] `JobResultEnum` — rejects `started`
- [ ] `JobPostBody` / `JobUpdateBody` — malformed UUID rejected
- [ ] `JobLineItemPostBody` — negative `unit_cost` rejected
- [ ] `JobStockPostBody` — rejects `broughtToSwap`
- [ ] `JobLineItemUpdateBody` — omitted field absent from payload
- [ ] `JobLineItemUpdateBody` — explicit `None` sends `null`
- [ ] Worksheet answer union — each variant serialises to its own shape
