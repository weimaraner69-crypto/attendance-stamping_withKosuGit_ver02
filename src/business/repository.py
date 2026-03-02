"""業務管理ドメインのリポジトリ実装。

DailyReport、SalesRecord、LaborCost の CRUD 操作。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session  # noqa: TC002

from business.models import ReportStatus  # noqa: TC001
from business.tables import DailyReportTable, LaborCostTable, SalesRecordTable
from shared.repository import Repository


class DailyReportRepository(Repository[DailyReportTable]):
    """日報リポジトリ。"""

    def __init__(self, session: Session) -> None:
        """初期化。

        Args:
            session: SQLAlchemy セッション
        """
        super().__init__(session, DailyReportTable)

    def get_by_id(self, report_id: str) -> DailyReportTable | None:
        """ID で検索。

        Args:
            report_id: 検索対象のレポート ID

        Returns:
            見つかったレコード、なければ None
        """
        stmt = select(self._table_class).where(
            self._table_class.report_id == report_id
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list_by_employee(self, employee_id: str) -> list[DailyReportTable]:
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

    def list_by_status(self, status: ReportStatus) -> list[DailyReportTable]:
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

    def delete(self, report_id: str) -> bool:
        """ID で削除。

        Args:
            report_id: 削除対象のレポート ID

        Returns:
            削除成功時は True、失敗時は False
        """
        return super().delete(report_id)

    def _get_pk_column(self) -> Any:
        """プライマリキーカラムを取得。

        Returns:
            report_id カラム
        """
        return self._table_class.report_id


class SalesRecordRepository(Repository[SalesRecordTable]):
    """売上記録リポジトリ。"""

    def __init__(self, session: Session) -> None:
        """初期化。

        Args:
            session: SQLAlchemy セッション
        """
        super().__init__(session, SalesRecordTable)

    def get_by_id(self, record_id: str) -> SalesRecordTable | None:
        """ID で検索。

        Args:
            record_id: 検索対象のレコード ID

        Returns:
            見つかったレコード、なければ None
        """
        stmt = select(self._table_class).where(
            self._table_class.record_id == record_id
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def delete(self, record_id: str) -> bool:
        """ID で削除。

        Args:
            record_id: 削除対象のレコード ID

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


class LaborCostRepository(Repository[LaborCostTable]):
    """給与コストリポジトリ。"""

    def __init__(self, session: Session) -> None:
        """初期化。

        Args:
            session: SQLAlchemy セッション
        """
        super().__init__(session, LaborCostTable)

    def get_by_id(self, labor_cost_id: str) -> LaborCostTable | None:
        """ID で検索。

        Args:
            labor_cost_id: 検索対象のコスト ID

        Returns:
            見つかったレコード、なければ None
        """
        stmt = select(self._table_class).where(
            self._table_class.labor_cost_id == labor_cost_id
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list_by_employee(self, employee_id: str) -> list[LaborCostTable]:
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

    def delete(self, labor_cost_id: str) -> bool:
        """ID で削除。

        Args:
            labor_cost_id: 削除対象のコスト ID

        Returns:
            削除成功時は True、失敗時は False
        """
        return super().delete(labor_cost_id)

    def _get_pk_column(self) -> Any:
        """プライマリキーカラムを取得。

        Returns:
            labor_cost_id カラム
        """
        return self._table_class.labor_cost_id
