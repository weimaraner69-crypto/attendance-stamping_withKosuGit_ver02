"""SQLAlchemy ORM ベースクラス。

すべてのドメインモデルはこの Base を継承する。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM ベースクラス。

    SQLAlchemy 2.0 の DeclarativeBase を継承。
    すべてのモデルクラスはこれを継承する。
    """

    pass
