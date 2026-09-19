# -*- coding: utf-8 -*-
"""src/rag/vectorstore.py - チャンク保存と類似検索.

Why: RAGの保存・検索層を分離するため。
What: save_chunks、searchを提供する。
Assumption / Dependencies: SQLAlchemy、pgvector（Postgres時のみ）。
I/O: 入力=文書ID＋チャンク＋ベクトル、出力=類似チャンク。
Caution: SQLite時はPython側でコサイン計算する（件数が少ない前提）。
Future Work: pgvectorインデックス（HNSW）追加。
Change Log: 2026-09-19 初版作成。
"""

import math

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from config import get_settings
from src.db.models import DocumentChunk
from src.rag.embeddings import embed_query, embed_texts

settings = get_settings()

# 設定値ブロック（冒頭集約）
TOP_K = settings.top_k


def _cosine(a: list[float], b: list[float]) -> float:
    """コサイン類似度を計算する。

    Args:
        a: ベクトルA。
        b: ベクトルB。

    Returns:
        float: 類似度（1に近いほど類似）。
    """
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def save_chunks(db: Session, document_id: int, chunks: list[str]) -> None:
    """既存チャンクを置換して保存する。

    Args:
        db: DBセッション。
        document_id: 文書ID。
        chunks: チャンク一覧。

    Side Effects:
        document_chunks行を削除・挿入する。
    """
    # 解説：更新・削除時に古いベクトルが残らないよう、置換方式にする。
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    vectors = embed_texts(chunks)
    for idx, (chunk, vec) in enumerate(zip(chunks, vectors)):
        db.add(
            DocumentChunk(
                document_id=document_id, chunk_index=idx, content=chunk, embedding=vec
            )
        )
    db.commit()


def delete_chunks(db: Session, document_id: int) -> None:
    """文書のチャンクを削除する。

    Args:
        db: DBセッション。
        document_id: 文書ID.

    Side Effects:
        対象行を削除する。
    """
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    db.commit()


def search(db: Session, query: str, top_k: int = TOP_K) -> list[DocumentChunk]:
    """質問に類似したチャンクを返す。

    Args:
        db: DBセッション。
        query: 質問文。
        top_k: 取得件数。

    Returns:
        list[DocumentChunk]: 類似度順チャンク。

    Side Effects:
        なし（読取のみ）。
    """
    qvec = embed_query(query)
    rows = db.execute(select(DocumentChunk)).scalars().all()
    scored = [(_cosine(qvec, list(r.embedding or [])), r) for r in rows]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:top_k]]
