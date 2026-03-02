"""データベース接続管理モジュール。

SQLite への接続、セッション管理、初期化処理を提供。
"""

from __future__ import annotations

import os
from collections.abc import Generator  # noqa: TC003
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from shared.database.base import Base

# データベースファイルのパス
DB_DIR = Path(__file__).parent.parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "attendance.db"

# SQLite 接続文字列
DATABASE_URL = f"sqlite:///{DB_PATH}"

# エンジン作成（lazy initialization）
_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """SQLAlchemy エンジンを取得（シングルトン）。

    Returns:
        sqlalchemy.Engine: データベースエンジン

    Raises:
        RuntimeError: init_db() を先に呼び出す必要がある場合
    """
    global _engine
    if _engine is None:
        raise RuntimeError(
            "データベースが初期化されていません。"
            "アプリケーション起動時に init_db() を呼び出してください。"
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """SQLAlchemy セッションファクトリを取得（シングルトン）。

    Returns:
        sessionmaker: セッションファクトリ

    Raises:
        RuntimeError: init_db() を先に呼び出す必要がある場合
    """
    global _SessionLocal
    if _SessionLocal is None:
        raise RuntimeError(
            "データベースが初期化されていません。"
            "アプリケーション起動時に init_db() を呼び出してください。"
        )
    return _SessionLocal


def init_db() -> None:
    """データベース接続を初期化し、テーブルを作成する。

    本関数はアプリケーション起動時に1回のみ呼び出す必要がある。

    例::

        from shared.database import init_db
        init_db()
    """
    global _engine, _SessionLocal

    # SQLite エンジン作成
    # echo=True にするとSQL文をログ出力する（開発時便利）
    _engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("SQL_ECHO", "False").lower() == "true",
        connect_args={"check_same_thread": False},  # SQLite 用
    )

    # セッションファクトリ作成
    _SessionLocal = sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    # テーブルを作成
    Base.metadata.create_all(bind=_engine)


SessionLocal = sessionmaker(bind=None)  # dummy（init_db() で上書きされる）


def get_db_session() -> Generator[Session, None, None]:
    """データベースセッションを取得（ジェネレータ）。

    FastAPI の Depends で使用するための関数。
    with ブロックを抜ける際に自動的にクローズ・ロールバックされる。

    Yields:
        sqlalchemy.orm.Session: データベースセッション

    例::

        from fastapi import Depends
        from shared.database import get_db_session

        @app.get("/items/")
        def list_items(db: Session = Depends(get_db_session)):
            ...
    """
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
