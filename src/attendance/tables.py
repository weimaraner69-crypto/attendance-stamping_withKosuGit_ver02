"""勤怠管理ドメインのデータベーステーブルモデル。

出退勤記録・シフト管理のテーブル定義。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.sql import func

from attendance.models import AttendanceStatus, ShiftType
from shared.database import Base


class AttendanceRecordTable(Base):
    """出退勤記録テーブル"""

    __tablename__ = "attendance_records"

    # プライマリキー
    record_id = Column(String(50), primary_key=True, index=True)

    # 基本情報
    employee_id = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    check_in_time = Column(DateTime, nullable=False)
    check_out_time = Column(DateTime, nullable=True)
    status = Column(SQLEnum(AttendanceStatus), nullable=False)  # type: ignore[var-annotated]
    notes = Column(Text, nullable=True)

    # メタデータ
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class ShiftScheduleTable(Base):
    """シフトスケジュールテーブル"""

    __tablename__ = "shift_schedules"

    # プライマリキー
    shift_id = Column(String(50), primary_key=True, index=True)

    # 基本情報
    employee_id = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    shift_type = Column(SQLEnum(ShiftType), nullable=False)  # type: ignore[var-annotated]
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_fixed = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)

    # メタデータ
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
