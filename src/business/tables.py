"""業務管理ドメインのデータベーステーブルモデル。

日報・売上・人件費・原価管理のテーブル定義。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.sql import func

from business.models import ReportStatus
from shared.database import Base


class DailyReportTable(Base):
    """日報テーブル"""

    __tablename__ = "daily_reports"

    # プライマリキー
    report_id = Column(String(50), primary_key=True, index=True)

    # 基本情報
    employee_id = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    content = Column(Text, nullable=False)
    status = Column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.DRAFT)  # type: ignore[var-annotated]
    work_hours = Column(Numeric(8, 2), nullable=False)
    notes = Column(Text, nullable=True)

    # メタデータ
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class SalesRecordTable(Base):
    """売上記録テーブル"""

    __tablename__ = "sales_records"

    # プライマリキー
    record_id = Column(String(50), primary_key=True, index=True)

    # 基本情報
    date = Column(DateTime, nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    customer_name = Column(String(100), nullable=False)
    product_name = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)

    # メタデータ
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class LaborCostTable(Base):
    """人件費テーブル"""

    __tablename__ = "labor_costs"

    # プライマリキー
    labor_cost_id = Column(String(50), primary_key=True, index=True)

    # 基本情報
    employee_id = Column(String(50), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    hourly_rate = Column(Numeric(8, 2), nullable=False)
    total_hours = Column(Numeric(8, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)

    # メタデータ
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
