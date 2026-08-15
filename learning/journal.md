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


### 2026-08-15 — 🐛 BUG — API HTML responses + Dashboard empty despite JSON

**Context**: After same-origin Vercel `/api` proxy deploy, login worked but Dashboard showed "No Data" while Network showed dashboard JSON with categories. Some XHR rows showed document/HTML icons.

**Problem/Trigger**:
1. Paths with trailing slashes (`/api/v1/statements/`, `/api/v1/transactions/?…`) did not match Vercel rewrite and fell through to SPA `index.html` (200 HTML).
2. Paths without trailing slash were proxied, but FastAPI `redirect_slashes` issued **307** to absolute `https://…onrender.com/…/` (wrong host behind proxy).
3. Dashboard used `Promise.all([dashboard, transactions])` — transactions HTML parse failure aborted the whole batch, so good dashboard JSON was never `setState`’d.

**Resolution**:
1. `vercel.json` → `routes` with `/api/(.*)` → Render (captures trailing slashes).
2. FastAPI `redirect_slashes=False` + dual `""`/`"/"` list routes.
3. FE: drop trailing slashes; fix `/transactions?query` URL; reject `text/html` responses in API client.
4. Dashboard: `Promise.allSettled` + treat categories/total_expenses as `hasData` fallback.

**Lesson**: Never let one dependent fetch wipe sibling success (`allSettled`). For Vercel→external API proxies, trailing-slash + framework redirects are a common footgun.

**Affected Files**: `frontend/vercel.json`, `frontend/src/services/api.ts`, `frontend/src/pages/Dashboard.tsx`, `backend/app/main.py`, `backend/app/api/v1/statements.py`, `backend/app/api/v1/transactions.py`, `backend/app/api/v1/categories.py`

**Frontend Impact**: Dashboard renders when analytics JSON succeeds even if transactions temporarily fail; collection endpoints no longer receive HTML.

