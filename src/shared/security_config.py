"""セキュリティ設定値の共通定義。"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_CSP_REPORT_ONLY_POLICY = (
    "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; "
    "form-action 'self'; object-src 'none'"
)


def _parse_bool(value: str | None, *, default: bool, setting_name: str) -> bool:
    """環境変数から真偽値を読み取る。"""
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(f"{setting_name} は真偽値で指定してください")


def _parse_positive_int(value: str | None, *, default: int, setting_name: str) -> int:
    """環境変数から正の整数を読み取る。"""
    if value is None:
        return default

    try:
        parsed = int(value)
    except ValueError as error:
        raise ValueError(f"{setting_name} は整数で指定してください") from error

    if parsed <= 0:
        raise ValueError(f"{setting_name} は正の整数である必要があります")
    return parsed


def _ensure_safe_header_value(value: str, *, setting_name: str) -> str:
    """ヘッダー値に改行が含まれないことを検証する。"""
    if "\r" in value or "\n" in value:
        raise ValueError(f"{setting_name} に改行は指定できません")
    return value


def _normalize_same_site(value: str | None) -> str:
    """SameSite 設定値を正規化する。"""
    if value is None:
        return "Lax"

    normalized = value.strip().capitalize()
    if normalized not in {"Lax", "Strict", "None"}:
        raise ValueError("COOKIE_SAMESITE は Lax / Strict / None のいずれかで指定してください")
    return normalized


def _normalize_x_content_type_options(value: str | None) -> str:
    """X-Content-Type-Options 設定値を正規化する。"""
    if value is None:
        return "nosniff"

    normalized = value.strip().lower()
    normalized = _ensure_safe_header_value(
        normalized,
        setting_name="SECURITY_HEADER_X_CONTENT_TYPE_OPTIONS",
    )
    if normalized != "nosniff":
        raise ValueError("SECURITY_HEADER_X_CONTENT_TYPE_OPTIONS は nosniff のみ指定できます")
    return normalized


def _normalize_x_frame_options(value: str | None) -> str:
    """X-Frame-Options 設定値を正規化する。"""
    if value is None:
        return "DENY"

    normalized = value.strip().upper()
    normalized = _ensure_safe_header_value(
        normalized,
        setting_name="SECURITY_HEADER_X_FRAME_OPTIONS",
    )
    if normalized not in {"DENY", "SAMEORIGIN"}:
        raise ValueError(
            "SECURITY_HEADER_X_FRAME_OPTIONS は DENY / SAMEORIGIN のいずれかで指定してください"
        )
    return normalized


def _normalize_referrer_policy(value: str | None) -> str:
    """Referrer-Policy 設定値を正規化する。"""
    if value is None:
        return "strict-origin-when-cross-origin"

    normalized = value.strip().lower()
    normalized = _ensure_safe_header_value(
        normalized,
        setting_name="SECURITY_HEADER_REFERRER_POLICY",
    )
    allowed = {
        "no-referrer",
        "no-referrer-when-downgrade",
        "origin",
        "origin-when-cross-origin",
        "same-origin",
        "strict-origin",
        "strict-origin-when-cross-origin",
        "unsafe-url",
    }
    if normalized not in allowed:
        raise ValueError("SECURITY_HEADER_REFERRER_POLICY の値が不正です")
    return normalized


def _parse_csp_report_uri(value: str | None) -> str:
    """CSP レポート送信先を読み取る。"""
    report_uri = (value or "/csp-report").strip()
    report_uri = _ensure_safe_header_value(report_uri, setting_name="CSP_REPORT_URI")

    if not report_uri:
        raise ValueError("CSP_REPORT_URI は空文字を指定できません")
    if report_uri.startswith("/") or report_uri.startswith("https://"):
        return report_uri

    raise ValueError("CSP_REPORT_URI は '/' または 'https://' で始まる必要があります")


def _parse_csp_report_only_policy(value: str | None) -> str:
    """CSP report-only ポリシーを読み取る。"""
    policy = (value or DEFAULT_CSP_REPORT_ONLY_POLICY).strip()
    policy = _ensure_safe_header_value(policy, setting_name="CSP_REPORT_ONLY_POLICY")

    if not policy:
        raise ValueError("CSP_REPORT_ONLY_POLICY は空文字を指定できません")
    return policy


def _has_csp_report_uri_directive(policy: str) -> bool:
    """CSP ポリシーに report-uri が含まれるか判定する。"""
    return "report-uri " in policy.lower()


def _parse_oauth_callback_paths(value: str | None) -> tuple[str, ...]:
    """OAuth コールバック対象パスを読み取る。"""
    raw_value = value or "/auth/google/callback,/auth/line/callback"
    paths = tuple(path.strip() for path in raw_value.split(",") if path.strip())

    if not paths:
        raise ValueError("OAUTH_CALLBACK_PATHS は1つ以上指定する必要があります")

    for path in paths:
        if not path.startswith("/"):
            raise ValueError("OAUTH_CALLBACK_PATHS の各パスは '/' で始まる必要があります")

    return paths


@dataclass(frozen=True)
class CookieSettings:
    """認証Cookie設定。"""

    secure: bool
    http_only: bool
    same_site: str
    session_ttl_seconds: int
    idle_timeout_seconds: int

    def __post_init__(self) -> None:
        """不変条件の検証。"""
        if self.same_site not in {"Lax", "Strict", "None"}:
            raise ValueError("same_site は Lax / Strict / None のいずれかである必要があります")
        if self.session_ttl_seconds <= 0:
            raise ValueError("session_ttl_seconds は正の値である必要があります")
        if self.idle_timeout_seconds <= 0:
            raise ValueError("idle_timeout_seconds は正の値である必要があります")
        if self.idle_timeout_seconds > self.session_ttl_seconds:
            raise ValueError("idle_timeout_seconds は session_ttl_seconds 以下である必要があります")


@dataclass(frozen=True)
class SecurityHeaderSettings:
    """セキュリティヘッダー設定。"""

    x_content_type_options: str
    x_frame_options: str
    referrer_policy: str
    csp_report_only_enabled: bool
    csp_report_only_policy: str
    csp_report_uri: str

    def __post_init__(self) -> None:
        """不変条件の検証。"""
        if self.x_content_type_options != "nosniff":
            raise ValueError("x_content_type_options は nosniff である必要があります")
        if self.x_frame_options not in {"DENY", "SAMEORIGIN"}:
            raise ValueError("x_frame_options は DENY / SAMEORIGIN のいずれかである必要があります")
        if not self.referrer_policy:
            raise ValueError("referrer_policy は必須です")
        if not self.csp_report_only_policy:
            raise ValueError("csp_report_only_policy は必須です")
        if not self.csp_report_uri:
            raise ValueError("csp_report_uri は必須です")


@dataclass(frozen=True)
class SecurityRuntimeConfig:
    """SEC-001 で利用する実行時セキュリティ設定。"""

    trust_x_forwarded_proto: bool
    cookie: CookieSettings
    security_headers: SecurityHeaderSettings
    oauth_callback_paths: tuple[str, ...]
    key_rotation_days: int

    def __post_init__(self) -> None:
        """不変条件の検証。"""
        if not self.oauth_callback_paths:
            raise ValueError("oauth_callback_paths は1つ以上必要です")
        if self.key_rotation_days <= 0:
            raise ValueError("key_rotation_days は正の値である必要があります")


def get_security_runtime_config() -> SecurityRuntimeConfig:
    """環境変数から SEC-001 用の設定を構築する。"""
    trust_x_forwarded_proto = _parse_bool(
        os.getenv("TRUST_X_FORWARDED_PROTO"),
        default=True,
        setting_name="TRUST_X_FORWARDED_PROTO",
    )

    cookie_secure = _parse_bool(
        os.getenv("COOKIE_SECURE"),
        default=True,
        setting_name="COOKIE_SECURE",
    )
    cookie_http_only = _parse_bool(
        os.getenv("COOKIE_HTTP_ONLY"),
        default=True,
        setting_name="COOKIE_HTTP_ONLY",
    )
    cookie_same_site = _normalize_same_site(os.getenv("COOKIE_SAMESITE"))

    session_ttl_hours = _parse_positive_int(
        os.getenv("SESSION_TTL_HOURS"),
        default=12,
        setting_name="SESSION_TTL_HOURS",
    )
    idle_timeout_minutes = _parse_positive_int(
        os.getenv("IDLE_TIMEOUT_MINUTES"),
        default=120,
        setting_name="IDLE_TIMEOUT_MINUTES",
    )
    key_rotation_days = _parse_positive_int(
        os.getenv("KEY_ROTATION_DAYS"),
        default=90,
        setting_name="KEY_ROTATION_DAYS",
    )

    cookie_settings = CookieSettings(
        secure=cookie_secure,
        http_only=cookie_http_only,
        same_site=cookie_same_site,
        session_ttl_seconds=session_ttl_hours * 60 * 60,
        idle_timeout_seconds=idle_timeout_minutes * 60,
    )

    security_headers = SecurityHeaderSettings(
        x_content_type_options=_normalize_x_content_type_options(
            os.getenv("SECURITY_HEADER_X_CONTENT_TYPE_OPTIONS")
        ),
        x_frame_options=_normalize_x_frame_options(os.getenv("SECURITY_HEADER_X_FRAME_OPTIONS")),
        referrer_policy=_normalize_referrer_policy(os.getenv("SECURITY_HEADER_REFERRER_POLICY")),
        csp_report_only_enabled=_parse_bool(
            os.getenv("CSP_REPORT_ONLY_ENABLED"),
            default=True,
            setting_name="CSP_REPORT_ONLY_ENABLED",
        ),
        csp_report_only_policy=_parse_csp_report_only_policy(os.getenv("CSP_REPORT_ONLY_POLICY")),
        csp_report_uri=_parse_csp_report_uri(os.getenv("CSP_REPORT_URI")),
    )

    callback_paths = _parse_oauth_callback_paths(os.getenv("OAUTH_CALLBACK_PATHS"))

    return SecurityRuntimeConfig(
        trust_x_forwarded_proto=trust_x_forwarded_proto,
        cookie=cookie_settings,
        security_headers=security_headers,
        oauth_callback_paths=callback_paths,
        key_rotation_days=key_rotation_days,
    )


def build_security_headers(config: SecurityRuntimeConfig) -> dict[str, str]:
    """レスポンスへ付与するセキュリティヘッダーを構築する。"""
    headers = {
        "X-Content-Type-Options": config.security_headers.x_content_type_options,
        "X-Frame-Options": config.security_headers.x_frame_options,
        "Referrer-Policy": config.security_headers.referrer_policy,
    }

    if config.security_headers.csp_report_only_enabled:
        csp_policy = config.security_headers.csp_report_only_policy
        if not _has_csp_report_uri_directive(csp_policy):
            csp_policy = f"{csp_policy}; report-uri {config.security_headers.csp_report_uri}"
        headers["Content-Security-Policy-Report-Only"] = csp_policy

    return headers
