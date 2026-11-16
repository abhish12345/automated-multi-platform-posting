"""
Mastodon platform integration.

API docs: https://docs.joinmastodon.org/methods/statuses/
Endpoint : POST <instance>/api/v1/statuses
Auth     : Bearer token (user access token with write:statuses scope)
Public   : visibility="public" means the toot is publicly accessible
"""
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        if not settings.MASTODON_ACCESS_TOKEN:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="MASTODON_ACCESS_TOKEN is not configured.",
            )

        instance = settings.MASTODON_INSTANCE_URL.rstrip("/")
        endpoint = f"{instance}/api/v1/statuses"

        payload = {
            "status": message,
            "visibility": "public",
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    endpoint,
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {settings.MASTODON_ACCESS_TOKEN}"
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
