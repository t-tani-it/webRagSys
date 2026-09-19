# -*- coding: utf-8 -*-
"""src/llm/fake_provider.py - 課金なし偽LLM.

Why: テストと学習時に外部課金を避けるため。
What: 固定形式の偽回答を返す。
Assumption / Dependencies: なし。
I/O: 入力=質問＋コンテキスト、出力=偽回答文。
Caution: 本番回答として使わないこと。
Future Work: なし。
Change Log: 2026-09-19 初版作成。
"""


def fake_answer(question: str, context: str) -> str:
    """偽回答を生成する。

    Args:
        question: 質問文。
        context: 検索コンテキスト。

    Returns:
        str: 偽回答文。

    Side Effects:
        なし。
    """
    # 解説：外部通信せず、RAG配線の確認用に定型文を返す。
    head = context[:200].replace("\n", " ")
    return f"[FAKE回答] 質問「{question}」に対する関連情報：「{head}」"
