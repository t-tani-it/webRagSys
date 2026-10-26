# -*- coding: utf-8 -*-
"""src/schemas/chat.py - チャットAPIの入出力定義.

Why: 質問と回答の形式を固定するため。
What: ChatRequest、ChatResponseを提供する。
Assumption / Dependencies: Pydantic v2。
I/O: 入力=質問JSON、出力=回答JSON。
Caution: なし。
Future Work: 会話履歴ID、出典スコア追加。
Change Log: 2026-09-19 初版作成。
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """質問リクエスト。"""

    # 解説：項目名は英語維持し、説明文だけ日本語化して互換性を保つ。
    question: str = Field(
        min_length=1,
        description="質問文。1文字以上。空は422。先に文書登録が必要。",
        examples=["休暇は何日ですか。"],
    )


class ChatResponse(BaseModel):
    """回答レスポンス。"""

    answer: str = Field(description="回答文。根拠なしの場合もある。")
    source_ids: list[int] = Field(
        default=[],
        description="根拠文書の番号一覧。空は未登録で質問した状態。",
    )
