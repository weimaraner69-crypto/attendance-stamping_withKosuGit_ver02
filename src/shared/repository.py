"""汎用リポジトリベースクラス。

ORM テーブルに対する CRUD 操作の共通インターフェースを定義。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session  # noqa: TC002

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """リポジトリの汎用ベースクラス。

    CRUD 操作の標準インターフェースを提供する。
    """

    def __init__(self, session: Session, table_class: type[T]) -> None:
        """初期化。

        Args:
            session: SQLAlchemy セッション
            table_class: ORM テーブルクラス
        """
        self._session = session
        self._table_class = table_class

    def create(self, entity: T) -> T:
        """新規レコード作成。

        Args:
            entity: 作成するエンティティ

        Returns:
            作成されたエンティティ（ID を含む）
        """
        self._session.add(entity)
        self._session.flush()
        return entity

    def get_by_id(self, entity_id: Any) -> T | None:
        """ID で検索。

        Args:
            entity_id: 検索対象の ID

        Returns:
            見つかったエンティティ、なければ None
        """
        pk_col = self._get_pk_column()
        stmt = select(self._table_class).where(pk_col == entity_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def list_all(self, limit: int | None = None, offset: int = 0) -> list[T]:
        """すべてのレコードを取得。

        Args:
            limit: 最大取得数
            offset: オフセット

        Returns:
            レコード一覧
        """
        stmt = select(self._table_class).offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return list(self._session.execute(stmt).scalars().all())

    def update(self, entity: T) -> T:
        """レコード更新。

        Args:
            entity: 更新するエンティティ

        Returns:
            更新されたエンティティ
        """
        self._session.merge(entity)
        self._session.flush()
        return entity

    def delete(self, entity_id: Any) -> bool:
        """レコード削除。

        Args:
            entity_id: 削除対象の ID

        Returns:
            削除成功時は True、失敗時は False
        """
        entity = self.get_by_id(entity_id)
        if entity is None:
            return False
        self._session.delete(entity)
        self._session.flush()
        return True

    def delete_entity(self, entity: T) -> bool:
        """エンティティオブジェクトで削除。

        Args:
            entity: 削除するエンティティ

        Returns:
            常に True
        """
        self._session.delete(entity)
        self._session.flush()
        return True

    @abstractmethod
    def _get_pk_column(self) -> Any:
        """プライマリキーカラムを取得。

        テーブルクラスの id 以外の PK を使用する場合に実装。

        Returns:
            プライマリキーカラム
        """
        pass
