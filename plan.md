# SmartCloset Frontend Implementation Plan

## 1. Goal

Build a responsive, accessible frontend for SmartCloset that consumes the backend API in `spec/backend_api.md`, using skills from `lecture_slides`:

- Week 3: HTML + CSS + Bootstrap
- Week 4: HTTP/REST + request/response design
- Week 6: JavaScript (DOM/event/state)
- Week 7: jQuery + AJAX

This plan targets a frontend-first build in `frontend/` that can later be served by Django static/templates.

## 2. Scope (Mapped to Your Spec)

Must-have pages/features:

1. Auth: Login + Register
2. Closet: list/filter/add/edit/delete clothing items
3. OOTD Generator: weather-based recommendation
4. Outfit History: list/create/update/delete history entries
5. Settings: profile + integration/weather config + logout

## 3. Frontend Architecture

## 3.1 Folder Structure

```text
frontend/
  index.html                 # login/register shell
  dashboard.html             # main app shell
  closet.html
  ootd.html
  history.html
  settings.html
  assets/
    css/
      base.css
      components.css
      pages.css
    js/
      config.js
      auth.js
      api.js
      ui.js
      pages/
        login.js
        closet.js
        ootd.js
        history.js
        settings.js
    img/
      placeholder-item.png
```

## 3.2 Data/Request Flow

1. User logs in via `/api/auth/user/login/`
2. Store `access` + `refresh` in browser storage
3. All protected requests attach `Authorization: Bearer <access>`
4. On `401`, refresh token via `/api/auth/refresh/` and retry once
5. Logout calls `/api/auth/logout/`, then clear local tokens

## 4. API Mapping (Frontend Actions -> Backend Endpoints)

| Frontend action | Endpoint |
| --- | --- |
| Register | `POST /api/auth/user/register/` |
| Login | `POST /api/auth/user/login/` |
| Current user | `GET /api/auth/me/` |
| Load closet | `GET /api/wardrobe/items/` |
| Add item | `POST /api/wardrobe/items/` |
| Update item | `PATCH /api/wardrobe/items/{id}/` |
| Delete item | `DELETE /api/wardrobe/items/{id}/` |
| Upload image | `POST /api/wardrobe/items/upload/` |
| Recommend OOTD | `POST /api/outfits/recommend/` |
| History list | `GET /api/outfits/history/` |
| Add history | `POST /api/outfits/history/` |
| Edit history | `PATCH /api/outfits/history/{id}/` |
| Delete history | `DELETE /api/outfits/history/{id}/` |
| Weather city search | `GET /api/integrations/weather/search/?query=...` |
| Weather now | `GET /api/integrations/weather/now/?location=...` |

## 5. Step-by-Step Implementation Plan

## Step 1: Bootstrap the shared UI shell

Deliverables:

- Shared navigation matching sitemap/wireframes
- Responsive grid/layout using Bootstrap
- Shared CSS variables and utility classes

Snippet (`dashboard.html` shell):

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SmartCloset Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="./assets/css/base.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to content</a>
  <div class="container-fluid">
    <div class="row min-vh-100">
      <aside class="col-12 col-md-3 col-lg-2 app-sidebar p-3">
        <h1 class="h5">SmartCloset</h1>
        <nav aria-label="Main navigation">
          <a href="./dashboard.html" class="nav-link">Dashboard</a>
          <a href="./closet.html" class="nav-link">My Closet</a>
          <a href="./ootd.html" class="nav-link">OOTD Generator</a>
          <a href="./history.html" class="nav-link">History</a>
          <a href="./settings.html" class="nav-link">Settings</a>
        </nav>
      </aside>
      <main id="main-content" class="col-12 col-md-9 col-lg-10 p-4">
        <h2>Dashboard</h2>
        <div id="status-region" class="visually-hidden" aria-live="polite"></div>
      </main>
    </div>
  </div>
</body>
</html>
```

Snippet (`assets/css/base.css`):

```css
:root {
  --bg: #f4f7fb;
  --panel: #ffffff;
  --brand: #1457a6;
  --text: #1f2a37;
}

