"""
PostingService orchestrates concurrent posting to all registered platforms.
Each platform runs independently — a failure on one does not affect others.
"""
import asyncio
import logging

from app.platforms.base import BasePlatform
from app.platforms.devto import DevToPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.pastebin import PastebinPlatform
from app.schemas import PlatformResult, PostingResponse

logger = logging.getLogger(__name__)

# All registered platforms — add more here without touching any other file
PLATFORMS: list[BasePlatform] = [
    DevToPlatform(),
    TelegramPlatform(),
    MastodonPlatform(),
    DiscordPlatform(),
    PastebinPlatform(),
]


async def post_to_all(message: str) -> PostingResponse:
    """
    Post *message* to every platform concurrently.
    Returns a PostingResponse whose `success` field is True if at least
    one platform succeeded.
    """
    tasks = [platform.post(message) for platform in PLATFORMS]
    results: list[PlatformResult] = await asyncio.gather(*tasks)

    any_success = any(r.status == "success" for r in results)

    for result in results:
        if result.status == "success":
            logger.info("Posted to %s — %s", result.platform, result.posted_url)
        else:
            logger.warning(
                "Failed to post to %s — %s", result.platform, result.error
            )

    return PostingResponse(success=any_success, results=results)
