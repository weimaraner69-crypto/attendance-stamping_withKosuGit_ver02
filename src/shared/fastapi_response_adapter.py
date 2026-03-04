"""ApiResponse を FastAPI 応答へ変換するアダプタ。"""

from __future__ import annotations

import importlib.util
from typing import TYPE_CHECKING, Any

from shared.http_response_adapter import HttpResponseEnvelope, adapt_api_response_to_http

if TYPE_CHECKING:
    from shared.api_handlers import ApiResponse


def _is_fastapi_available() -> bool:
    """FastAPI 依存が導入済みか判定する。"""
    try:
        return importlib.util.find_spec("fastapi") is not None
    except ModuleNotFoundError:
        return False


def build_fastapi_response(envelope: HttpResponseEnvelope) -> Any:
    """HTTP 応答データを FastAPI の JSONResponse へ変換する。"""
    if not _is_fastapi_available():
        raise RuntimeError(
            "fastapi がインストールされていません。`pip install '.[web]'` を実行してください"
        )

    from fastapi.responses import JSONResponse  # type: ignore[import-not-found]

    response = JSONResponse(status_code=envelope.status_code, content=envelope.body)
    for header in envelope.headers:
        response.headers.append(header.name, header.value)

    return response


def adapt_api_response_to_fastapi(api_response: ApiResponse) -> Any:
    """ApiResponse を FastAPI 応答へ変換する。"""
    envelope = adapt_api_response_to_http(api_response)
    return build_fastapi_response(envelope)
