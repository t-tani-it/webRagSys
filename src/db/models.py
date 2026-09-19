# -*- coding: utf-8 -*-
"""src/db/models.py - 文書テーブル定義.

Why: 文書とRAG用チャンクの保存先を定義するため。
What: documents、document_chunksを提供する。
Assumption / Dependencies: SQLAlchemy、pgvector（Postgres時のみVector型）。
I/O: 入力=Python属性、出力=DB行。
Caution: embedding列はPostgresではVector、SQLiteではJSON代替とする。
Future Work: カテゴリ・会話履歴テーブル追加。
Change Log: 2026-09-19 初版作成。
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base, engine

# 設定値ブロック：embedding次元（Fake時は小次元で十分）
EMBEDDING_DIM = 8


def _embedding_column() -> object:
    """環境に応じたembedding列型を返す。

    Returns:
        object: Vector型（Postgres）またはJSON（SQLite等）。

    Side Effects:
        なし。
    """
    if engine.url.drivername.startswith("postgresql"):
        from pgvector.sqlalchemy import Vector

        return mapped_column(Vector(EMBEDDING_DIM))
    return mapped_column(JSON, default=list)


class Document(Base):
    """文書テーブル。"""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class DocumentChunk(Base):
    """RAG用チャンクテーブル。"""

    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = _embedding_column()  # type: ignore[assignment]
