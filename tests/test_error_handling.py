"""共通エラーハンドリングのテスト。"""

from __future__ import annotations

import logging

from shared.error_handling import build_internal_error_payload, sanitize_error_detail


def test_sanitize_error_detail_機微情報をマスキング() -> None:
    """エラー詳細のメール・トークン・パスワードをマスキングする。"""
    detail = "email=test@example.com token=abc123 password=hunter2"

    sanitized = sanitize_error_detail(detail)

    assert "test@example.com" not in sanitized
    assert "abc123" not in sanitized
    assert "hunter2" not in sanitized
    assert "[masked-email]" in sanitized
    assert "token=[masked]" in sanitized
    assert "password=[masked]" in sanitized


def test_build_internal_error_payload_contextもマスキング() -> None:
    """context情報にもマスキングが適用される。"""
    error = RuntimeError("token=abc123")

    payload = build_internal_error_payload(
        error,
        context={
            "resource": "sales",
            "note": "password=secret",
        },
    )

    assert payload["error_type"] == "RuntimeError"
    assert payload["detail"] == "token=[masked]"
    assert payload["context_resource"] == "sales"
    assert payload["context_note"] == "password=[masked]"
    assert payload["detail"] != "token=abc123"


def test_log_internal_error_ログ出力がマスキングされる(caplog) -> None:
    """内部エラーログに機微情報が残らない。"""
    from shared.error_handling import log_internal_error

    logger_name = "shared.error_handling.test"
    caplog.set_level(logging.ERROR, logger=logger_name)

    log_internal_error(
        RuntimeError("email=test@example.com password=secret"),
        context={"resource": "sales"},
        logger_name=logger_name,
    )

    logged = "\n".join(message for message in caplog.messages)
    assert "test@example.com" not in logged
    assert "password=secret" not in logged
    assert "[masked-email]" in logged
    assert "password=[masked]" in logged
