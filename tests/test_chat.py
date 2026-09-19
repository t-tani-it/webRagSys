# -*- coding: utf-8 -*-
"""tests/test_chat.py - AIチャットテスト（偽実装）.

Why: 課金なしでRAG回答の配線を検証するため。
What: 質問送信、偽回答、参照ID、RAG検索を検証する。
Assumption / Dependencies: USE_FAKE=true、conftestのclient。
I/O: 入力=質問JSON、出力=回答JSON。
Caution: 外部通信しないこと。
Future Work: 本番LLMのモック追加。
Change Log: 2026-09-19 初版作成。
"""

from fastapi.testclient import TestClient

from src.rag.chunker import split_text


def test_chat_uses_documents(client: TestClient) -> None:
    """登録文書を利用した回答を検証する。"""
    client.post("/documents", json={"title": "休暇規定", "content": "年次休暇は10日付与される"})
    res = client.post("/chat", json={"question": "休暇は何日?"})
    assert res.status_code == 200
    body = res.json()
    assert "FAKE回答" in body["answer"]
    assert len(body["source_ids"]) >= 1


def test_chunker() -> None:
    """分割処理を検証する。"""
    chunks = split_text("abcdef", chunk_size=4, overlap=1)
    assert chunks[0] == "abcd"
    assert "".join(chunks).replace(" ", "") != ""
