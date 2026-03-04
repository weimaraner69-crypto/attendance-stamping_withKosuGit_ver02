"""FastAPI応答アダプタのテスト。"""

from __future__ import annotations

import pytest

from shared.api_handlers import ApiResponse
from shared.fastapi_response_adapter import (
    _is_fastapi_available,
    adapt_api_response_to_fastapi,
    build_fastapi_response,
)
from shared.http_response_adapter import HttpHeader, HttpResponseEnvelope


def test_adapt_api_response_to_fastapi_未導入時はエラー(monkeypatch: pytest.MonkeyPatch) -> None:
    """FastAPI未導入時は明示エラーを返す。"""
    monkeypatch.setattr("shared.fastapi_response_adapter._is_fastapi_available", lambda: False)

    response = ApiResponse(status_code=200, body={"ok": True}, headers={"X-Test": "value"})

    with pytest.raises(RuntimeError, match="fastapi"):
        adapt_api_response_to_fastapi(response)


def test_build_fastapi_response_導入済みなら変換できる() -> None:
    """FastAPI導入済み環境では JSONResponse へ変換できる。"""
    if not _is_fastapi_available():
        pytest.skip("fastapi 未導入のためスキップ")

    envelope = HttpResponseEnvelope(
        status_code=200,
        body={"ok": True},
        headers=(
            HttpHeader(name="X-Test", value="value"),
            HttpHeader(name="Set-Cookie", value="session_id=token; Path=/; Max-Age=10"),
        ),
    )

    response = build_fastapi_response(envelope)

    assert response.status_code == 200
    assert response.body == b'{"ok":true}'
    assert response.headers["x-test"] == "value"
    assert any(raw_header[0] == b"set-cookie" for raw_header in response.raw_headers)
