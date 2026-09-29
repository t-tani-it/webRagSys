# -*- coding: utf-8 -*-
"""tests/test_backends.py - 4パターン backend 検証.

Why: fake/ollama × sqlite/postgres の組合せを検証するため。
What: SQLiteはpytest内、PostgreSQLは設定を分離した子プロセスでE2E検証する。
Assumption / Dependencies: pytest、Ollama任意、Postgres任意（不可時はskip）。
I/O: 入力=API呼出／設定切替、出力=検証結果。
Caution: 本番DBを汚さない。Ollama実測は遅延あり。
Future Work: CI用PostgreSQL＋pgvectorサービスへの接続。
Change Log: 2026-09-29 PostgreSQLケースを子プロセスE2Eに変更。
"""

import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from config import get_settings


def _ollama_available() -> bool:
    """Ollama到達可否を返す。"""
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen("http://localhost:11434/", timeout=3) as res:
            return res.status == 200
    except (OSError, urllib.error.URLError):
        return False


def _pg_available() -> bool:
    """Postgres到達可否を返す（TEST_DATABASE_URL必須）。"""
    from sqlalchemy.exc import SQLAlchemyError

    url = os.getenv("TEST_DATABASE_URL", "")
    if not url.startswith("postgresql"):
        return False
    try:
        engine = create_engine(url, connect_args={"connect_timeout": 3})
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False
    finally:
        if "engine" in locals():
            engine.dispose()


def _pg_vector_available() -> bool:
    """pgvector拡張の有無を返す。"""
    from sqlalchemy.exc import SQLAlchemyError

    url = os.getenv("TEST_DATABASE_URL", "")
    try:
        engine = create_engine(url, connect_args={"connect_timeout": 3})
        with engine.begin() as conn:
            rows = conn.execute(
                text("SELECT 1 FROM pg_available_extensions WHERE name='vector'")
            ).all()
        return len(rows) == 1
    except SQLAlchemyError:
        return False
    finally:
        if "engine" in locals():
            engine.dispose()


def _run_postgres_e2e(provider: str, embedding_dim: int) -> None:
    """専用設定の子プロセスでPostgreSQL＋pgvectorのAPI E2Eを行う。"""
    database_url = os.getenv("TEST_DATABASE_URL", "")
    database_name = make_url(database_url).database if database_url else None
    if not database_name or not database_name.lower().endswith("_test"):
        pytest.skip("安全のためTEST_DATABASE_URLのDB名は_testで終わる必要がある")

    probe = dedent(
        """
        from fastapi.testclient import TestClient
        from sqlalchemy.engine import make_url

        from config import get_settings
        from src.api.main import create_app
        from src.db.database import Base, engine, init_db

        settings = get_settings()
        assert engine.dialect.name == "postgresql"
        assert make_url(settings.database_url).database.lower().endswith("_test")
        assert settings.embedding_dim == EXPECTED_DIM

        from src.db import models  # noqa: F401
        from src.rag.embeddings import embed_texts

        assert len(embed_texts(["次元確認"])[0]) == EXPECTED_DIM
        Base.metadata.drop_all(bind=engine)
        init_db()
        try:
            with TestClient(create_app()) as client:
                created = client.post(
                    "/documents",
                    json={"title": "就業規則", "content": "年次休暇は10日付与する。"},
                )
                assert created.status_code == 201, created.text
                doc_id = created.json()["id"]
                response = client.post("/chat", json={"question": "休暇は何日ですか。"})
                assert response.status_code == 200, response.text
                body = response.json()
                assert doc_id in body["source_ids"], body
                if EXPECTED_PROVIDER == "ollama":
                    assert "FAKE回答" not in body["answer"], body
                else:
                    assert "FAKE回答" in body["answer"], body
        finally:
            Base.metadata.drop_all(bind=engine)
            engine.dispose()
        """
    ).replace("EXPECTED_DIM", str(embedding_dim)).replace(
        "EXPECTED_PROVIDER", repr(provider)
    )
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": database_url,
            "USE_FAKE": "true" if provider == "fake" else "false",
            "LLM_PROVIDER": provider,
            "EMBEDDING_DIM": str(embedding_dim),
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "qwen3.5:4b",
            "OLLAMA_EMBED_MODEL": "qwen3-embedding:0.6b",
        }
    )
    # 解説：固定テストコードを子プロセスで実行し、DB次元のimport時設定を分離する。
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", probe],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"


