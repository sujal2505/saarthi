# Saarthi Smart Assistant — Setup Guide

## What this does

Replaces the hardcoded 4-question bot with a **Gemini-powered assistant** that:
- Reads the customer's real spending, goals, balance, and credit data from the DB
- Sends that data as context to Gemini on every message
- Returns plain-language answers personalised to *that customer's* actual numbers
- Maintains conversation history within the session

---

## Files to copy

| Generated file | Copy to |
|---|---|
| `assistant_service.py` | `apps/api/app/services/assistant.py` (overwrite) |
| `assistant_router.py` | `apps/api/app/routers/assistant.py` (overwrite) |
| `AssistantPage.tsx` | `apps/web/src/pages/AssistantPage.tsx` (overwrite) |

---

## 1 — Add your Gemini API key

In `apps/api/.env` (and `.env.example`):

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

In `apps/api/app/config.py`, make sure it is loaded:

```python
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
```

---

## 2 — Install httpx on the backend

```bash
# Inside apps/api/
pip install httpx
```

Or add to `requirements.txt`:
```
httpx>=0.27.0
```

---

## 3 — Fix the auth helper import in the router

In `assistant_router.py`, line 10:

```python
from app.lib.auth import get_current_customer_id
```

Change `app.lib.auth` and `get_current_customer_id` to match whatever your
project uses for JWT/auth. For example, if your other routers use:

```python
from app.dependencies import get_current_user
```

… then update the import and the `Depends(...)` call to match.

---

## 4 — Register the new router in main.py

Check `apps/api/app/main.py`. If the old assistant router is already included,
no change needed — you're replacing the file, not the import. But confirm:

```python
from app.routers import assistant
app.include_router(assistant.router)
```

---

## 5 — Check the frontend API client base URL

In `apps/web/src/lib/api.ts`, confirm the base URL is set to your backend:

```typescript
// Should look something like this
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  withCredentials: true,   // if you use cookie-based auth
});
```

The new chat endpoint is `POST /api/assistant/chat`.

---

## 6 — Test it

Start both backend and frontend, log in as any customer, go to
the Assistant page. Try:

- "Where am I spending the most this month?"
- "How are my goals going?"
- "Can I take a loan of ₹50,000?"
- "What's my savings rate?"

You should get answers that reference the customer's *actual numbers*,
not generic advice.

---

## How the context works

Every time a message is sent, the backend:

1. Queries the DB for that customer's last 30 transactions
2. Computes spending by category, income, expenses, savings rate
3. Loads all their goals with progress %
4. Injects all of this into the Gemini system prompt
5. Sends the full conversation history + new message to Gemini
6. Returns the reply to the frontend

Gemini sees the numbers and answers *about them* — it cannot invent
figures that don't exist in the data.

---

## Gemini model used

`gemini-2.0-flash` — fast and cost-effective for conversational tasks.
To switch to a more capable model, change the `GEMINI_URL` constant
in `assistant_service.py`:

```python
# More capable (slower, costs more)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

# Fastest / cheapest
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
```