body {
  background: linear-gradient(180deg, #eef4ff 0%, var(--bg) 100%);
  color: var(--text);
}

.app-sidebar {
  background: var(--panel);
  border-right: 1px solid #d9e2ef;
}

.skip-link {
  position: absolute;
  left: -9999px;
}

.skip-link:focus {
  left: 1rem;
  top: 1rem;
  z-index: 9999;
  background: #fff;
  padding: .5rem .75rem;
}
```

## Step 2: Implement auth (register/login/logout)

Deliverables:

- Register form + client validation
- Login form + token persistence
- Auth guard for protected pages

Snippet (`assets/js/config.js`):

```js
export const API_BASE = "http://127.0.0.1:8000/api";
```

Snippet (`assets/js/auth.js`):

```js
const ACCESS_KEY = "sc_access";
const REFRESH_KEY = "sc_refresh";

export function setTokens({ access, refresh }) {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}
```

Snippet (`assets/js/pages/login.js` using jQuery AJAX):

```js
import { API_BASE } from "../config.js";
import { setTokens } from "../auth.js";

$("#loginForm").on("submit", function (e) {
  e.preventDefault();
  $.ajax({
    url: `${API_BASE}/auth/user/login/`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      username: $("#username").val().trim(),
      password: $("#password").val()
    })
  }).done((data) => {
    setTokens(data);
    window.location.href = "../../dashboard.html";
  }).fail((xhr) => {
    $("#loginError").text(xhr.responseJSON?.detail || "Login failed");
  });
});
```

## Step 3: Build API client wrapper with refresh-retry

Deliverable: one place for all authenticated fetch calls.

Snippet (`assets/js/api.js`):

```js
import { API_BASE } from "./config.js";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./auth.js";

