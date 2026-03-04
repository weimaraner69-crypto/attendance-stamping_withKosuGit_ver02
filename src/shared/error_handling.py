"""共通エラーハンドリング。"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


PUBLIC_INTERNAL_ERROR_MESSAGE = "処理に失敗しました。時間をおいて再度お試しください"
PUBLIC_VALIDATION_ERROR_MESSAGE = "入力内容を確認してください"

_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)(password|passwd|token|secret|api[_-]?key|authorization)\s*[:=]\s*[^,\s]+"
)


def sanitize_error_detail(detail: str) -> str:
    """内部エラー詳細から機微情報をマスキングする。"""
    masked = _EMAIL_PATTERN.sub("[masked-email]", detail)
    masked = _SECRET_ASSIGNMENT_PATTERN.sub(r"\g<1>=[masked]", masked)
    if len(masked) > 500:
        return masked[:500] + "..."
    return masked


def build_internal_error_payload(
    error: Exception,
    *,
    context: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """内部ログ向けのエラーペイロードを構築する。"""
    payload = {
        "error_type": type(error).__name__,
        "detail": sanitize_error_detail(str(error)),
    }

    if context is not None:
        for key, value in context.items():
            payload[f"context_{key}"] = sanitize_error_detail(value)

    return payload


def log_internal_error(
    error: Exception,
    *,
    context: Mapping[str, str] | None = None,
    logger_name: str = "shared.error_handling",
) -> None:
    """内部詳細をマスキングしてログ出力する。"""
    logger = logging.getLogger(logger_name)
    payload = build_internal_error_payload(error, context=context)
    logger.error("内部エラー: %s", payload)
