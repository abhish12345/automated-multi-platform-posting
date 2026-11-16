# Sample API Logs & Responses

## Server Startup

```
INFO:     Started server process [15012]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:4000 (Press CTRL+C to quit)
```

---

## Sample Request

```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out our latest business platform and grow your online visibility. https://dxora.com"}'
```

---

## Sample Response — All Platforms Success

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

---

## Sample Response — Validation Error (message too long)

**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA https://example.com/path"}'
```

**Response (422):**
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

---

## Sample Response — Validation Error (no CTA link)

**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "No link in this message at all"}'
```

**Response (422):**
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

---

## Sample Response — Validation Error (multiple links)

**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Visit https://example.com and also https://another.com"}'
```

**Response (422):**
```json
{
  "detail": [
    {
      "field": "message",
      "message": "Value error, Message must contain exactly one CTA link (found 2)."
    }
  ]
}
```

---

## Server Logs During Posting

```
2026-11-16 18:02:35  INFO     app.main — Received posting request: Check out our latest business platform and gro
2026-11-16 18:02:35  INFO     app.services.posting_service — Posted to Dev.to — https://dev.to/abhishek_pandey/...
2026-11-16 18:02:36  INFO     app.services.posting_service — Posted to Telegram — https://t.me/dxora_tech_notifications/3
2026-11-16 18:02:36  INFO     app.services.posting_service — Posted to Mastodon — https://mastodon.social/@abhishek_pandey/117627431062486277
2026-11-16 18:02:37  INFO     app.services.posting_service — Posted to Discord — https://discord.com/channels/@me/...
2026-11-16 18:02:37  INFO     app.services.posting_service — Posted to Pastebin — https://pastebin.com/E1vbV0dW
INFO:     127.0.0.1:52341 - "POST /posting HTTP/1.1" 200 OK
```
