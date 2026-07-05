# Partner Negotiations (Purrtner Onboarding) — Spec

**Status:** Draft
**Date:** 2026-07-05
**Related:** First spec in this repo (no prior `docs/specs/`, no `docs/HANDOFF.md`). Establishes the spec format for the project.

## Goal
Turn "purrtners" from a standalone, read-only catalog into an owned, negotiated relationship: a prospective business picks a protector or foster home, proposes a deal (a message + a monetary amount to "host" its coupon), and that host reviews the request and accepts/rejects/counters. Only an accepted negotiation makes the partner publicly listed, and it is owned by the accepting host — which unlocks edit/delete rights that do not exist today.

## Context & Current State
- `PartnerModel` (`app/adapters/outbound/persistence/models.py:200`) has business + coupon fields only; no owner, no status, no relationships.
- `Partner` domain entity (`app/domain/entities/partner.py:5`) mirrors the model; `PartnerRepository` port (`app/domain/ports/repositories.py:73`) exposes only `save`, `find_all`, `find_by_location`.
- `PartnerRepositoryImpl.find_all` (`app/adapters/outbound/persistence/partner_repository.py:20`) filters `is_active == True`.
- `PartnerService` (`app/application/partner_service.py:4`) only has `.list()`.
- `partner_router.py` (`app/adapters/inbound/api/partner_router.py:6`) wires only `GET /partners`. The frontend `createPartner` (`rescute/src/lib/api/partners.ts:4`) POSTs to `/partners` but no such route exists — dead code.
- Frontend `PartnerForm` (`rescute/src/components/partners/PartnerForm.tsx`) collects only business/coupon info; `/partners/register` (`rescute/src/app/partners/register/page.tsx`) renders it. `/partners` page (`rescute/src/app/partners/page.tsx`) lists via `PartnerCard` with no edit/delete UI.
- Users have `protector` and `foster` roles (`app/domain/value_objects.py:5`). There is **no** "partner/business" user account, and registration today is unauthenticated. Profiles: `ProtectorProfileModel` (`org_name`, city, state, `models.py:41`), `FosterProfileModel` (`full_name`, phone, city, state, `models.py:59`).
- Prior art to mirror:
  - Ownership + owner-scoped mutation: `DonationService.update` checks `post.protector_id != protector_id` (`app/application/donation_service.py:28`).
  - Host-facing review of incoming records: `GET /donations/intents` (`app/adapters/inbound/api/donation_router.py:88`) + `/dashboard/intents` page (`rescute/src/app/dashboard/intents/page.tsx`).
  - Status-transition endpoint: `PATCH /foster/applications/{id}/status` (`app/adapters/inbound/api/foster_router.py:26`).
  - Auth guards: `get_protector`, `get_foster`, `get_current_user` (`app/adapters/inbound/api/middleware/auth.py`).
  - Migrations are hand-written, numbered Alembic revisions (`alembic/versions/002_donation_intents.py`).

## Proposed Design

### Ownership & lifecycle model
1. **Registration creates a real (unlisted) partner + one negotiation.** Instead of storing a JSON snapshot, the business info is persisted as a `PartnerModel` row with `is_active=False` and `owner_id=NULL`. A `PartnerNegotiationModel` row (status `pending`) links that partner to exactly **one** target host (`host_id`).
2. **1 partner ↔ 1 negotiation.** Requirement 2 states the business chooses a single protector/foster at registration. This 1:1 mapping is the smallest model that satisfies the requirement and avoids a fan-out of competing offers. (See Open Questions if multi-host bidding is later desired.)
3. **Acceptance goes live.** When the host accepts, the service sets `partner.owner_id = negotiation.host_id` and `partner.is_active = True`. Reject/counter leave the partner unlisted.
4. **Public listing filter.** `GET /partners` returns partners with `is_active == True AND owner_id IS NOT NULL`. Because new partners start inactive, they are invisible until accepted.
5. **Ownership unlocks mutation.** `PATCH /partners/{id}` and `DELETE /partners/{id}` are authenticated and require `partner.owner_id == current_user.id`.

