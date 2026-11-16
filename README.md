# Automated Multi-Platform Posting System

A **FastAPI** application that publishes a short message to **5 third-party platforms** concurrently through their REST APIs.

---

## Supported Platforms

| # | Platform | API Type | Auth |
|---|----------|----------|------|
| 1 | **Dev.to** | REST | API Key header |
| 2 | **Telegram** | Bot REST | Bot Token |
| 3 | **Mastodon** | REST | OAuth Bearer Token |
| 4 | **Discord** | Incoming Webhook | Webhook URL |
| 5 | **Pastebin** | REST | Developer API Key |

---

## Project Structure

```
automated-posting/
│
├── app/
│   ├── main.py                  # FastAPI app & /posting endpoint
│   ├── schemas.py               # Pydantic models + input validation
│   ├── config.py                # Settings loaded from .env
│   ├── platforms/
│   │   ├── base.py              # Abstract BasePlatform class
│   │   ├── devto.py             # Dev.to integration
│   │   ├── telegram.py          # Telegram Bot integration
│   │   ├── mastodon.py          # Mastodon integration
│   │   ├── discord.py           # Discord Webhook integration
│   │   └── pastebin.py          # Pastebin integration
│   └── services/
│       └── posting_service.py   # Runs all platforms concurrently
│
├── docs/
│   └── sample_logs.md           # Real API logs and sample responses
├── tests/
│   └── test_posting.py          # Pytest test suite
│
├── .env.example                 # Template — copy to .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone / enter the project

```bash
cd automated-posting
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

```bash
cp .env.example .env
# Then edit .env and fill in your API keys
```

**Where to get each key:**

| Platform | Where to get credentials |
|----------|--------------------------|
| Dev.to | [dev.to/settings/extensions](https://dev.to/settings/extensions) → Generate API Key |
| Telegram | Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token; add bot to your channel as Admin |
| Mastodon | Instance Settings → Development → New Application (scope: `write:statuses`) |
| Discord | Server → Channel Settings → Integrations → Webhooks → New Webhook → Copy URL |
| Pastebin | [pastebin.com/doc_api](https://pastebin.com/doc_api) → Your Unique Developer API Key |

### 5. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

### 6. Open the interactive API docs

```
http://localhost:4000/docs
```

---

## API Reference

### `POST /posting`

Publishes a message to all configured platforms concurrently.

#### Request body

```json
{
  "message": "Check out our latest business platform. https://example.com"
}
```

#### Validation rules

| Rule | Detail |
|------|--------|
| Max length | 200 characters |
| CTA link | Exactly one `http://` or `https://` URL required |
| URL format | Must be a valid URL |

#### Example — success

```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out our latest platform and grow your visibility. https://example.com"}'
```

```json
{
  "success": true,
  "results": [
    {
      "platform": "Dev.to",
      "status": "success",
      "posted_url": "https://dev.to/abhishek_pandey/check-out-our-latest-business-platform-and-grow-your-online-visibility-httpsdxoracom-1nh2",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:02:35",
      "error": null
    },
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/dxora_tech_notifications/3",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:02:36",
      "error": null
    },
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@abhishek_pandey/117627431062486277",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:02:36",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": "https://discord.com/channels/@me/1509562483990593636/1571948628350738584",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:02:37",
      "error": null
    },
    {
      "platform": "Pastebin",
      "status": "success",
      "posted_url": "https://pastebin.com/E1vbV0dW",
      "public_access": true,
      "date": "2026-11-16",
      "time": "18:02:37",
      "error": null
    }
  ]
}
```

#### Example — validation error (message too long)

```json
{
  "detail": [
    {
      "field": "message",
      "message": "Value error, Message must not exceed 200 characters (got 215)."
    }
  ]
}
```

#### Example — validation error (no link)

```json
{
  "detail": [
    {
      "field": "message",
      "message": "Value error, Message must contain exactly one CTA link."
    }
  ]
}
```

> See [`docs/sample_logs.md`](docs/sample_logs.md) for complete real API logs and all validation error examples.

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output:

```
tests/test_posting.py::test_valid_message_accepted       PASSED
tests/test_posting.py::test_message_too_long             PASSED
tests/test_posting.py::test_message_no_url               PASSED
tests/test_posting.py::test_message_multiple_urls        PASSED
tests/test_posting.py::test_invalid_url                  PASSED
tests/test_posting.py::test_empty_message                PASSED
tests/test_posting.py::test_response_structure           PASSED
tests/test_posting.py::test_success_false_when_all_fail  PASSED
tests/test_posting.py::test_health_check                 PASSED
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| `asyncio.gather` for all platforms | Posts concurrently — total latency ≈ slowest single platform, not sum of all |
| Each platform catches its own exceptions | One failure never blocks the others |
| `BasePlatform` abstract class | Adding a new platform requires only a new file + one line in `posting_service.py` |
| `pydantic-settings` for config | Type-safe, auto-reads `.env`, never accidentally leaks secrets into code |
| `httpx.AsyncClient` | Native async HTTP, compatible with FastAPI's async runtime |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEVTO_API_KEY` | Yes (Dev.to) | Dev.to personal API key |
| `TELEGRAM_BOT_TOKEN` | Yes (Telegram) | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes (Telegram) | Channel username e.g. `@mychannel` |
| `MASTODON_ACCESS_TOKEN` | Yes (Mastodon) | OAuth access token with write:statuses scope |
| `MASTODON_INSTANCE_URL` | No | Defaults to `https://mastodon.social` |
| `DISCORD_WEBHOOK_URL` | Yes (Discord) | Full webhook URL from channel integrations |
| `PASTEBIN_API_KEY` | Yes (Pastebin) | Developer API key from pastebin.com |

> Any platform whose credentials are missing returns `status: "failed"` with a clear error message; the rest continue normally.
