# BigChange API — Analysis & Documentation Defects

Findings from porting this client against the live BigChange API (v1).
Recorded because none of this is derivable from their documentation — in
several cases the documentation is actively wrong.

Last updated: 2026-07-21

---

## Working rule

**BigChange's documentation is not a reliable source for response shapes or
preconditions. Real payloads are the only ground truth.**

Every model built purely from their docs should be treated as provisional
until validated against a live response.

---

## 1. Undocumented mandatory filters on `GET /jobs`

An unfiltered request is rejected:

```
422 {"title":"One or more validation errors occurred.","status":422,
     "errors":{"queryParams":["No filter or date range provided. At least one of
     the filters [Id, Reference] must be set, or at least one of the date ranges
     [(CreatedAtFrom and CreatedAtTo), (StartAtFrom and StartAtTo),
     (StatusModifiedAtFrom and StatusModifiedAtTo)] must be provided"]}}
```

The docs list **every** query parameter as optional. The requirement appears
nowhere except this error message.

### The docs and the error contradict each other

The docs list a `plannedAtFrom` / `plannedAtTo` pair. The 422 does **not**
name it as a sufficient date range. So `plannedAt` is a valid filter but
apparently does not on its own satisfy the requirement.

**Consequence:** do not re-encode the sufficiency rule client-side. Two of
BigChange's own sources disagree about it, so any client-side version is a
guess. Guard only the stable half ("at least one filter supplied") and let
the 422 own the rest.

---

## 2. Fields return `null` despite not being marked nullable

`GET /jobs` — these five are documented as plain `string` with no nullable
marker, and all returned `null` on live data:

- `reference`
- `internalComment`
- `resourcesComment`
- `contactComment`
- `officeNotes`

Note the failure shape: BigChange sends JSON `null`, **not** `""` and **not**
an omitted key.

**Consequence:** in Pydantic v2, `str | None` still means *required and
present*. Fields must be `str | None = None` to tolerate this. Assume any
documented-as-non-nullable string may in fact be null.

---

## 3. Wrong example payload on `GET /jobs/{jobId}/stock`

The "Get a list of job stocks" endpoint documents its response example as a
**Job** object — `typeId`, `typeName`, `contactAddress`, `contactLocation`,
`plannedDuration`, `customFields`, `siteContactIds`, `status: "new"`. Not one
stock-related field appears.

**Resolved** via the single-fetch endpoint (`GET /jobs/{jobId}/stock/{jobStockId}`),
which documents the real schema. `JobStock` is now modelled from that.

This demonstrates the silent-drop risk concretely: the provisional model
inferred from the list endpoint's query parameters had **6 fields**. The real
schema has **16**, including `quantityPlanned`, `quantityActual`, `make`,
`model`, `serialNumber` and a nested `worksheets` array. Pydantic would have
parsed every response successfully while discarding all ten missing fields.

**Working practice:** when a list endpoint's docs look wrong, check the
corresponding single-fetch endpoint — they are documented separately and the
single-item page has so far been the more reliable of the two.

---

## 4. Enum value sets: documented vs. observed

Only promote a field to `StrEnum` when the docs enumerate the **full** value
set. An undocumented value causes the entire response to fail validation.

| Field | Typed as | Reason |
|---|---|---|
| `Job.status` | `JobStatus` enum | All 16 values documented |
| `JobLineItem.lineItemType` | `LineItemType` enum | All 12 values documented |
| `JobConstraint.status` | `str` | Only `IsNotViolated` observed; set undocumented |
| `JobConstraint.type` | `str` | Only `JobMustCompleteBefore` observed; set undocumented |
| `JobStock.action` | `str` | Read and filter enums differ, and the read set has inconsistent casing — see below |

`JobStockActionFilter` exists as an enum for **building query filters**, where
the values are documented. It is deliberately not used to validate responses.

### `JobStockAction` — filter and read value sets are not the same

BigChange defines two separate enums with the same purpose:

- `JobStockActionFilter` (query param) — 7 values, no "unknown"
- `JobStockActionRead` (response field) — 8 values, adds an unknown/Unknown case

Worse, the read enum's docs are internally inconsistent about that extra
value's casing: the description bullet gives `unknown`, while the "Possible
values" list and the example both give `Unknown`.

`JobStock.action` is therefore typed `str`. Validating it against either
casing would reject half the possible responses. Both casings are covered by
tests.

---

## 5. Confirmed-good behaviour

Verified against live data, safe to rely on:

- **Pagination params** are `pageNumber` (1–2147483) and `pageSize` (1–1000)
  across endpoints. `iter_pages` in `_helpers.py` depends on these names.
- **Paged envelope** is `{items, pageNumber, pageSize, pageItemCount}`.
  Some models omit `pageSize`; Pydantic ignores it harmlessly.
- **Array filters cap at 50 items** (`id`, `reference`, `status`, `typeId`,
  `contactId`, `orderNumber`, `resourceId`, `vehicleId`). Fetching more than
  50 ids requires batching.
- **Timestamps** parse as tz-aware ISO 8601, both `...Z` and `...+00:00`.
- The contacts list endpoint returns the **full** contact shape, not a
  trimmed summary.

---

## 6. Untested surface

No data on the development account — these are built from docs alone and are
unverified against a real response:

- `JobLineItem` / `JobLineItemListResponse` (`/jobs/{id}/lineItems`)
- `JobStock` / `JobStockListResponse` (`/jobs/{id}/stock`) — schema now
  documented (§3), but never seen against a live response
- `JobActiveFlag` / `JobFlagHistory` (`/jobs/{id}/flags`)

`JobLineItem` deliberately marks everything optional except `id`,
`createdAt` and `lineItemType`, on the basis that a model which cannot be
tested should fail open rather than reject valid data.
