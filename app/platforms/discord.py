"""
Discord platform integration via Incoming Webhook.

Docs    : https://discord.com/developers/docs/resources/webhook#execute-webhook
Endpoint: POST <webhook_url>
Auth    : Webhook URL contains the token — no separate auth header needed
Public  : Messages in a public channel are visible to all server members
"""
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DiscordPlatform(BasePlatform):
    name = "Discord"

    async def post(self, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        if not settings.DISCORD_WEBHOOK_URL:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="DISCORD_WEBHOOK_URL is not configured.",
            )

        # ?wait=true makes Discord return the created message object
        # so we can build a direct link to it
        url = settings.DISCORD_WEBHOOK_URL.rstrip("/") + "?wait=true"

        payload = {
            "content": message,
            "username": "Automated Posting Bot",
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, json=payload)

            if response.status_code in (200, 204):
                data = response.json() if response.status_code == 200 else {}
                # Build a direct message link if we have the IDs
                channel_id = data.get("channel_id")
                message_id = data.get("id")
                if channel_id and message_id:
                    # Discord message links need the guild (server) ID too;
                    # we can extract it from the webhook URL
                    # URL format: .../webhooks/<application_id>/<token>
                    posted_url = f"https://discord.com/channels/@me/{channel_id}/{message_id}"
                else:
                    posted_url = None

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=posted_url,
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
