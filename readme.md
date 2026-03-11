# SmartCloset Run Guide

This project has:
- Backend: Django API in local `backend/` folder
- Frontend: static multi-page app in `frontend/`

## 1. Start Backend Service (uv)

From project root:

```bash
cd backend

# Create venv (first time only)
uv venv .venv

# Install dependencies (first time only)
uv pip install --python .venv/bin/python -r requirements.txt

# Apply migrations
uv run --python .venv/bin/python python manage.py migrate

# Start backend at http://127.0.0.1:8000
uv run --python .venv/bin/python python manage.py runserver 127.0.0.1:8000
```

## 2. Start Frontend Service

From project root:

```bash
cd frontend

# Install frontend dependencies (first time only)
npm install

# Build TypeScript to browser JS
npm run build

# Serve static files at http://127.0.0.1:5500
python3 -m http.server 5500
```

Then open:
- Frontend: `http://127.0.0.1:5500/index.html`
- Backend API: `http://127.0.0.1:8000/api/`

## 2.1 Configure DashScope

The app now uses DashScope for:

- clothing image analysis during wardrobe upload
- outfit recommendation text in the OOTD flow

Configure it by environment variables.

Recommended defaults:

```bash
DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/api/v1
DASHSCOPE_API_KEY=your_dashscope_api_key_here
TEXT_OUTPUT_MODEL=qwen3.5-flash
```

Notes:

- the selected text model must support image input if you want wardrobe image analysis to work
- if the LLM request fails during outfit recommendation, the backend returns an error instead of a fallback recommendation
- Gemini is no longer used by this project

## 3. Nginx Config (Frontend + API Reverse Proxy)

Use this server block (replace paths and domain):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    root /absolute/path/to/IT Group Work/frontend;
    index index.html;

    # Frontend pages
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API reverse proxy to Django
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Media files from Django (uploaded clothing images)
    location /media/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Optional: cache static assets
    location ~* \.(css|js|svg|png|jpg|jpeg|gif|ico|woff2?)$ {
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
        try_files $uri =404;
    }
}
```

## 4. Enable Nginx Site (Ubuntu/Debian)

```bash
sudo cp /path/to/your-site.conf /etc/nginx/sites-available/smartcloset
sudo ln -s /etc/nginx/sites-available/smartcloset /etc/nginx/sites-enabled/smartcloset
sudo nginx -t
sudo systemctl reload nginx
```

## 5. Quick Health Checks

```bash
# Backend health (auth endpoint should return 401 or 405 depending on method)
curl -i http://127.0.0.1:8000/api/auth/me/

# Frontend page
curl -I http://127.0.0.1:5500/index.html
```
