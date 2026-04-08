# Backend Gaps and Contract Warnings

Frontend-only adaptation notes (no backend changes applied):

1. Critical data integrity risk: `backend/src/data/users.json` contains unresolved merge markers in current branch snapshot, which can break backend startup/read operations.
2. Auth/session is global in-memory (`UserService._current_logged_in_user`) and not per-client token/session. The frontend treats it as a shared server session and surfaces auth errors.
3. Role is not returned by `UserResponse`; frontend infers role heuristically from username for route UX only. Backend remains source of truth for authorization.
4. Restaurant search endpoints effectively search by restaurant id string, not name/menu terms.
5. Restaurant owner order lookup appears to iterate restaurant storage inconsistently (`RestaurantRepo.read_all()` returns dict but service loops as list), which can produce runtime failures.
6. Ratings router permission check uses `RatingRepo` review record keyed by order id; ownership fields may be absent, so some review actions can reject valid requests.
7. No dedicated payment endpoint is exposed in router despite payment service existence; payment simulation is UI-level only.
8. Several order ops use query params (`reason`, `driver`) and may return validation errors for missing values; frontend preserves these contracts.