async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error("No refresh token");
  const res = await fetch(`${API_BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh })
  });
  if (!res.ok) throw new Error("Refresh failed");
  const data = await res.json();
  setTokens(data);
  return data.access;
}

export async function apiFetch(path, options = {}, retry = true) {
  const access = getAccessToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
    ...(access ? { Authorization: `Bearer ${access}` } : {})
  };

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401 && retry) {
    try {
      const newAccess = await refreshAccessToken();
      return apiFetch(path, {
        ...options,
        headers: { ...(options.headers || {}), Authorization: `Bearer ${newAccess}` }
      }, false);
    } catch {
      clearTokens();
      window.location.href = "/frontend/index.html";
    }
  }
  return res;
}
```

## Step 4: Closet page (CRUD + upload + filters)

Deliverables:

- List cards from `/wardrobe/items/`
- Add/edit modal
- Delete confirm
- Image upload (`multipart/form-data`)

Snippet (`assets/js/pages/closet.js`):

```js
import { apiFetch } from "../api.js";

async function loadItems() {
  const res = await apiFetch("/wardrobe/items/");
  const items = await res.json();
  const html = items.map(item => `
    <article class="card p-3">
      <img src="${item.image_url || "./assets/img/placeholder-item.png"}" alt="${item.item}" class="img-fluid rounded">
      <h3 class="h6 mt-2 mb-1">${item.item}</h3>
      <p class="small text-muted mb-2">${item.category} · ${item.color_semantics || "unknown color"}</p>
      <button class="btn btn-sm btn-outline-danger" data-id="${item.id}" data-action="delete">Delete</button>
    </article>
  `).join("");
  document.querySelector("#itemsGrid").innerHTML = html;
}

document.querySelector("#uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.querySelector("#file");
  const fd = new FormData();
  fd.append("file", fileInput.files[0]);

  const res = await fetch("http://127.0.0.1:8000/api/wardrobe/items/upload/", {
    method: "POST",
    headers: { Authorization: `Bearer ${localStorage.getItem("sc_access")}` },
    body: fd
  });
  if (res.ok) loadItems();
});

loadItems();
```

## Step 5: OOTD generator page

Deliverables:

- City search + location id selection
- Generate recommendation (`/outfits/recommend/`)
- Save to history

Snippet:

```js
import { apiFetch } from "../api.js";

async function recommend(locationId) {
  const res = await apiFetch("/outfits/recommend/", {
    method: "POST",
    body: JSON.stringify({ location: locationId })
  });
  const data = await res.json();
  document.querySelector("#weatherText").textContent =
    `${data.weather.location} ${data.weather.temperature}°C, ${data.weather.condition}`;
  document.querySelector("#recommendText").textContent =
    data.outfit.recommendation_text || "No recommendation text returned.";
}
```

## Step 6: History page

Deliverables:

- List history entries
- Rate/edit feedback
- Delete history item

Snippet:

```js
import { apiFetch } from "../api.js";

async function deleteHistory(id) {
  const res = await apiFetch(`/outfits/history/${id}/`, { method: "DELETE" });
  if (res.ok) {
    await loadHistory();
  }
}
```

## Step 7: Settings + integrations page

Deliverables:

- Show current user info (`/auth/me/`)
- Show integration config (`/integrations/config/`)
- Update integration config
- Logout flow

Snippet:

```js
import { apiFetch } from "../api.js";
import { clearTokens } from "../auth.js";

document.querySelector("#logoutBtn").addEventListener("click", async () => {
  const refresh = localStorage.getItem("sc_refresh");
  await apiFetch("/auth/logout/", {
    method: "POST",
    body: JSON.stringify({ refresh })
  });
  clearTokens();
  window.location.href = "./index.html";
});
```

## 6. Accessibility Plan (Implement During Build)

Apply at least these 5 items across auth + closet + ootd:

1. Proper labels and input associations (`<label for=...>`)
2. Keyboard reachable controls, visible focus states
3. `aria-live` for async messages (success/error/loading)
4. Color contrast >= WCAG AA
5. Form errors linked by `aria-describedby`

Snippet:

```html
<label for="username" class="form-label">Username</label>
<input id="username" name="username" class="form-control" aria-describedby="usernameHelp" required>
<div id="usernameHelp" class="form-text">Use your registered username.</div>
<div id="formStatus" class="visually-hidden" aria-live="polite"></div>
```

## 7. Sustainability/Performance Plan

Baseline and after-change (Lighthouse) on:

1. Login page
2. Closet page

Optimizations:

- compress images before upload preview
- lazy-load item thumbnails (`loading="lazy"`)
- minify CSS/JS for deploy
- avoid duplicate API calls with local cache per page

Snippet:

```html
<img src="..." alt="White T-shirt" loading="lazy" width="240" height="240">
```

## 8. Suggested Build Sequence (Execution Order)

1. Create static page shells and shared styles.
2. Finish auth and route guards first.
3. Implement closet CRUD + upload.
4. Implement OOTD recommendation and weather search.
5. Implement outfit history interactions.
6. Implement settings/integrations/logout.
7. Accessibility pass and keyboard/focus testing.
8. Lighthouse baseline + improvements + after report.

## 9. Definition of Done

Frontend is done when:

1. All main pages from sitemap/wireframes are functional.
2. Must + Should stories are testable through UI.
3. Token refresh works without manual relogin.
4. Core flows are responsive on mobile and desktop.
5. Accessibility criteria are demonstrably implemented.
6. Lighthouse before/after evidence is captured.

## 10. Risks and Mitigations (Backend-Aligned)

- Risk: category values are strict enum (`top|bottom|shoes`), while AI/upload pipelines may output inconsistent labels.
  - Mitigation: enforce client-side normalization before submit; reject unknown values early in form validation; add contract tests for upload-returned category.
- Risk: `POST /api/outfits/recommend/` creates both `Outfit` and `OutfitHistory` records automatically (side effect).
  - Mitigation: frontend must not auto-create an additional history entry after recommend success; treat returned `history` object as source of truth.
- Risk: weather dependency can return `503 weather unavailable`, blocking recommendation.
  - Mitigation: provide fallback UX ("manual outfit selection" path), retain last successful recommendation in UI state, and show retry action with status messaging.
- Risk: token refresh flow may fail due missing/expired refresh token.
  - Mitigation: single refresh-retry in `api.js`, then hard logout + redirect; preserve the intended return page in query string for better recovery UX.
- Risk: media upload + image analysis path can fail (`file required`, non-image, analyzer exception).
  - Mitigation: pre-validate MIME/size client-side, show explicit upload error states, and allow manual item creation when analysis fails.
- Risk: frontend/backend schema drift over time (API docs and backend code updated separately).
  - Mitigation: update `spec/backend_api.md` and `spec/backend_issues.md` at each backend contract change, and run a smoke test checklist against live endpoints before demos.
- Risk: access-control regressions (user should only read/write own wardrobe/history).
  - Mitigation: add integration tests for cross-user access and validate every list/detail endpoint is user-scoped in QA.
- Risk: performance and dependency footprint (e.g., `rembg`/`onnxruntime`) can slow local demos.
  - Mitigation: separate "core demo path" from "AI upload path"; preload sample items so core CRUD/OOTD flows work even when heavy services are unavailable.

## 11. Detailed TODO List (Phased, Do Not Implement Yet)

Use this checklist as the execution tracker for the whole frontend plan.

### Phase 0: Project setup and alignment

- [ ] Confirm scope freeze for Must/Should/Could features with team.
- [ ] Confirm backend base URL and environment strategy (`dev`, `demo`, `prod`).
- [ ] Verify `spec/backend_api.md` version matches active backend branch.
- [ ] Create issue-tracking rhythm using `spec/backend_issues.md`.
- [ ] Define page ownership (who builds which page/module).
- [ ] Define coding conventions (JS style, naming, error handling, commit format).

### Phase 1: Frontend skeleton and shared system

- [ ] Create `frontend/` file/folder structure from Section 3.1.
- [ ] Create all page shells (`index`, `dashboard`, `closet`, `ootd`, `history`, `settings`).
- [ ] Implement shared sidebar/top navigation and active-link state.
- [ ] Add shared CSS foundations (`base.css`, variables, spacing, typography).
- [ ] Add reusable utility classes (cards, form groups, status banners, empty states).
- [ ] Add skip-link and global `aria-live` region patterns.
- [ ] Set up shared JS modules (`config.js`, `auth.js`, `api.js`, `ui.js`) as stubs.

### Phase 2: Authentication and route protection

- [ ] Build register form UI and validation states.
- [ ] Build login form UI and validation states.
- [ ] Implement register API call and success/error handling.
- [ ] Implement login API call and token persistence.
- [ ] Implement logout API call and token clearing.
- [ ] Implement auth guard for protected pages.
- [ ] Implement redirect flow for unauthenticated access attempts.
- [ ] Implement token refresh + single retry strategy on 401.
- [ ] Add auth UX polish (loading states, disabled submit, readable error messages).

### Phase 3: Closet CRUD and upload flow

- [ ] Build closet grid/list layout with responsive behavior.
- [ ] Implement load/list items from `/api/wardrobe/items/`.
- [ ] Build add-item form (manual create path).
- [ ] Build edit-item form/modal.
- [ ] Implement delete confirmation and delete action.
- [ ] Implement filter/search UI (category/style/season/usage where applicable).
- [ ] Implement upload form for `/api/wardrobe/items/upload/`.
- [ ] Add upload pre-validation (file type/size) and failure handling.
- [ ] Normalize/validate `category` values (`top|bottom|shoes`) before submit.
- [ ] Add empty-state and first-item onboarding hints.

### Phase 4: OOTD recommendation flow

- [ ] Build weather location search UI.
- [ ] Implement city search (`/api/integrations/weather/search/`).
- [ ] Implement current weather preview (`/api/integrations/weather/now/`).
- [ ] Build OOTD result panel (weather + recommendation + selected items).
- [ ] Implement `POST /api/outfits/recommend/`.
- [ ] Ensure returned `history` from recommend is used as source of truth.
- [ ] Add graceful fallback path when weather/recommendation fails (manual selection).
- [ ] Add clear state transitions (idle/loading/success/error/retry).

### Phase 5: Outfit history management

- [ ] Build history list view and item card layout.
- [ ] Implement history list fetch (`GET /api/outfits/history/`).
- [ ] Implement manual history create flow only where needed.
- [ ] Implement rating/feedback edit (`PATCH /api/outfits/history/{id}/`).
- [ ] Implement delete history entry (`DELETE /api/outfits/history/{id}/`).
- [ ] Add “wear again” action mapping to existing outfit data.
- [ ] Add filters/sorting (date/rating) if within scope.
- [ ] Prevent duplicate entries caused by recommend side effects.

### Phase 6: Settings and integrations

- [ ] Build profile/settings page sections (profile, integrations, security).
- [ ] Implement current-user fetch (`GET /api/auth/me/`).
- [ ] Implement integration config read (`GET /api/integrations/config/`).
- [ ] Implement integration config update (`POST /api/integrations/config/`).
- [ ] Add safe handling for masked/optional API keys in UI.
- [ ] Wire logout action in settings and global nav.
- [ ] Add danger-zone UX copy and confirmation patterns (non-destructive unless endpoint exists).

### Phase 7: Cross-cutting quality (accessibility, performance, resilience)

- [ ] Verify semantic labels and form associations on key forms.
- [ ] Verify keyboard navigation across all interactive controls.
- [ ] Add visible focus styles and contrast checks (WCAG AA target).
- [ ] Ensure async feedback uses `aria-live` where appropriate.
- [ ] Add image lazy-loading and fixed dimensions for layout stability.
- [ ] Remove duplicate/unnecessary API calls per page load.
- [ ] Add robust error boundary patterns for network/API failures.
- [ ] Add offline/slow-network messaging for critical flows.

### Phase 8: Integration testing and acceptance

- [ ] Build endpoint smoke-test checklist from Section 4 mappings.
- [ ] Test auth lifecycle: login -> refresh -> logout -> relogin.
- [ ] Test closet CRUD and upload end-to-end with real backend.
- [ ] Test recommendation flow with valid and failing weather scenarios.
- [ ] Test history CRUD and duplicate-protection behavior.
- [ ] Test settings/integration update and persistence.
- [ ] Test ownership boundaries using two user accounts.
- [ ] Verify mobile and desktop responsiveness on target breakpoints.
- [ ] Run accessibility checks on selected required pages.
- [ ] Run Lighthouse baseline and after-optimization comparison.

### Phase 9: Submission-ready artifacts

- [ ] Capture screenshots/video snippets of all required working flows.
- [ ] Compile accessibility evidence for selected pages.
- [ ] Compile sustainability/performance before-after evidence.
- [ ] Summarize implemented Must/Should/Could with proof links.
- [ ] Record known issues and mitigations in `spec/backend_issues.md`.
- [ ] Prepare demo script aligned with coursework marking criteria.

## 12. Optional Upgrade (After Core Pass)

If time allows, add:

- client-side pagination and sorting
- skeleton loaders for async sections
- dark mode toggle (already present in wireframe concept)
- reusable modal component for add/edit/delete confirmations
