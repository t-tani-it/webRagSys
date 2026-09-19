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

    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    """回答レスポンス。"""

    answer: str
    source_ids: list[int] = []
