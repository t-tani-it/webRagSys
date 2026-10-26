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

    # 解説：項目名は英語維持し、説明文だけ日本語化して互換性を保つ。
    title: str = Field(
        min_length=1,
        max_length=200,
        description="文書題名。1文字以上200文字以下。空は422。",
        examples=["休暇規定"],
    )
    content: str = Field(
        min_length=1,
        description="文書本文。1文字以上。検索と回答の根拠になる。",
        examples=["年次休暇は10日付与する。"],
    )


class DocumentUpdate(BaseModel):
    """文書更新リクエスト。"""

    title: str = Field(
        min_length=1,
        max_length=200,
        description="文書題名。1文字以上200文字以下。空は422。",
        examples=["休暇規定"],
    )
    content: str = Field(
        min_length=1,
        description="文書本文。1文字以上。更新後は検索用情報も置換される。",
        examples=["年次休暇は10日付与する。"],
    )


class DocumentOut(BaseModel):
    """文書レスポンス。"""

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
