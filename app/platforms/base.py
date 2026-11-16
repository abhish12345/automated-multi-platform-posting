from abc import ABC, abstractmethod
from app.schemas import PlatformResult


class BasePlatform(ABC):
    """
    Every platform adapter inherits from this class and implements `post`.
    The method must NEVER raise — it catches its own exceptions and
    returns a PlatformResult with status="failed".
    """

    name: str = "Unknown"

    @abstractmethod
    async def post(self, message: str) -> PlatformResult:
        """Publish *message* and return a structured result."""
        ...
