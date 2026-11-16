"""
Pastebin platform integration.

API docs: https://pastebin.com/doc_api
Endpoint : POST https://pastebin.com/api/api_post.php
Auth     : api_dev_key (Developer API key from pastebin.com account)
Public   : api_paste_private=0 means public paste
"""
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult

PASTEBIN_API_URL = "https://pastebin.com/api/api_post.php"


class PastebinPlatform(BasePlatform):
    name = "Pastebin"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        if not settings.PASTEBIN_API_KEY:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="PASTEBIN_API_KEY is not configured.",
            )

        payload = {
            "api_dev_key": settings.PASTEBIN_API_KEY,
            "api_option": "paste",
            "api_paste_code": message,
            "api_paste_name": "Automated Post",
            "api_paste_format": "text",
            "api_paste_private": "0",    # 0 = public
            "api_paste_expire_date": "1M",  # expire after 1 month
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(PASTEBIN_API_URL, data=payload)

            # Pastebin returns plain text: either a URL or "Bad API request, ..."
            text = response.text.strip()

            if response.status_code == 200 and text.startswith("https://pastebin.com/"):
                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=text,
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
                    error=f"HTTP {response.status_code}: {text[:200]}",
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
