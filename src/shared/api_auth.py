"""API 層向け認証・認可アダプタ。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from shared.error_handling import (
    PUBLIC_INTERNAL_ERROR_MESSAGE,
    PUBLIC_VALIDATION_ERROR_MESSAGE,
)
from shared.exceptions import AuthenticationError, AuthorizationError, ValidationError
from shared.rbac import require_permission

if TYPE_CHECKING:
    from shared.auth import AuthContext


@dataclass(frozen=True)
class ApiErrorResponse:
    """API エラーレスポンス情報。"""

    status_code: int
    message: str


def authorize_api_request(
    context: AuthContext | None,
    *,
    resource: str,
    action: str,
) -> AuthContext:
    """API リクエストの認証・認可を実行する。"""
    return require_permission(context, resource=resource, action=action)


def to_api_error_response(error: Exception) -> ApiErrorResponse:
    """認証・認可例外を API レスポンス形式へ変換する。"""
    if isinstance(error, AuthenticationError):
        return ApiErrorResponse(status_code=401, message=str(error))

    if isinstance(error, AuthorizationError):
        return ApiErrorResponse(status_code=403, message=str(error))

    if isinstance(error, ValidationError):
        return ApiErrorResponse(status_code=400, message=PUBLIC_VALIDATION_ERROR_MESSAGE)

    return ApiErrorResponse(
        status_code=500,
        message=PUBLIC_INTERNAL_ERROR_MESSAGE,
    )
