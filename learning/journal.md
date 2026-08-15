# Learning Journal

### 2026-08-15 — 🐛 BUG — Custom domain login Failed to fetch

**Context**: Deployed FE on Vercel (`txnnova.byakshendra.in`), BE on Render, custom GoDaddy domain. Login showed "Failed to fetch" with provisional headers to `api.txnnova.byakshendra.in`.

**Problem/Trigger**: Browser could not reliably reach the API subdomain. DNS for `api.txnnova.byakshendra.in` was configured (CNAME → Render) and worked via public resolvers / Node, but local/router DNS was flaky. CORS itself was already correct for `https://txnnova.byakshendra.in`. Refresh cookies were also missing `Secure` because Render `ENVIRONMENT` defaulted to `development`.

**Resolution**:
1. Proxy `/api/*` through Vercel to Render so the browser only talks to `txnnova.byakshendra.in` (same-origin).
2. Set production `VITE_API_URL=/api/v1` (`.env.production` + Vercel env must match).
3. Harden refresh cookie (`Secure` outside development, explicit `path=/`).
4. Restore session via `/auth/refresh` instead of speculative `/auth/me`.

**Lesson**: For Vercel FE + Render BE, prefer same-origin `/api` rewrites over a separate `api.*` custom domain. Custom API DNS adds failure modes that surface as opaque `Failed to fetch`, not CORS errors.

**Affected Files**: `frontend/vercel.json`, `frontend/.env.production`, `frontend/.env.example`, `frontend/src/services/api.ts`, `frontend/src/contexts/AuthContext.tsx`, `backend/app/api/v1/auth.py`, `backend/.env.example`

**Frontend Impact**: Login/register no longer depend on `api.txnnova.byakshendra.in` resolving in the user's browser.

