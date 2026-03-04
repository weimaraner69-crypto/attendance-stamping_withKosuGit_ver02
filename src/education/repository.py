"""教育管理ドメインのリポジトリ実装。

LearningContent、LearningProgress の CRUD 操作。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session  # noqa: TC002

from education.models import ProgressStatus  # noqa: TC001
from education.tables import LearningContentTable, LearningProgressTable
from shared.repository import Repository


class LearningContentRepository(Repository[LearningContentTable]):
    """学習コンテンツリポジトリ。"""

    def __init__(self, session: Session) -> None:
        """初期化。

        Args:
            session: SQLAlchemy セッション
        """
        super().__init__(session, LearningContentTable)

    def get_by_id(self, content_id: str) -> LearningContentTable | None:
        """ID で検索。

        Args:
            content_id: 検索対象のコンテンツ ID

        Returns:
            見つかったレコード、なければ None
        """
        stmt = select(self._table_class).where(self._table_class.content_id == content_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def list_by_category(self, category: str) -> list[LearningContentTable]:
        """カテゴリで検索。

        Args:
            category: 検索対象のカテゴリ

        Returns:
            マッチしたレコード一覧
        """
        stmt = select(self._table_class).where(self._table_class.category == category)
        return list(self._session.execute(stmt).scalars().all())

    def list_active(self) -> list[LearningContentTable]:
        """アクティブなコンテンツのみ取得。

        Returns:
            アクティブなレコード一覧
        """
        stmt = select(self._table_class).where(self._table_class.is_active == 1)
        return list(self._session.execute(stmt).scalars().all())

    def delete(self, content_id: str) -> bool:
        """ID で削除。

        Args:
            content_id: 削除対象のコンテンツ ID

        Returns:
            削除成功時は True、失敗時は False
        """
        return super().delete(content_id)

    def _get_pk_column(self) -> Any:
        """プライマリキーカラムを取得。

        Returns:
            content_id カラム
        """
        return self._table_class.content_id


class LearningProgressRepository(Repository[LearningProgressTable]):
    """学習進捗リポジトリ。"""

    def __init__(self, session: Session) -> None:
        """初期化。

        Args:
            session: SQLAlchemy セッション
        """
        super().__init__(session, LearningProgressTable)

    def get_by_id(self, progress_id: str) -> LearningProgressTable | None:
        """ID で検索。

        Args:
            progress_id: 検索対象の進捗 ID

        Returns:
            見つかったレコード、なければ None
        """
        stmt = select(self._table_class).where(self._table_class.progress_id == progress_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def list_by_employee(self, employee_id: str) -> list[LearningProgressTable]:
        """従業員 ID で検索。

        Args:
            employee_id: 従業員 ID

        Returns:
            マッチしたレコード一覧
        """
        stmt = select(self._table_class).where(self._table_class.employee_id == employee_id)
        return list(self._session.execute(stmt).scalars().all())

    def list_by_status(self, status: ProgressStatus) -> list[LearningProgressTable]:
        """ステータスで検索。

        Args:
            status: 検索対象のステータス

        Returns:
            マッチしたレコード一覧
        """
        stmt = select(self._table_class).where(self._table_class.status == status)
        return list(self._session.execute(stmt).scalars().all())

    def list_by_content(self, content_id: str) -> list[LearningProgressTable]:
        """コンテンツ ID で検索。

        Args:
            content_id: 検索対象のコンテンツ ID

        Returns:
            マッチしたレコード一覧
        """
        stmt = select(self._table_class).where(self._table_class.content_id == content_id)
        return list(self._session.execute(stmt).scalars().all())

    def delete(self, progress_id: str) -> bool:
        """ID で削除。

        Args:
            progress_id: 削除対象の進捗 ID

        Returns:
            削除成功時は True、失敗時は False
        """
        return super().delete(progress_id)

    def _get_pk_column(self) -> Any:
        """プライマリキーカラムを取得。

        Returns:
            progress_id カラム
        """
        return self._table_class.progress_id