### Actors & auth (judgment call)
There is no "business" user account and registration is public today. We keep **registration unauthenticated** (consistent with adoption/donation intents, which capture contact info from anonymous submitters). The negotiation therefore carries `contact_email` + `contact_phone` so the host can reach the business out-of-band. All host-side actions (list negotiations, accept/reject/counter, edit/delete owned partner) require `get_current_user` and are scoped by `host_id`/`owner_id` — **not** role-gated, because both protectors and fosters can host.

### Negotiation status
`NegotiationStatus`: `pending | accepted | rejected | countered`. `countered` records the host's counter terms (`counter_amount`, `counter_message`) for offline follow-up; the business cannot respond in-app (no account), so a countered negotiation is resolved when the host later accepts or rejects. This is the pragmatic scope boundary (see Open Questions).

### Error handling
Service raises `ValueError` for not-found / not-owned / invalid-transition; routers map to `404`/`403`/`400` exactly like `donation_router.py` and `foster_router.py`.

## Scope
- **In scope:** partner registration with host selection + proposed deal; host review/accept/reject/counter; owner edit/delete; public listing filter; frontend register form update, dashboard negotiations view, owner-scoped edit/delete UI; Alembic migration.
- **Out of scope (explicitly):** a "business" user role/login; in-app business response to counters; per-transaction commission (the deal is a single `proposed_amount`); payment processing/escrow; geolocation of `find_by_location` (unchanged).

## Interfaces / Models / Endpoints

### Domain
```python
# value_objects.py
class NegotiationStatus(str, Enum):
    pending = "pending"; accepted = "accepted"; rejected = "rejected"; countered = "countered"

# entities/partner.py — extend Partner
owner_id: UUID | None = None

# entities/partner.py — new
@dataclass
class PartnerNegotiation:
    partner_id: UUID
    host_id: UUID
    proposed_amount: float
    contact_email: str
    contact_phone: str
    id: UUID | None = None
    proposed_message: str | None = None
    status: NegotiationStatus = NegotiationStatus.pending
    counter_amount: float | None = None
    counter_message: str | None = None
    created_at: datetime | None = None

# entities/user.py — new read model for host picker
@dataclass
class Host:
    user_id: UUID
    role: UserRole
    display_name: str      # org_name (protector) or full_name (foster)
    city: str | None = None
    state: str | None = None
```

### Persistence
- `PartnerModel`: add `owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)`. Keep existing `is_active` column (server_default true) but registration writes `is_active=False` explicitly.
- New `PartnerNegotiationModel` (`partner_negotiations`): `id`, `partner_id` FK→partners.id, `host_id` FK→users.id, `proposed_amount` Float, `proposed_message` Text?, `contact_email`, `contact_phone`, `status` default `'pending'`, `counter_amount` Float?, `counter_message` Text?, `created_at`.

### Ports (`repositories.py`)
- `PartnerRepository`: add `find_by_id(id)`, `delete(id)`, `save_negotiation(n)`, `find_negotiation_by_id(id)`, `find_negotiations_by_host(host_id)`.
- `UserRepository`: add `find_hosts() -> list[Host]`.

