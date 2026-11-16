"""
Telegram platform integration.

API docs: https://core.telegram.org/bots/api#sendmessage
Endpoint : POST https://api.telegram.org/bot<token>/sendMessage
Auth     : bot token embedded in the URL path
Public   : messages sent to a public channel are publicly visible
"""
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class TelegramPlatform(BasePlatform):
    name = "Telegram"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not configured.",
            )

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, json=payload)

            data = response.json()

            if response.status_code == 200 and data.get("ok"):
                result = data.get("result", {})
                message_id = result.get("message_id")
                # Build a public URL only for public @username channels
                chat = result.get("chat", {})
                username = chat.get("username")
                if username and message_id:
                    posted_url = f"https://t.me/{username}/{message_id}"
                    public = True
                else:
                    posted_url = None
                    public = False

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=posted_url,
                    public_access=public,
                    date=date_str,
                    time=time_str,
                    error=None,
                )
            else:
                error_desc = data.get("description", response.text[:200])
                return PlatformResult(
                    platform=self.name,
                    status="failed",
                    posted_url=None,
                    public_access=False,
                    date=None,
                    time=None,
                    error=f"HTTP {response.status_code}: {error_desc}",
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
