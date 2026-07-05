# Logged-in User Profile Editing — Spec

**Status:** Draft
**Date:** 2026-07-05
**Related:** `docs/specs/partner-negotiations-spec.md` (established spec format + host/profile read-model prior art). Root `docs/HANDOFF.md` is deploy-focused and unrelated to this feature.

## Goal
Give a logged-in protector or foster user the ability to view and edit their own profile (org/name, description, phone, city, state) after registration. Today these fields are written once at registration and are never readable or editable again — there is no self-service profile screen and no update path anywhere in the stack.

## Context & Current State
- **Auth API is read-only for the user.** `auth_router.py` exposes only `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, and `GET /auth/me`. `me` returns just `id`, `email`, `role` (`app/adapters/inbound/api/auth_router.py:68`), never profile fields.
- **`AuthService` has no update path.** Only `register`, `login`, `get_current_user`, and token helpers (`app/application/auth_service.py:16`). No `user_service.py` exists.
- **Domain already models the full shape.** `ProtectorProfile` (`user_id`, `org_name`, `id`, `description`, `phone`, `city`, `state`) and `FosterProfile` (`user_id`, `full_name`, `phone`, `city`, `state`, `id`) at `app/domain/entities/user.py:19` and `:30`. A `Host` read-model (`app/domain/entities/user.py:40`) already normalizes protector/foster into a display shape — good prior art for a read-model approach here.
- **Repository can insert but not read/update profiles by user.** `UserRepository` port (`app/domain/ports/repositories.py:12`) has `save_protector_profile` / `save_foster_profile` (INSERT-only — they always construct a new model, `user_repository.py:47` and `:63`) and `find_hosts`, but **no** find-one-profile-by-user or update methods. `find_by_id` returns only the `User` (no profile fields — `_to_domain` at `user_repository.py:92` ignores the joined profiles).
- **Persistence constraints differ by role.** `ProtectorProfileModel` (`models.py:41`): only `org_name` NOT NULL; `description`, `phone`, `city`, `state` nullable. `FosterProfileModel` (`models.py:59`): `full_name`, `phone`, `city`, `state` all **NOT NULL**. Both have `user_id` UNIQUE (one profile per user).
- **Frontend has no profile page and no client-side profile data.** No `dashboard/profile` route exists (`src/app/dashboard/**` has cats/applications/donations/intents/partners only). `useAuth()` exposes `{ user, loading, login, register, logout }` and `user` (from `getMeApi()` → `/auth/me`) carries only `id`, `email`, `role` (`src/lib/auth/context.tsx:15`, `src/lib/api/auth.ts:31`).
- **The Navbar "Profile" link is a misnomer.** It routes to `/dashboard` (protector) or `/foster/applications` (foster) — a "go to my area" link, not a profile page (`src/components/ui/Navbar.tsx:60` and `:138`).
- **Correction to the brief:** a `/foster/` area **does** exist (`src/app/foster/applications/page.tsx`, `src/app/foster/apply/page.tsx`), but unlike protectors it has **no** shared nav shell (protectors get `DashboardNav`, `src/components/dashboard/DashboardNav.tsx:6`). So a foster profile page is reachable but must be linked from the Navbar, not a foster dashboard nav (there isn't one).
- **Prior art to mirror:**
  - Read-model normalizing both roles: `Host` + `find_hosts` (`user_repository.py:78`).
  - Owner-scoped mutation via `get_current_user`, `ValueError` → HTTP mapping: `partner_router.py` / `PartnerService.update_partner` (`partner_service.py:79`).
  - Per-domain router registration: `router.py:14`.
  - Frontend edit form pattern: `src/app/dashboard/donations/[id]/edit/page.tsx` (uncontrolled form, `defaultValue`, `FormData`, `saved` flag).
  - Per-domain API client: `src/lib/api/*.ts`.

## Proposed Design

### Service boundary — new `UserService` (not `AuthService`)
Profile read/update is a **profile-CRUD concern**, distinct from authentication (credential verification, token issuance, identity resolution). `AuthService` is cohesive around auth today; folding profile CRUD into it would blur that boundary and grow it toward a god-service. The codebase already favors one service per domain concept (`CatService`, `DonationService`, `PartnerService`). Therefore: **new `UserService`** depending on `UserRepository`, exposing `get_profile` and `update_profile`. It shares the same `UserRepository` as `AuthService` — no new repository.

### Normalized read-model — reuse the `Host` pattern
Rather than leak two divergent profile shapes to the router, add a `UserProfile` read-model (dataclass) that merges the current user's identity + role-appropriate profile fields into one shape. Both `get_profile` and `update_profile` return `UserProfile`, so the router maps 1:1 to a single `ProfileResponse`. This mirrors how `Host` already normalizes protector/foster.

```
UserProfile { email, role, org_name?, full_name?, description?, phone?, city?, state? }
```
For a protector, `full_name` is `None`; for a foster, `org_name` and `description` are `None`.

### Endpoints — self-scoped, no id in URL
Two endpoints on a new `user_router` (prefix `/users`), both guarded by `get_current_user` so the target is **always the caller** — no id in the path, no way to address another user:
- `GET /users/me/profile` → `ProfileResponse`
- `PATCH /users/me/profile` (partial) → `ProfileResponse`

We keep `GET /auth/me` unchanged (it is consumed by `useAuth`'s bootstrap and only needs identity). Profile data is fetched separately by the profile page. Rationale: avoid widening the hot auth-bootstrap payload and avoid a breaking change to the `User` client type.

### Partial update semantics
`PATCH` accepts any subset of `{ org_name, full_name, description, phone, city, state }`. `UserService.update_profile`:
1. Loads the caller's existing profile (by `user.id`, role-selected).
2. Applies only **provided** (non-`None`) fields that are valid for the role — protector ignores `full_name`; foster ignores `org_name`/`description`.
3. Enforces NOT-NULL invariants: a foster may not blank `full_name`/`phone`/`city`/`state`, and a protector may not blank `org_name` (raise `ValueError` → 400). Fields not provided are untouched.
4. Persists via a role-appropriate `update_*_profile` repo method and returns the refreshed `UserProfile`.

### Repository additions
`save_*_profile` are INSERT-only (registration). Add read + update methods:
- `find_protector_profile(user_id) -> ProtectorProfile | None`
- `find_foster_profile(user_id) -> FosterProfile | None`
- `update_protector_profile(profile) -> ProtectorProfile`
- `update_foster_profile(profile) -> FosterProfile`
Update methods fetch the existing model by `user_id`, assign fields, `flush`, and return the domain entity. (Do not reuse `save_*` — those always `add` a new row and would violate the `user_id` UNIQUE constraint.)

### Error handling
`UserService` raises `ValueError` for "profile not found" and invalid-blank violations; the router maps `ValueError` → `404`/`400`, mirroring `partner_router.py`. A missing profile for an authenticated user is a data-integrity edge (registration always creates one) — treat as 404.

## Scope
- **In scope:** `UserService` (get/update profile); `UserProfile` read-model; repo find/update methods; `/users/me/profile` GET+PATCH; DI + router wiring; frontend protector profile page (`/dashboard/profile`), foster profile page (`/foster/profile`), API client, types; Navbar "Profile" link retargeting + a `DashboardNav` item for protectors.
- **Out of scope (explicitly):** email change; password change (needs current-password confirmation + a larger security surface — deferred, see Open Questions); registering new profiles (unchanged); editing `is_active`/role; any migration (no schema change — all columns already exist); a foster dashboard nav shell (the foster profile page is reached via the Navbar link only).

## Interfaces / Models / Endpoints

### Domain (`app/domain/entities/user.py`)
```python
@dataclass
class UserProfile:
    email: str
    role: UserRole
    org_name: str | None = None
    full_name: str | None = None
    description: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
```

### Ports (`app/domain/ports/repositories.py`, `UserRepository`)
```python
async def find_protector_profile(self, user_id: UUID) -> ProtectorProfile | None: ...
async def find_foster_profile(self, user_id: UUID) -> FosterProfile | None: ...
async def update_protector_profile(self, profile: ProtectorProfile) -> ProtectorProfile: ...
async def update_foster_profile(self, profile: FosterProfile) -> FosterProfile: ...
```

### Service (`app/application/user_service.py`)
```python
class UserService:
    def __init__(self, user_repo: UserRepository) -> None: ...
    async def get_profile(self, user: User) -> UserProfile: ...
    async def update_profile(self, user: User, data: dict) -> UserProfile: ...
```

### Schemas (`app/adapters/inbound/api/schemas/user.py`)
```python
class ProfileResponse(BaseModel):
    email: str
    role: UserRole
    org_name: str | None = None
    full_name: str | None = None
    description: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    model_config = ConfigDict(from_attributes=True)

class ProfileUpdate(BaseModel):   # all optional (partial PATCH)
    org_name: str | None = None
    full_name: str | None = None
    description: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
```
`PATCH` router passes `body.model_dump(exclude_unset=True)` to the service so untouched fields stay untouched.

### Endpoints (all under `/api/v1`)
| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/users/me/profile` | current_user | Return caller's role-appropriate profile |
| PATCH | `/users/me/profile` | current_user | Update caller's profile fields (partial) |

### Frontend types (`src/lib/types/index.ts`)
```ts
export interface UserProfile {
  email: string;
  role: UserRole;
  org_name?: string | null;
  full_name?: string | null;
  description?: string | null;
  phone?: string | null;
  city?: string | null;
  state?: string | null;
}
```

## Impact Analysis
- **No migration.** All columns already exist; this is purely new read/update paths. `save_*_profile` unchanged.
- **DI change:** add `get_user_service` to `app/dependencies.py` (depends on `get_user_repository`). `AuthService` untouched.
- **Router registration:** add `user_router` to `app/adapters/inbound/api/router.py` (import + `include_router`).
- **Non-breaking:** `GET /auth/me`, `UserResponse`, and the client `User` type are unchanged; the profile screen fetches `/users/me/profile` on demand, so `useAuth` bootstrap is unaffected.
- **Foster NOT-NULL invariants:** the service must reject blanking `full_name`/`phone`/`city`/`state`; the DB would otherwise raise an integrity error. Protector `org_name` likewise.
- **Frontend nav consistency:** retarget the Navbar "Profile" link (desktop `Navbar.tsx:60`, mobile `:138`) to `/dashboard/profile` (protector) / `/foster/profile` (foster); add `['/dashboard/profile', 'Profile']` to `DashboardNav`.
- **Next.js caveat:** `rescute/AGENTS.md` warns this Next.js has non-standard APIs — the Implementer MUST read the relevant guide in `node_modules/next/dist/docs/` before touching any page/routing/`.tsx` file.
- **Tests:** service tests (get returns role-shaped profile; update applies provided fields; blanking a foster required field / protector `org_name` raises; role-irrelevant fields ignored); repo round-trip for find/update; router auth (401 unauthenticated) + 400 on invalid blank. No existing test suite was located — confirm tooling before writing; do not block units on it.

## Implementation Units
Dependency-ordered, ~50 LOC max each.

**Backend**
1. **`UserProfile` read-model** — files: `app/domain/entities/user.py` — add the `UserProfile` dataclass. Acceptance: imports resolve; instantiable with role-partial fields.
2. **Port methods** — files: `app/domain/ports/repositories.py` — add abstract `find_protector_profile`, `find_foster_profile`, `update_protector_profile`, `update_foster_profile` to `UserRepository`. Acceptance: ABC updated; `UserRepositoryImpl` must implement them next.
3. **Repo find methods** — files: `app/adapters/outbound/persistence/user_repository.py` — implement `find_protector_profile`, `find_foster_profile` (`select ... where user_id ==`, map model→domain). Acceptance: returns the profile for an existing user, `None` otherwise.
4. **Repo update methods** — files: `app/adapters/outbound/persistence/user_repository.py` — implement `update_protector_profile`, `update_foster_profile` (fetch model by `user_id`, assign fields, `flush`, return domain). Acceptance: mutating a field persists it; no duplicate row created.
5. **`UserService`** — files: `app/application/user_service.py` (new) — `get_profile(user)` (role-select find, build `UserProfile`); `update_profile(user, data)` (load, apply provided+valid fields, enforce NOT-NULL invariants, persist, return `UserProfile`). Acceptance: protector/foster each get correct shape; blanking a required field raises `ValueError`.
6. **Schemas** — files: `app/adapters/inbound/api/schemas/user.py` (new) — `ProfileResponse`, `ProfileUpdate`. Acceptance: models validate; `ProfileResponse` maps from `UserProfile` via `from_attributes`.
7. **DI wiring** — files: `app/dependencies.py` — add `get_user_service` depending on `get_user_repository`. Acceptance: app boots.
8. **Router** — files: `app/adapters/inbound/api/user_router.py` (new) + `app/adapters/inbound/api/router.py` — `APIRouter(prefix="/users", tags=["users"])`; `GET /users/me/profile`, `PATCH /users/me/profile` (both `Depends(get_current_user)`, `ValueError`→404/400); register in `router.py`. Acceptance: GET returns caller's profile; PATCH updates it; unauthenticated → 401.

**Frontend** (read `node_modules/next/dist/docs/` first)
9. **Types** — files: `src/lib/types/index.ts` — add `UserProfile`. Acceptance: `tsc` clean.
10. **API client** — files: `src/lib/api/users.ts` (new) — `getMyProfile(): Promise<UserProfile>` (`GET /users/me/profile`), `updateMyProfile(data): Promise<UserProfile>` (`PATCH /users/me/profile`). Acceptance: signatures match schemas.
11. **Protector profile page** — files: `src/app/dashboard/profile/page.tsx` (new) — `ProtectedRoute requiredRole="protector"`; fetch `getMyProfile`, render `DashboardNav`, an uncontrolled form (`defaultValue`) for `org_name`, `description`, `phone`, `city`, `state`; submit via `updateMyProfile`; `saved` flag. Mirror `dashboard/donations/[id]/edit/page.tsx`. Acceptance: pre-filled, saves, shows confirmation.
12. **Foster profile page** — files: `src/app/foster/profile/page.tsx` (new) — `ProtectedRoute requiredRole="foster"`; fetch `getMyProfile`, form for `full_name`, `phone`, `city`, `state` (all `required`); submit via `updateMyProfile`. Acceptance: pre-filled, saves, required fields cannot be blanked.
13. **Nav wiring** — files: `src/components/ui/Navbar.tsx` (desktop + mobile "Profile" links → `user.role === 'protector' ? '/dashboard/profile' : '/foster/profile'`) and `src/components/dashboard/DashboardNav.tsx` (add `['/dashboard/profile', 'Profile']`). Acceptance: Profile link lands on the new page; dashboard nav item renders/highlights.

## Open Questions
1. **Password/email change:** assumed **deferred**. Password change needs current-password confirmation and re-hashing (an `AuthService` concern, not profile CRUD); email change needs uniqueness re-check and likely re-verification. Both are a larger security surface than the fields requested. Confirm they stay out of this iteration.
2. **Foster required-field blanking:** assumed the service **rejects** attempts to blank `full_name`/`phone`/`city`/`state` (400) rather than silently ignoring them. Confirm reject-vs-ignore.
3. **Foster nav shell:** the foster profile page is reachable only via the Navbar "Profile" link (fosters have no `DashboardNav`). Assumed acceptable for this iteration; a dedicated foster nav shell is a separate feature. Confirm.
4. **`GET /auth/me` scope:** assumed **unchanged** (identity-only), with profile fetched separately. Confirm we should not instead enrich `/auth/me` + the client `User` type (which would be a broader, breaking change to `useAuth`).
