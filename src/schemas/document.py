# -*- coding: utf-8 -*-
"""src/schemas/document.py - 文書APIの入出力定義.

Why: リクエスト検証とレスポンス整形を分離するため。
What: 作成・更新・参照スキーマを提供する。
Assumption / Dependencies: Pydantic v2。
I/O: 入力=JSON、出力=検証済みdict。
Caution: なし。
Future Work: カテゴリ追加。
Change Log: 2026-09-19 初版作成。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """文書登録リクエスト。"""

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class DocumentUpdate(BaseModel):
    """文書更新リクエスト。"""

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class DocumentOut(BaseModel):
    """文書レスポンス。"""

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
