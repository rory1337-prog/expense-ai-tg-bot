from unittest.mock import AsyncMock, Mock, mock_open, patch

import httpx
import pytest

from ai import ai_parse_photo, ai_parse_question


@pytest.mark.asyncio
async def test_ai_parse_photo_returns_none_on_timeout():
    with (
        patch("builtins.open", mock_open(read_data=b"image")),
        patch("ai.httpx.AsyncClient") as client_mock,
    ):
        client = AsyncMock()
        client.post.side_effect = httpx.TimeoutException("timeout")
        client_mock.return_value.__aenter__.return_value = client

        result = await ai_parse_photo("receipt.jpg")

    assert result is None


@pytest.mark.asyncio
async def test_ai_parse_photo_returns_none_on_invalid_json():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "output": [
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": "not-json",
                    }
                ]
            }
        ]
    }

    with (
        patch("builtins.open", mock_open(read_data=b"image")),
        patch("ai.httpx.AsyncClient") as client_mock,
    ):
        client = AsyncMock()
        client.post.return_value = response
        client_mock.return_value.__aenter__.return_value = client

        result = await ai_parse_photo("receipt.jpg")

    assert result is None


@pytest.mark.asyncio
async def test_ai_parse_photo_returns_none_without_output_text():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"output": []}

    with (
        patch("builtins.open", mock_open(read_data=b"image")),
        patch("ai.httpx.AsyncClient") as client_mock,
    ):
        client = AsyncMock()
        client.post.return_value = response
        client_mock.return_value.__aenter__.return_value = client

        result = await ai_parse_photo("receipt.jpg")

    assert result is None


@pytest.mark.asyncio
async def test_ai_parse_question_returns_fallback_on_timeout():
    with patch("ai.httpx.AsyncClient") as client_mock:
        client = AsyncMock()
        client.post.side_effect = httpx.TimeoutException("timeout")
        client_mock.return_value.__aenter__.return_value = client

        result = await ai_parse_question("How much did I spend?")

    assert result == {
        "intent": "unknown",
        "period": "month",
        "language": "en",
        "category": None,
    }
