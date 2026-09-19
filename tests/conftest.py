# -*- coding: utf-8 -*-
"""tests/conftest.py - テスト用DB設定.

Why: 本番DBを汚さずSQLiteで検証するため。
What: テスト用engineとclientを提供する。
Assumption / Dependencies: pytest、fastapi、SQLAlchemy。
I/O: 入力=なし、出力=client。
Caution: なし。
Future Work: Postgres実DBテスト追加。
Change Log: 2026-09-19 初版作成。
"""

import os
from pathlib import Path

os.environ["USE_FAKE"] = "true"

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture()
def db(tmp_path: Path) -> Generator[Session, None, None]:
    """テスト用DBセッションを返す（テストごとに独立ファイル）。

    Args:
        tmp_path: pytest一時ディレクトリ。

    Yields:
        Session: テスト用セッション。

    Side Effects:
        一時DBファイル作成。
    """
    from src.db import models  # noqa: F401 解説：create_all前にテーブル登録する。
    from src.db.database import Base

    # 解説：固定ファイル共有による間欠失敗を避けるため、テストごとに分離する。
    test_engine = create_engine(
        f"sqlite:///{tmp_path}/test.db", connect_args={"check_same_thread": False}
    )
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    """APIテスト用クライアントを返す。

    Args:
        db: テスト用セッション。

    Yields:
        TestClient: テストクライアント。
    """
    from src.api.main import create_app
    from src.db.database import get_db

    app = create_app()

    def override() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override
    return TestClient(app)
