"""セキュリティ設定モジュールのテスト。"""

from __future__ import annotations

import pytest

from shared.security_config import build_security_headers, get_security_runtime_config


def test_get_security_runtime_config_デフォルト値() -> None:
    """環境変数未指定時は初期確定値が適用される。"""
    config = get_security_runtime_config()

    assert config.trust_x_forwarded_proto is True
    assert config.cookie.secure is True
    assert config.cookie.http_only is True
    assert config.cookie.same_site == "Lax"
    assert config.cookie.session_ttl_seconds == 12 * 60 * 60
    assert config.cookie.idle_timeout_seconds == 120 * 60
    assert config.security_headers.x_content_type_options == "nosniff"
    assert config.security_headers.x_frame_options == "DENY"
    assert config.security_headers.referrer_policy == "strict-origin-when-cross-origin"
    assert config.security_headers.csp_report_only_enabled is True
    assert config.security_headers.csp_report_uri == "/csp-report"
    assert config.oauth_callback_paths == ("/auth/google/callback", "/auth/line/callback")
    assert config.key_rotation_days == 90

    headers = build_security_headers(config)

    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy-Report-Only" in headers
    assert "report-uri /csp-report" in headers["Content-Security-Policy-Report-Only"]


def test_get_security_runtime_config_環境変数上書き(monkeypatch: pytest.MonkeyPatch) -> None:
    """環境変数で設定を上書きできる。"""
    monkeypatch.setenv("TRUST_X_FORWARDED_PROTO", "true")
    monkeypatch.setenv("COOKIE_SECURE", "true")
    monkeypatch.setenv("COOKIE_HTTP_ONLY", "true")
    monkeypatch.setenv("COOKIE_SAMESITE", "Strict")
    monkeypatch.setenv("SESSION_TTL_HOURS", "8")
    monkeypatch.setenv("IDLE_TIMEOUT_MINUTES", "60")
    monkeypatch.setenv("SECURITY_HEADER_X_FRAME_OPTIONS", "SAMEORIGIN")
    monkeypatch.setenv("SECURITY_HEADER_REFERRER_POLICY", "no-referrer")
    monkeypatch.setenv("CSP_REPORT_ONLY_ENABLED", "false")
    monkeypatch.setenv("OAUTH_CALLBACK_PATHS", "/auth/google/callback,/auth/line/callback")
    monkeypatch.setenv("KEY_ROTATION_DAYS", "30")

    config = get_security_runtime_config()

    assert config.cookie.same_site == "Strict"
    assert config.cookie.session_ttl_seconds == 8 * 60 * 60
    assert config.cookie.idle_timeout_seconds == 60 * 60
    assert config.security_headers.x_frame_options == "SAMEORIGIN"
    assert config.security_headers.referrer_policy == "no-referrer"
    assert config.security_headers.csp_report_only_enabled is False
    assert config.key_rotation_days == 30

    headers = build_security_headers(config)

    assert headers["X-Frame-Options"] == "SAMEORIGIN"
    assert headers["Referrer-Policy"] == "no-referrer"
    assert "Content-Security-Policy-Report-Only" not in headers


def test_get_security_runtime_config_same_site不正値でエラー(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SameSite が不正値ならエラー。"""
    monkeypatch.setenv("COOKIE_SAMESITE", "Invalid")

    with pytest.raises(ValueError, match="COOKIE_SAMESITE"):
        get_security_runtime_config()


def test_get_security_runtime_config_x_frame_options不正値でエラー(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """X-Frame-Options が不正値ならエラー。"""
    monkeypatch.setenv("SECURITY_HEADER_X_FRAME_OPTIONS", "ALLOWALL")

    with pytest.raises(ValueError, match="SECURITY_HEADER_X_FRAME_OPTIONS"):
        get_security_runtime_config()


def test_get_security_runtime_config_referrer_policy不正値でエラー(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Referrer-Policy が不正値ならエラー。"""
    monkeypatch.setenv("SECURITY_HEADER_REFERRER_POLICY", "invalid-policy")

    with pytest.raises(ValueError, match="SECURITY_HEADER_REFERRER_POLICY"):
        get_security_runtime_config()


def test_get_security_runtime_config_oauth_path不正でエラー(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OAuth パスが '/' で始まらない場合はエラー。"""
    monkeypatch.setenv("OAUTH_CALLBACK_PATHS", "auth/google/callback")

    with pytest.raises(ValueError, match="OAUTH_CALLBACK_PATHS"):
        get_security_runtime_config()


def test_get_security_runtime_config_idleがttl超過でエラー(monkeypatch: pytest.MonkeyPatch) -> None:
    """アイドルタイムアウトがTTLを超える場合はエラー。"""
    monkeypatch.setenv("SESSION_TTL_HOURS", "1")
    monkeypatch.setenv("IDLE_TIMEOUT_MINUTES", "120")

    with pytest.raises(ValueError, match="idle_timeout_seconds"):
        get_security_runtime_config()
