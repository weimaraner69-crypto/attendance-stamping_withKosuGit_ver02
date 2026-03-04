"""主要セキュリティ要件の回帰テスト。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attendance.api import get_attendance_summary_sample
from business.api import export_sales_data
from shared.audit import sanitize_audit_metadata
from shared.auth import GENERIC_AUTH_ERROR_MESSAGE, AuthContext
from shared.auth_endpoints import GENERIC_LOCKOUT_ERROR_MESSAGE, login_with_password
from shared.csrf import create_csrf_token
from shared.login_protection import InMemoryLoginProtection, LoginProtectionConfig
from shared.security import User

if TYPE_CHECKING:
    from collections.abc import Mapping


def test_security_regression_未認証アクセスは401() -> None:
    """未認証アクセス時は 401 を返す。"""
    response = get_attendance_summary_sample(None)

    assert response.status_code == 401
    assert response.body["ok"] is False


def test_security_regression_権限外エクスポートは403() -> None:
    """権限外の売上エクスポートは 403 を返す。"""

    def sales_exporter(_: AuthContext) -> Mapping[str, Any]:
        return {
            "export_id": "export-001",
            "resource": "sales",
            "datasets": ["sales"],
            "executed_by": "user_001",
        }

    context = AuthContext(user_id="user_001", role="manager", is_active=True)
    csrf_token = create_csrf_token()

    response = export_sales_data(
        context,
        method="POST",
        csrf_header_token=csrf_token,
        csrf_cookie_token=csrf_token,
        sales_exporter=sales_exporter,
    )

    assert response.status_code == 403
    assert response.body["ok"] is False


def test_security_regression_csrf不備は403() -> None:
    """更新系で CSRF トークン不備の場合は 403 を返す。"""

    def sales_exporter(_: AuthContext) -> Mapping[str, Any]:
        return {
            "export_id": "export-001",
            "resource": "sales",
            "datasets": ["sales"],
            "executed_by": "user_001",
        }

    context = AuthContext(user_id="user_001", role="tax_accountant", is_active=True)
    csrf_token = create_csrf_token()

    response = export_sales_data(
        context,
        method="POST",
        csrf_header_token=None,
        csrf_cookie_token=csrf_token,
        sales_exporter=sales_exporter,
    )

    assert response.status_code == 403
    assert response.body["ok"] is False


def test_security_regression_認証cookie属性が統一される() -> None:
    """ログイン成功時にセッションCookie属性が統一される。"""

    def authenticate(username: str, password: str) -> User | None:
        if username == "john_doe" and password == "password":
            return User(user_id="user_001", username="john_doe", role="manager", is_active=True)
        return None

    response = login_with_password(
        request_scheme="https",
        request_headers={},
        username="john_doe",
        password="password",
        authenticate=authenticate,
    )

    assert response.status_code == 200
    assert len(response.set_cookies) == 1
    cookie = response.set_cookies[0]
    assert cookie.secure is True
    assert cookie.http_only is True
    assert cookie.same_site == "Lax"


def test_security_regression_ログイン失敗閾値超過で429() -> None:
    """ログイン失敗が閾値を超えると 429 を返す。"""

    def authenticate(_: str, __: str) -> User | None:
        return None

    protection = InMemoryLoginProtection(
        config=LoginProtectionConfig(max_failed_attempts=2, lock_minutes=15),
    )

    first_response = login_with_password(
        request_scheme="https",
        request_headers={},
        username="john_doe",
        password="wrong",
        authenticate=authenticate,
        login_protection=protection,
    )
    second_response = login_with_password(
        request_scheme="https",
        request_headers={},
        username="john_doe",
        password="wrong",
        authenticate=authenticate,
        login_protection=protection,
    )
    locked_response = login_with_password(
        request_scheme="https",
        request_headers={},
        username="john_doe",
        password="wrong",
        authenticate=authenticate,
        login_protection=protection,
    )

    assert first_response.status_code == 401
    assert first_response.body["error"] == GENERIC_AUTH_ERROR_MESSAGE
    assert second_response.status_code == 401
    assert second_response.body["error"] == GENERIC_AUTH_ERROR_MESSAGE
    assert locked_response.status_code == 429
    assert locked_response.body["error"] == GENERIC_LOCKOUT_ERROR_MESSAGE


def test_security_regression_監査メタデータから機微情報を除外() -> None:
    """監査メタデータから機微情報キーを除外する。"""
    metadata = {
        "target_id": "report-001",
        "email": "secret@example.com",
        "token": "token-001",
    }

    sanitized = sanitize_audit_metadata(metadata)

    assert sanitized == {"target_id": "report-001"}
