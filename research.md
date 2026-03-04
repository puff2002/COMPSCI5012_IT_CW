# Repository Research Report

## 1) Scope and Method

This report is based on a full pass through the current repository contents, including:

- top-level structure and git history
- all project/spec Markdown files
- all Draw.io source diagrams (`.drawio`) and exported PNGs
- assessment briefs in `assessment/`
- lecture materials in `lecture_slides/`

I analyzed both final artifacts and versioned variants (especially ER/wireframe iterations) to understand intent, evolution, and implementation implications.

## 2) What This Repository Is

This repository is a **coursework planning and design workspace** for an Internet Technology group project called **SmartCloset**.

It is **not** an implementation repository yet. There is currently:

- no Django project
- no Python backend code
- no HTML/CSS/JS source app
- no tests, deployment config, or runtime scripts

The repo currently functions as:

1. a **design package** (`spec/`) for the planned app
2. an **assessment brief archive** (`assessment/`)
3. a **lecture reference archive** (`lecture_slides/`)

## 3) High-Level Folder Anatomy

### `spec/`
Primary design artifacts for SmartCloset:

- `Project Design.md` (concise product + user-story summary)
- system architecture diagram
- sitemap diagram
- ER diagram versions (`er`, `er_v2`, `er_v3`, `er_v4`)
- wireframe versions (`Wireframes`, `Wireframes_v2`, split `v3_*` pages)
- `backend_api.md` (broken symlink; details below)

### `assessment/`
Assignment briefs and guidance:

- Design Specification brief (coursework 4)
- Implementation Report brief (coursework 5)
- Video Presentation brief (coursework 6)
- Example visuals (`assessment/examples/*.png`)

### `lecture_slides/`
Seven lecture decks in PDF plus extracted/converted Markdown text:

- Week 1: architecture, ER, info architecture
- Week 2: frameworks + Django
- Week 3: HTML/CSS/Bootstrap + accessibility/sustainability framing
- Week 4: protocols/messaging/REST
- Week 5: client-side environment
- Week 6: client-side scripting (JavaScript)
- Week 7: jQuery/AJAX

### `frontend/`
Currently empty directory.

## 4) Product Intent: What SmartCloset Is Supposed to Do

From `spec/Project Design.md`, SmartCloset is a wardrobe web app centered on:

1. user accounts + profile fields (nickname/height/weight)
2. digital clothing inventory with CRUD
3. outfit generation (OOTD) using random/filtered logic
4. outfit history/logging
5. optional weather integration and optional AI recommendation

### User-story prioritization currently defined

- **Must**: auth, inventory input/storage, filtering/viewing, CRUD
- **Should**: OOTD generation, outfit history
- **Could**: weather-aware suggestions
- **Won’t**: AR virtual try-on

This aligns with course minimum constraints (auth + DB interaction + meaningful user input).

## 5) System Architecture (as Designed)

From `spec/system_architecture/smart_closet_System_Architecture.drawio`:

### Three-tier decomposition

- **Client Tier**: web browser (HTML/CSS/JS)
- **Application Tier**: web server (logic/routing) + image upload handler
- **Data Tier**: SQL database for user/item/log data

### Explicit integrations and flows

- Browser <-> server via **HTTP JSON**
- Server <-> DB via **SQL Query**
- Server <-> external **Weather API** via API calls

### Interpretation

This architecture assumes either:

- API-first backend responses (JSON), or
- mixed rendering with JSON-based endpoints for interactive features

Given coursework requirements (Django backend mandatory), this maps naturally to Django views/DRF-style endpoints.

## 6) Information Architecture / Navigation Model

From `spec/sitemap/smart_closet_site_map.drawio`:

### Entry and auth flow

- `Login Page` <-> `Register Page` (new user branch)
- `Login` -> `Dashboard` on auth success

### Main navigation (Level 1)

- Dashboard
- My Closet
- OOTD Generator
- History
- Settings

### Feature level (Level 2)

- Closet: search/filters, item grid, add-item modal
- OOTD: preference selection (season/occasion), result view, quick picks
- History: outfit log listing by date
- Settings: profile settings, app preferences, security zone

### Detail level (Level 3)

- edit/delete confirmations
- save-to-history action
- wear-again / delete history entry
- change password
- delete-account warning

### Specificity worth noting

The sitemap is unusually explicit for student work: it models hierarchy bands (public, level1/2/3), includes edge semantics (auth success/new user), and visually distinguishes danger/security actions.

## 7) Data Model Evolution and Current State

There are four ER iterations showing a clear progression.

### `smart_closet_er.drawio` (early normalized attempt)
Entities include:

- `USER`
- `CLOTHING_ITEM`
- `CATEGORY`
- `OUTFIT_LOG`

Relationships include:

- USER owns CLOTHING_ITEM (1:N)
- CATEGORY classifies CLOTHING_ITEM (1:N)
- USER records OUTFIT_LOG (1:N)
- OUTFIT_LOG includes CLOTHING_ITEM (M:N)

This version has stronger relational normalization (separate category entity + explicit log).

### `smart_closet_er_v2.drawio` (conceptual simplification)
Concept-level nodes only (User, Clothing Item, Outfit combinations, History Log, User Preferences) without full attribute definitions.

### `smart_closet_er_v3` and `v4` (current detailed tabular version)
Entities become:

- `USER`
- `CLOTHING_ITEM`
- `OUTFIT (OOTD)`

`v4` details:

