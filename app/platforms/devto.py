"""
Dev.to platform integration.

API docs: https://developers.forem.com/api/v1#tag/articles/operation/createArticle
Endpoint : POST https://dev.to/api/articles
Auth     : header  api-key: <token>
"""
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DevToPlatform(BasePlatform):
    name = "Dev.to"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        if not settings.DEVTO_API_KEY:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="DEVTO_API_KEY is not configured.",
            )

        payload = {
            "article": {
                "title": message[:100],       # title is required; use first 100 chars
                "body_markdown": message,
                "published": True,
                "tags": ["announcement"],
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "https://dev.to/api/articles",
                    json=payload,
                    headers={
                        "api-key": settings.DEVTO_API_KEY,
                        "Content-Type": "application/json",
                    },
                )

            if response.status_code in (200, 201):
                data = response.json()
                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=data.get("url"),
                    public_access=True,
                    date=date_str,
                    time=time_str,
                    error=None,
                )
            else:
                return PlatformResult(
                    platform=self.name,
                    status="failed",
                    posted_url=None,
                    public_access=False,
                    date=None,
                    time=None,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                )

        except Exception as exc:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error=str(exc),
            )
