# Frontend-Backend Smoke Checklist

## Prerequisites

- Backend running at `http://127.0.0.1:8000`
- At least 2 test users (user A, user B)
- OpenRouter environment variables configured for wardrobe analysis and OOTD generation if needed

## Endpoint checks

- [x] `POST /api/auth/user/register/`
- [x] `POST /api/auth/user/login/`
- [x] `GET /api/auth/me/`
- [x] `POST /api/auth/refresh/`
- [x] `POST /api/auth/logout/`
- [x] `GET /api/wardrobe/items/`
- [x] `POST /api/wardrobe/items/`
- [x] `PATCH /api/wardrobe/items/{id}/`
- [x] `DELETE /api/wardrobe/items/{id}/`
- [x] `POST /api/wardrobe/items/upload/`
- [x] `POST /api/outfits/recommend/`
- [x] `GET /api/outfits/history/`
- [x] `POST /api/outfits/history/`
- [x] `PATCH /api/outfits/history/{id}/`
- [x] `DELETE /api/outfits/history/{id}/`
- [x] `GET /api/integrations/config/`
- [x] `POST /api/integrations/config/`

## Frontend flows

- [x] Login and redirect
- [x] Token refresh on 401
- [x] Closet CRUD
- [x] Upload and fallback to manual create
- [x] OOTD generation and auto-history behavior
- [x] History edit/delete
- [x] Settings fetch/update/logout
- [x] Route guard and unauthorized redirect