- USER: `User_ID`, `Username`, `Email`, `Password_Hash`, `Gender`, `Height_CM`, `Weight_KG`, `Settings_JSON`
- CLOTHING_ITEM: `Item_ID`, `User_ID`, `Category`, `Season`, `Image_URL`
- OUTFIT: `Outfit_ID`, `User_ID`, `Date_Created`, `Occasion`, `Weather_Info`

Relationships in `v4`:

- USER **OWNS** CLOTHING_ITEM (1:N)
- USER **GENERATES** OUTFIT (1:N)
- CLOTHING_ITEM **CONTAINS** OUTFIT (M:N)

### Critical model implications

1. `v4` removes explicit `CATEGORY` entity and stores category as string.
2. `v4` replaces `OUTFIT_LOG` with `OUTFIT` concept.
3. `M:N` between clothing and outfit implies a join table will be required in actual Django models.
4. `Settings_JSON` indicates intent to mix normalized and semi-structured preference storage.

### Inconsistency to address before coding

The textual design says outfit generation often picks Top+Bottom (or single full-body piece), but ER `v4` has no explicit structure for outfit item roles (top/bottom/full) beyond free-form category values. This will need stricter schema or validation logic during implementation.

## 8) Wireframe System and UI Specificity

Wireframe iterations:

- `smart_closet_Wireframes.drawio`: minimal 4-screen base (login/dashboard/add/generator)
- `smart_closet_Wireframes_v2.drawio`: expanded multi-screen flow
- `smart_closet_Wireframes_v3_*`: split, annotated page-specific designs

### Covered screens in v3 set

- auth (login/register)
- dashboard + add/edit flow
- my closet listing/search/filter/pagination
- OOTD generator with preferences + quick picks
- outfit history with filtering and actions
- settings (profile/preferences/security)

### Usability details already designed

- side navigation appears as persistent IA anchor
- CRUD actions are visible and local to context
- history has reuse + delete shortcuts
- settings includes danger-zone concepts (delete account)
- each v3 page has numbered annotations describing intent

### Quality artifacts

There are minor noisy artifacts in Draw.io content (e.g., stray `dwd` labels, mixed newline encodings), but overall structure is coherent.

## 9) Assessment Alignment: How Well the Design Fits Marking Requirements

Based on the briefs in `assessment/`:

### Strong alignment already present

- clear app overview and user-story set
- explicit auth/data-input/data-storage use cases
- architecture + ER + sitemap + wireframes included
- accessibility and sustainability are identified as required implementation/report dimensions

### Gaps relative to implementation coursework (CW5)

Not present yet in repo:

- Django codebase
- responsive UI implementation assets
- client-side interactivity code
- tests
- sustainability benchmark evidence (before/after)
- accessibility implementation evidence on chosen pages
- deployment artifacts/URLs

So the repository is currently **design-ready but implementation-empty**.

## 10) Repository Integrity and Tooling Findings

### Git history pattern

Four commits on March 4, 2026:

1. initial asset import
2. update adding API symlink + dashboard annotation tweak
3. folder reorganization into `assessment/spec`
4. lecture slide import

History suggests rapid structuring rather than iterative software development.

### Important broken reference

`spec/backend_api.md` is a symlink to `../Wardrobe-Management/backend/API.md` and is currently broken in this repository context.

Impact:

- API contract cannot be inspected locally
- backend endpoint assumptions in spec are currently unverifiable

### Repo hygiene

- `.gitignore` only ignores `.DS_Store`
- no language-specific ignores yet (expected since no app code)

## 11) Deep Summary: How This Project “Works” Right Now

At present, this workspace “works” as a **design intelligence package**, not as executable software.

Operationally, the current assets provide:

1. Product intent (what SmartCloset should do)
2. Interaction architecture (how users move through pages/features)
3. System decomposition (client/app/data/external weather API)
4. Data contracts at conceptual ER level (with evolving schema choices)
5. Coursework compliance scaffolding (what must be built/reported)
6. Theory context (lecture references to guide implementation choices)

It does **not** currently execute or deliver user-facing behavior because implementation assets are absent.

## 12) Key Specificities and Risks to Preserve

Most important specifics discovered:

- `M1/M2/M3/M4 + S1/S2 + C1/W1` MoSCoW framing is already tightly defined.
- Weather API integration is treated as optional at feature level but present in architecture and OUTFIT schema (`Weather_Info`).
- Data model evolution moved from normalized category/log entities to simpler string-driven design; this will trade flexibility for speed unless corrected.
- Security-sensitive flows are explicitly in IA/wireframes (change password/delete account), which increases implementation scope beyond basic CRUD.
- Linked backend API spec is missing due broken symlink, creating a blind spot for endpoint naming and payload formats.

## 13) Recommended Immediate Follow-up (from this analysis)

1. Restore or replace `spec/backend_api.md` with an in-repo API contract.
2. Freeze one canonical ER version (currently `v4`) and explicitly define outfit-item role modeling.
3. Convert v3 wireframes + sitemap into route list and component checklist.
4. Bootstrap Django project structure and map each Must story to model/view/template/API endpoint.
5. Define accessibility and sustainability acceptance criteria early (before UI implementation drift).

---

### Final Conclusion

This repository is a well-assembled **pre-implementation design dossier** for a SmartCloset web app and coursework submission pipeline. It demonstrates strong planning artifacts (architecture/sitemap/wireframes/ER evolution), but no executable system yet. The main technical blockers before implementation are schema finalization consistency and the missing API spec target.
