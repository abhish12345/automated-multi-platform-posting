"""
Unit and integration tests for the /posting endpoint.

Run with:
    pytest tests/ -v
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app
from app.schemas import PlatformResult


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def valid_message():
    return "Check out our latest business platform. https://example.com"


@pytest.fixture
def mock_success_result():
    return PlatformResult(
        platform="MockPlatform",
        status="success",
        posted_url="https://example.com/post/1",
        public_access=True,
        date="2026-11-16",
        time="10:00:00",
        error=None,
    )


@pytest.fixture
def mock_failed_result():
    return PlatformResult(
        platform="MockPlatform",
        status="failed",
        posted_url=None,
        public_access=False,
        date="2026-11-16",
        time="10:00:00",
        error="Authentication failed",
    )


# ── Validation tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_valid_message_accepted(valid_message, mock_success_result):
    with patch(
        "app.main.post_to_all",
        new=AsyncMock(return_value=type("R", (), {
            "success": True,
            "results": [mock_success_result],
            "model_dump": lambda self: {
                "success": True,
                "results": [mock_success_result.model_dump()]
            }
        })()),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/posting", json={"message": valid_message})
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_message_too_long():
    long_msg = "A" * 190 + " https://example.com/path"  # > 200 chars
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/posting", json={"message": long_msg})
    assert resp.status_code == 422
    body = resp.json()
    assert any("200" in str(e) for e in body["detail"])


@pytest.mark.asyncio
async def test_message_no_url():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/posting", json={"message": "No link here at all"})
    assert resp.status_code == 422
    body = resp.json()
    assert any("link" in str(e).lower() for e in body["detail"])


@pytest.mark.asyncio
async def test_message_multiple_urls():
    msg = "Visit https://example.com and also https://another.com"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/posting", json={"message": msg})
    assert resp.status_code == 422
    body = resp.json()
    assert any("link" in str(e).lower() for e in body["detail"])


@pytest.mark.asyncio
async def test_invalid_url():
    msg = "Check this out at http://not a valid url here"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/posting", json={"message": msg})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_empty_message():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/posting", json={"message": ""})
    assert resp.status_code == 422


# ── Response structure tests ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_response_structure(valid_message, mock_success_result, mock_failed_result):
    from app.schemas import PostingResponse
    mock_response = PostingResponse(
        success=True,
        results=[mock_success_result, mock_failed_result],
    )

    with patch("app.main.post_to_all", new=AsyncMock(return_value=mock_response)):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/posting", json={"message": valid_message})

    assert resp.status_code == 200
    body = resp.json()
    assert "success" in body
    assert "results" in body
    assert isinstance(body["results"], list)

    result_keys = {"platform", "status", "posted_url", "public_access", "date", "time", "error"}
    for r in body["results"]:
        assert result_keys.issubset(r.keys()), f"Missing keys in result: {r}"


@pytest.mark.asyncio
async def test_success_false_when_all_fail(valid_message, mock_failed_result):
    from app.schemas import PostingResponse
    mock_response = PostingResponse(success=False, results=[mock_failed_result])

    with patch("app.main.post_to_all", new=AsyncMock(return_value=mock_response)):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/posting", json={"message": valid_message})

    assert resp.status_code == 200
    assert resp.json()["success"] is False


# ── Health check ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
