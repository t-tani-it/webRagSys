# -*- coding: utf-8 -*-
"""src/db/database.py - DB接続管理.

Why: 接続生成を一元化し、APIから再利用するため。
What: engine、SessionLocal、get_db、init_dbを提供する。
Assumption / Dependencies: SQLAlchemy、pgvector（Postgres時のみ）。
I/O: 入力=DATABASE_URL、出力=Session。
Caution: APIキー等の直書き禁止。LIKE検索でSQL組立しないこと。
Future Work: コネクションプール調整。
Change Log: 2026-09-19 初版作成。
"""

import os
from collections.abc import Generator

from sqlalchemy import text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import get_settings

settings = get_settings()

# 設定値ブロック（冒頭集約）
# 解説：環境変数DATABASE_URL優先。本番はPostgres、ドライバ欠落時はSQLiteに退避する。
DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url)


def _create_engine():
    """環境に応じたengineを生成する。"""
    from sqlalchemy import create_engine as _ce

    url = DATABASE_URL
    if url.startswith("postgresql"):
        try:
            import psycopg2  # noqa: F401 解説：存在確認のみ。

            return _ce(url)
        except ImportError:
            # 解説：テスト環境等でPGドライバなしでも起動できるよう退避する。
            url = "sqlite:///./app.db"
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return _ce(url, connect_args=connect_args)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """DBセッションを供給する。

    Yields:
        Session: DBセッション。

    Side Effects:
        セッションを開閉する。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """テーブル初期化とpgvector拡張有効化。

    Side Effects:
        テーブル作成、拡張作成（Postgres時のみ）。
    """
    from src.db import models  # noqa: F401 解説：テーブル登録のため遅延importする。

    # 解説：URL文字列ではなく実engineの方言で判定する（SQLite退避時は拡張不要）。
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
