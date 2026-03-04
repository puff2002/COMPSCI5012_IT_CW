# Backend/API Issues Log

This file tracks confirmed or suspected backend/API issues discovered during frontend planning and implementation.

## How to use this log

- Add one entry per issue.
- Keep status updated (`Open`, `In Progress`, `Blocked`, `Resolved`).
- Link related files/endpoints for fast follow-up.
- When resolved, keep the entry and add a short resolution note.

## Issue Template

```md
## BI-XXX: Short title
- Date: YYYY-MM-DD
- Status: Open | In Progress | Blocked | Resolved
- Severity: High | Medium | Low
- Area: API contract | Backend logic | Auth | Data model | Integrations | Docs
- Source: file/path or endpoint
- Description: ...
- Impact: ...
- Proposed mitigation: ...
- Owner: ...
- Resolution note: ... (optional)
```

## Open Issues

## BI-001: `recommend` endpoint has write side effects
- Date: 2026-03-04
- Status: Open
- Severity: Medium
- Area: API contract
- Source: `POST /api/outfits/recommend/`, `backend/outfits/views.py`
- Description: Calling recommendation creates both `Outfit` and `OutfitHistory`.
- Impact: Frontend can accidentally create duplicate history records if it also calls `POST /api/outfits/history/` after recommendation.
- Proposed mitigation: Document this as explicit endpoint behavior and treat returned `history` as canonical on frontend.
- Owner: TBD

## BI-002: Category semantics mismatch risk between strict enum and AI pipeline
- Date: 2026-03-04
- Status: Open
- Severity: High
- Area: Data model
- Source: `backend/wardrobe/models.py`, `backend/services/recommendation.py`, `spec/backend_api.md`
- Description: `ClothingItem.category` is restricted to `top|bottom|shoes`; AI-related recommendation code also contains logic with Chinese category labels (`上衣`, `裤子`), indicating a potential mismatch path.
- Impact: Incorrect category values can break filtering/grouping and reduce OOTD recommendation quality.
- Proposed mitigation: Normalize category values at service boundary and add tests asserting enum-compatible outputs for upload/analyze flows.
- Owner: TBD

## BI-003: Weather payload naming is mixed across response objects
- Date: 2026-03-04
- Status: Open
- Severity: Medium
- Area: API contract
- Source: `spec/backend_api.md`, `backend/outfits/serializers.py`
- Description: API responses include both camelCase fields (e.g., `feelsLike`) and snake_case fields (e.g., `weather_detail.feels_like`) in related payloads.
- Impact: Frontend mapping complexity increases and bugs are more likely if field names are assumed to be uniform.
- Proposed mitigation: Define and enforce field naming conventions per endpoint in API docs; map explicitly in frontend adapter layer.
- Owner: TBD

## BI-004: Backend/API contract synchronization process is not yet defined
- Date: 2026-03-04
- Status: Open
- Severity: Medium
- Area: Docs
- Source: `spec/backend_api.md`, linked backend workspace
- Description: API documentation is now local, but there is no explicit update workflow when backend endpoints/models change.
- Impact: Stale docs can cause frontend implementation drift and integration failures.
- Proposed mitigation: Add a release checklist item: update `spec/backend_api.md` and this file for every backend contract change.
- Owner: TBD
