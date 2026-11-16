import re
from pydantic import BaseModel, field_validator
from typing import Optional

URL_REGEX = re.compile(
    r"https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}(?:\.\d{1,3}){3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class PostingRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        # 1. Length check
        if len(v) > 200:
            raise ValueError(
                f"Message must not exceed 200 characters (got {len(v)})."
            )

        # 2. Extract all URLs from the message
        words = v.split()
        urls = [w for w in words if re.match(r"https?://\S+", w, re.IGNORECASE)]

        if len(urls) == 0:
            raise ValueError("Message must contain exactly one CTA link.")
        if len(urls) > 1:
            raise ValueError(
                f"Message must contain exactly one CTA link (found {len(urls)})."
            )

        # 3. Validate the single URL format
        url = urls[0].rstrip(".,;!?)")  # strip trailing punctuation
        if not URL_REGEX.match(url):
            raise ValueError(f"The URL '{url}' is not valid.")

        return v


class PlatformResult(BaseModel):
    platform: str
    status: str                    # "success" | "failed"
    posted_url: Optional[str]
    public_access: bool
    date: Optional[str]
    time: Optional[str]
    error: Optional[str]


class PostingResponse(BaseModel):
    success: bool
    results: list[PlatformResult]
