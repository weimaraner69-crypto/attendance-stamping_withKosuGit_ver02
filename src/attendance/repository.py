"""出勤管理ドメインのリポジトリ実装。

AttendanceRecord、ShiftSchedule の CRUD 操作。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session  # noqa: TC002

from attendance.models import AttendanceStatus, ShiftType  # noqa: TC001
from attendance.tables import AttendanceRecordTable, ShiftScheduleTable
from shared.repository import Repository


class AttendanceRecordRepository(Repository[AttendanceRecordTable]):
    """出勤記録リポジトリ。"""

    def __init__(self, session: Session) -> None:
        """初期化。

        Args:
            session: SQLAlchemy セッション
        """
        super().__init__(session, AttendanceRecordTable)

    def get_by_id(self, record_id: str) -> AttendanceRecordTable | None:
        """ID で検索。

        Args:
            record_id: 検索対象の記録 ID

        Returns:
            見つかったレコード、なければ None
        """
        stmt = select(self._table_class).where(
            self._table_class.record_id == record_id
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list_by_employee(self, employee_id: str) -> list[AttendanceRecordTable]:
        """従業員 ID で検索。

        Args:
            employee_id: 従業員 ID

        Returns:
            マッチしたレコード一覧
        """
        stmt = select(self._table_class).where(
            self._table_class.employee_id == employee_id
        )
        return list(self._session.execute(stmt).scalars().all())

    def list_by_status(
        self, status: AttendanceStatus
    ) -> list[AttendanceRecordTable]:
        """ステータスで検索。

        Args:
            status: 検索対象のステータス

        Returns:
            マッチしたレコード一覧
        """
        stmt = select(self._table_class).where(
            self._table_class.status == status
        )
        return list(self._session.execute(stmt).scalars().all())

    def delete(self, record_id: str) -> bool:
        """ID で削除。

        Args:
            record_id: 削除対象の記録 ID

        Returns:
            削除成功時は True、失敗時は False
        """
        return super().delete(record_id)

    def _get_pk_column(self) -> Any:
        """プライマリキーカラムを取得。

        Returns:
            record_id カラム
        """
        return self._table_class.record_id


class ShiftScheduleRepository(Repository[ShiftScheduleTable]):
    """シフトスケジュールリポジトリ。"""

    def __init__(self, session: Session) -> None:
        """初期化。

        Args:
            session: SQLAlchemy セッション
        """
        super().__init__(session, ShiftScheduleTable)

    def get_by_id(self, shift_id: str) -> ShiftScheduleTable | None:
        """ID で検索。

        Args:
            shift_id: 検索対象のシフト ID

        Returns:
            見つかったレコード、なければ None
        """
        stmt = select(self._table_class).where(
            self._table_class.shift_id == shift_id
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list_by_employee(self, employee_id: str) -> list[ShiftScheduleTable]:
        """従業員 ID で検索。

        Args:
            employee_id: 従業員 ID

        Returns:
            マッチしたレコード一覧
        """
        stmt = select(self._table_class).where(
            self._table_class.employee_id == employee_id
        )
        return list(self._session.execute(stmt).scalars().all())

    def list_by_shift_type(self, shift_type: ShiftType) -> list[ShiftScheduleTable]:
        """シフトタイプで検索。

        Args:
            shift_type: 検索対象のシフトタイプ

        Returns:
            マッチしたレコード一覧
        """
        stmt = select(self._table_class).where(
            self._table_class.shift_type == shift_type
        )
        return list(self._session.execute(stmt).scalars().all())

    def delete(self, shift_id: str) -> bool:
        """ID で削除。

        Args:
            shift_id: 削除対象のシフト ID

        Returns:
            削除成功時は True、失敗時は False
        """
        return super().delete(shift_id)

    def _get_pk_column(self) -> Any:
        """プライマリキーカラムを取得。

        Returns:
            shift_id カラム
        """
        return self._table_class.shift_id
