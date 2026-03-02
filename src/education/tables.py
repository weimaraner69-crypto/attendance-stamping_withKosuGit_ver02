"""教育管理ドメインのデータベーステーブルモデル。

学習コンテンツ・進捗管理のテーブル定義。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.sql import func

from education.models import ProgressStatus
from shared.database import Base


class LearningContentTable(Base):
    """学習コンテンツテーブル"""

    __tablename__ = "learning_contents"

    # プライマリキー
    content_id = Column(String(50), primary_key=True, index=True)

    # 基本情報
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    created_by = Column(String(50), nullable=False)
    is_active = Column(Integer, nullable=False, default=1)

    # メタデータ
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class LearningProgressTable(Base):
    """学習進捗テーブル"""

    __tablename__ = "learning_progress"

    # プライマリキー
    progress_id = Column(String(50), primary_key=True, index=True)

    # 基本情報
    employee_id = Column(String(50), nullable=False, index=True)
    content_id = Column(String(50), nullable=False, index=True)
    status = Column(SQLEnum(ProgressStatus), nullable=False)  # type: ignore[var-annotated]
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)

    # メタデータ
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