@pytest.fixture()
def ollama_env(monkeypatch: pytest.MonkeyPatch):
    """Ollama設定を有効化する（後片付け付き）。"""
    monkeypatch.setenv("USE_FAKE", "false")
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3.5:4b")
    monkeypatch.setenv("OLLAMA_EMBED_MODEL", "qwen3-embedding:0.6b")
    monkeypatch.setenv("EMBEDDING_DIM", "1024")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_b_fake_postgres_crud() -> None:
    """B: fake+postgresのVector列とAPI E2Eを検証する（不可時はskip）。"""
    if not _pg_available():
        pytest.skip("TEST_DATABASE_URL未設定またはPostgres到達不可")
    if not _pg_vector_available():
        pytest.skip("pgvector拡張未導入")
    _run_postgres_e2e("fake", 8)


@pytest.mark.skipif(not _ollama_available(), reason="Ollama停止中")
def test_c_ollama_sqlite_embed_search(
    ollama_env: None, tmp_path
) -> None:
    """C: ollama+sqliteのEmbeddingと検索を検証する。"""
    from sqlalchemy import create_engine as _ce

    from src.db import models  # noqa: F401 解説：テーブル登録のため。
    from src.db.database import Base
    from src.rag.embeddings import embed_texts

    vecs = embed_texts(["年次休暇は10日付与する"])
    assert len(vecs[0]) == 1024
    test_engine = _ce(
        f"sqlite:///{tmp_path}/c.db", connect_args={"check_same_thread": False}
    )
    session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)
    db = session_factory()
    try:
        from src.db.models import Document
        from src.rag import chunker, vectorstore

        doc = Document(title="C用", content="年次休暇は10日付与する")
        db.add(doc)
        db.commit()
        db.refresh(doc)
        vectorstore.save_chunks(db, doc.id, chunker.split_text(doc.content))
        hits = vectorstore.search(db, "休暇は何日")
        assert len(hits) >= 1
    finally:
        db.close()


@pytest.mark.skipif(not _ollama_available(), reason="Ollama停止中")
def test_c_ollama_sqlite_chat(ollama_env: None, tmp_path) -> None:
    """C: ollama+sqliteのchat E2Eを検証する（実LLM応答、FAKEでない）。"""
    from sqlalchemy import create_engine as _ce

    from src.api.main import create_app
    from src.db import models  # noqa: F401 解説：テーブル登録のため。
    from src.db.database import Base, get_db

    test_engine = _ce(
        f"sqlite:///{tmp_path}/chat.db", connect_args={"check_same_thread": False}
    )
    session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)
    db = session_factory()
    app = create_app()

    def override():
        yield db

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    try:
        res = client.post("/documents", json={"title": "休暇", "content": "年次休暇は10日"})
        assert res.status_code == 201
        res = client.post("/chat", json={"question": "休暇は何日?"})
        assert res.status_code == 200
        body = res.json()
        assert "FAKE回答" not in body["answer"]
        assert len(body["answer"]) > 0
    finally:
        db.close()


def test_d_ollama_postgres_e2e() -> None:
    """D: ollama+postgresのEmbedding・API E2Eを検証する（不可時はskip）。"""
    if not _pg_available():
        pytest.skip("TEST_DATABASE_URL未設定またはPostgres到達不可")
    if not _pg_vector_available():
        pytest.skip("pgvector拡張未導入のためD本格E2Eは保留")
    if not _ollama_available():
        pytest.skip("Ollama停止中")
    _run_postgres_e2e("ollama", 1024)
