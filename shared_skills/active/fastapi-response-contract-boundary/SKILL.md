---
name: fastapi-response-contract-boundary
description: Audit and fix FastAPI/Pydantic response contract failures and analytics metric drift. Use when endpoints return ResponseValidationError/500, legacy JSON rows miss required response fields, response_model schemas need compatibility normalizers, or dashboard/trend/report APIs disagree on a canonical metric.
---

# FastAPI Response Contract Boundary

Use this skill to keep strict FastAPI response models without letting old or external data crash user-facing endpoints.

## Workflow

1. Reproduce with the real API first.
   - Create or identify a real row that triggers the endpoint.
   - Capture the HTTP status and backend traceback.
   - If test data is created, clean it through the public deletion path and verify database counts.

2. Check official docs before code edits.
   - FastAPI response model validation/filtering behavior.
   - Pydantic v2 model validation, field defaults, and validators.
   - SQLAlchemy/ORM serialization docs only when the fix touches ORM loading or mapped attributes.

3. Locate the contract boundary.
   - Input schema: rejects invalid new writes.
   - Stored data: may contain legacy or externally written JSON.
   - Service serializer: should normalize legacy stored data before FastAPI validates the response.
   - Response schema: should remain strict unless the product contract truly changed.

4. Do not "fix" by removing `response_model`.
   - A 500 from `ResponseValidationError` is a useful release gate.
   - Keep strict response models and make returned data conform to them.
   - Prefer one service-level normalizer over scattered endpoint patches.

5. Normalize legacy JSON deliberately.
   - Fill missing required response fields with explicit safe defaults such as `target_window`, `legacy_signal`, or `unknown`.
   - Drop or coerce invalid optional fields such as weights outside accepted ranges.
   - Preserve new-write validation so malformed new payloads are still rejected.
   - Add regression tests that validate the final dict with the response Pydantic model.

6. For analytics metrics, define one canonical source.
   - Identify the invariant, for example `net_balance == -life_hours_delta`.
   - Derive secondary totals from the canonical metric, not from a competing raw sum.
   - Keep explanatory category fields separate from canonical totals when schemas have legacy display fields.
   - Test cross-endpoint identity, not only each endpoint shape.

## Regression Tests

- Unit test the serializer/normalizer with malformed legacy JSON.
- Validate the serialized output through the actual response model.
- Unit test metric helper invariants with same-direction and opposite-direction raw totals.
- Run the backend tests from the project test root, not a repository root that collects scratch scripts.
- Rebuild the Docker service if production runs in Docker.
- Run a real API smoke that covers the failing endpoint, adjacent frontend contract endpoints, and account deletion cleanup.

## Completion Standard

- Original failure is reproduced and then passes.
- Strict response models remain enabled.
- Legacy bad data no longer causes endpoint 500.
- New malformed writes are still rejected or normalized at the documented input boundary.
- Cross-endpoint metric identities hold in real API output.
- Test data is deleted and verified from user-owned tables.
