# -*- coding: utf-8 -*-
"""src/rag/chain.py - RAG回答チェーン.

Why: 検索→整形→LLMの流れを1関数にまとめるため。
What: answer_questionを提供する（LangChain Retriever相当の薄い層）。
Assumption / Dependencies: vectorstore、llm.providerに依存。
I/O: 入力=DB＋質問、出力=回答＋参照ID。
Caution: なし。
Future Work: LCEL Chainへの置換、出典スコア付与。
Change Log: 2026-09-19 初版作成。
"""

from sqlalchemy.orm import Session

from src.llm.provider import generate_answer
from src.rag import vectorstore


def answer_question(db: Session, question: str) -> tuple[str, list[int]]:
    """RAGで質問に回答する。

    Args:
        db: DBセッション。
        question: 質問文。

    Returns:
        tuple[str, list[int]]: 回答文と参照文書ID一覧。

    Side Effects:
        読取のみ（保存しない）。
    """
    # 解説：validate→検索→整形→生成の順にする。保存は行わない。
    hits = vectorstore.search(db, question)
    context = "\n".join(h.content for h in hits)
    answer = generate_answer(question, context)
    source_ids = sorted({h.document_id for h in hits})
    return answer, source_ids
