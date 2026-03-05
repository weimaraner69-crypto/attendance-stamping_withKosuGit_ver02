"""shared ドメインのデータベーステーブルモデル。"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text

from shared.database import Base


class AuditLogTable(Base):
    """監査ログテーブル。"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    actor_user_id = Column(String(100), nullable=False, index=True)
    actor_role = Column(String(50), nullable=False, index=True)
    resource = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    result = Column(String(20), nullable=False, index=True)
    occurred_at = Column(DateTime, nullable=False, index=True)
    target_resource_id = Column(String(255), nullable=True)
    error_type = Column(String(100), nullable=True)
    metadata_json = Column(Text, nullable=False, default="{}")


class CspReportTable(Base):
    """CSP違反レポート受信テーブル。"""

    __tablename__ = "csp_reports"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    occurred_at = Column(DateTime, nullable=False, index=True)
    document_uri = Column(String(2048), nullable=True)
    violated_directive = Column(String(255), nullable=True, index=True)
    effective_directive = Column(String(255), nullable=True)
    blocked_uri = Column(String(2048), nullable=True)
    original_policy = Column(Text, nullable=True)
    disposition = Column(String(32), nullable=True)
    referrer = Column(String(2048), nullable=True)
    status_code = Column(Integer, nullable=True)
    report_json = Column(Text, nullable=False, default="{}")
