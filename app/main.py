import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import post_to_all

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Automated Multi-Platform Posting API",
    description=(
        "Publishes a short message across multiple third-party platforms "
        "(Dev.to, Telegram, Mastodon, Discord, Pastebin) through their REST APIs."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── Global validation-error handler (returns clean JSON, not 422 detail) ─────
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = [
        {"field": " → ".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Automated Multi-Platform Posting API is running."}


@app.post(
    "/posting",
    response_model=PostingResponse,
    summary="Post a message to all configured platforms",
    tags=["Posting"],
    responses={
        200: {"description": "Posting attempted; check per-platform results."},
        422: {"description": "Input validation failed."},
    },
)
async def posting(request: PostingRequest) -> PostingResponse:
    """
    Accepts a **message** (≤ 200 chars, exactly one CTA URL) and publishes it
    across every configured platform concurrently.

    - If a platform's credentials are missing or the API call fails, that
      platform returns `status: "failed"` and the others continue.
    - `success` at the top level is `true` if **at least one** platform succeeded.
    """
    logger.info("Received posting request: %s", request.message[:60])
    return await post_to_all(request.message)