### Endpoints (all under `/api/v1`)
| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/partners` | public | List **accepted+active** partners (changed filter) |
| GET | `/partners/hosts` | public | List protectors + fosters to apply to (`HostResponse`) |
| POST | `/partners/register` | public | Create unlisted partner + pending negotiation |
| GET | `/partners/negotiations` | current_user | Negotiations targeting me (embeds partner business info) |
| PATCH | `/partners/negotiations/{id}` | current_user (host owns) | `action`: accept \| reject \| counter (+ counter fields) |
| PATCH | `/partners/{id}` | current_user (owner) | Update business/coupon fields |
| DELETE | `/partners/{id}` | current_user (owner) | Delete owned partner |

Route ordering: static paths (`/hosts`, `/register`, `/negotiations`) MUST be declared before `/{id}` paths to avoid path-param capture (FastAPI matches in declaration order).

### Schemas (`schemas/partner.py`)
- `HostResponse{ user_id, role, display_name, city?, state? }`
- `PartnerRegister{ name, description?, address, cep, city, state, coupon_code?, discount_pct?, host_id, proposed_amount>0, proposed_message?, contact_email, contact_phone }`
- `NegotiationResponse{ id, status, proposed_amount, proposed_message?, contact_email, contact_phone, counter_amount?, counter_message?, created_at, partner: PartnerResponse }`
- `NegotiationAction{ action: Literal['accept','reject','counter'], counter_amount?, counter_message? }`
- `PartnerUpdate{ name?, description?, address?, cep?, city?, state?, coupon_code?, discount_pct? }`
- Extend `PartnerResponse` with `owner_id: UUID | None`.

### Frontend types (`rescute/src/lib/types/index.ts`)
Add `NegotiationStatus`, `PartnerNegotiation`, `Host`; add `owner_id?: string | null` to `Partner`.

## Impact Analysis
- **Breaking:** `GET /partners` filter tightens — any partner without an accepted negotiation disappears from the public list. Existing seeded partners have `owner_id=NULL` and will vanish; migration/backfill note below.
- **DI change:** `PartnerService` now needs `UserRepository` (for hosts) in addition to `PartnerRepository`; update `get_partner_service` (`dependencies.py:89`).
- **Frontend dead code:** replace `createPartner` (`partners.ts:4`) POST `/partners` with `registerPartner` → `/partners/register`.
- **Migration/backfill:** `003` adds `partners.owner_id` + `partner_negotiations`. Existing demo partners would drop off the public list. Decide per Open Questions whether the migration backfills a synthetic accepted negotiation/owner for seed data, or seed data is re-created. Default: do **not** auto-backfill; document that seeds must be re-registered.
- **Security:** owner/host scoping enforced in the service layer (mirrors `donation_service`), never trusting client-supplied ids. `proposed_amount`/`counter_amount` validated `> 0`.
- **Next.js caveat:** `rescute/AGENTS.md` warns this Next.js has non-standard APIs — the Implementer MUST read `node_modules/next/dist/docs/` before touching any page/routing/`.tsx` file.
- **Tests:** add service tests for register (creates inactive partner + pending negotiation), accept (flips active + owner), reject/counter, owner-scoped update/delete rejection; repository round-trip for negotiations; router auth/403/404 paths. (No existing test suite located — confirm test tooling before writing; do not block units on it.)

## Implementation Units
Dependency-ordered, ~50 LOC max each.

**Backend**
1. **Negotiation enum + entities** — files: `app/domain/value_objects.py`, `app/domain/entities/partner.py`, `app/domain/entities/user.py` — add `NegotiationStatus`, `PartnerNegotiation`, `Host`, and `owner_id` on `Partner`. Acceptance: imports resolve; `Partner(...)` accepts `owner_id`.
2. **Persistence models** — files: `app/adapters/outbound/persistence/models.py` — add `owner_id` to `PartnerModel`; add `PartnerNegotiationModel`. Acceptance: `Base.metadata` includes `partner_negotiations` with all columns.
3. **Alembic migration `003_partner_negotiations`** — files: `alembic/versions/003_partner_negotiations.py` — `add_column partners.owner_id` (FK users.id, nullable); `create_table partner_negotiations`; downgrade reverses. `down_revision="002_donation_intents"`. Acceptance: upgrade/downgrade are symmetric.
4. **Port signatures** — files: `app/domain/ports/repositories.py` — add abstract `find_by_id`, `delete`, `save_negotiation`, `find_negotiation_by_id`, `find_negotiations_by_host` to `PartnerRepository`; `find_hosts` to `UserRepository`. Acceptance: ABCs updated.
5. **Partner repo — partner methods + filter** — files: `app/adapters/outbound/persistence/partner_repository.py` — implement `find_by_id`, `delete`, add `owner_id` to `_to_model`/`_to_domain`, change `find_all` filter to `is_active AND owner_id IS NOT NULL`. Acceptance: listed partners require owner.
6. **Partner repo — negotiation methods + mappers** — files: `app/adapters/outbound/persistence/partner_repository.py` — implement `save_negotiation`, `find_negotiation_by_id`, `find_negotiations_by_host`, plus `_negotiation_to_domain`. Acceptance: round-trips a `PartnerNegotiation`.
7. **User repo — find_hosts** — files: `app/adapters/outbound/persistence/user_repository.py` — query protectors+fosters joined to profiles, map to `Host` (display_name from `org_name`/`full_name`). Acceptance: returns both roles with names.
8. **PartnerService — register + hosts + list** — files: `app/application/partner_service.py` — inject `UserRepository`; add `list_hosts()`, `register(data) -> PartnerNegotiation` (creates inactive partner then pending negotiation), keep `list()`. Acceptance: register persists both rows.
9. **PartnerService — act + update + delete** — files: `app/application/partner_service.py` — add `list_negotiations(host_id)`, `act_on_negotiation(host_id, id, action, counter_*)` (accept flips partner active+owner; enforce `host_id` match), `update_partner(owner_id, id, data)`, `delete_partner(owner_id, id)` (enforce ownership, raise `ValueError` otherwise). Acceptance: non-owner/non-host raises.
10. **Schemas** — files: `app/adapters/inbound/api/schemas/partner.py` — add `HostResponse`, `PartnerRegister`, `NegotiationResponse`, `NegotiationAction`, `PartnerUpdate`; add `owner_id` to `PartnerResponse`. Acceptance: models validate.
11. **DI wiring** — files: `app/dependencies.py` — `get_partner_service` also depends on `get_user_repository`. Acceptance: app boots.
12. **Router — public routes** — files: `app/adapters/inbound/api/partner_router.py` — add `GET /partners/hosts`, `POST /partners/register` (declared before `/{id}`). Acceptance: register returns 201 with negotiation.
13. **Router — host routes** — files: `app/adapters/inbound/api/partner_router.py` — add `GET /partners/negotiations`, `PATCH /partners/negotiations/{id}`, `PATCH /partners/{id}`, `DELETE /partners/{id}` with `get_current_user` + `ValueError`→404/403. Acceptance: auth + ownership enforced.

**Frontend** (read `node_modules/next/dist/docs/` first)
14. **Types** — files: `rescute/src/lib/types/index.ts` — add `NegotiationStatus`, `PartnerNegotiation`, `Host`; `owner_id?` on `Partner`. Acceptance: `tsc` clean.
15. **API client** — files: `rescute/src/lib/api/partners.ts` — replace `createPartner` with `registerPartner` → `/partners/register`; add `getHosts`, `getNegotiations`, `actOnNegotiation`, `updatePartner`, `deletePartner`. Acceptance: signatures match schemas.
16. **Register form — host picker + offer** — files: `rescute/src/components/partners/PartnerForm.tsx` — fetch `getHosts`, add a host `<select>`, `proposed_amount`, `proposed_message`, `contact_email`, `contact_phone`; call `registerPartner`. Acceptance: submits full payload; success state unchanged.
17. **Dashboard negotiations page** — files: `rescute/src/app/dashboard/partners/page.tsx` (new) — list `getNegotiations`, show partner info + proposed amount, accept/reject/counter buttons (mirror `intents/page.tsx`). Acceptance: actions call `actOnNegotiation` and refresh.
18. **Dashboard nav item** — files: `rescute/src/components/dashboard/DashboardNav.tsx` — add `['/dashboard/partners', 'Purrtners']`. Acceptance: link renders/active-highlights.
19. **Owner edit/delete affordance** — files: `rescute/src/components/partners/PartnerCard.tsx` (+ `rescute/src/app/partners/page.tsx` to pass current user) — when `useAuth().user?.id === partner.owner_id`, show Edit/Delete calling `updatePartner`/`deletePartner`. Acceptance: controls appear only for owner.

## Open Questions
1. **Counter semantics:** confirm that a countered negotiation is resolved offline (host later accepts/rejects) and no in-app business reply is needed for this milestone. Assumed **yes**.
2. **Seed/demo partners:** should `003` backfill a synthetic accepted negotiation + `owner_id` so existing demo partners stay visible, or will seeds be re-created via `/partners/register`? Assumed **re-create seeds** (no backfill).
3. **Host visibility:** should `/partners/hosts` list all protectors+fosters, or only those meeting some criteria (e.g., has a profile / is_active)? Assumed **all active users with a profile**.
4. **Amount currency/units:** `proposed_amount` is a plain float in the same unit as donation amounts (BRL, no cents handling). Confirm no currency field is required.
