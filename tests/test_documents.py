# -*- coding: utf-8 -*-
"""tests/test_documents.py - 文書CRUDテスト.

Why: 要件の文書管理5項目を検証するため。
What: 登録・取得・更新・削除・存在しないIDを検証する。
Assumption / Dependencies: pytest、conftestのclient。
I/O: 入力=API呼出、出力=検証結果。
Caution: なし。
Future Work: ページング追加時に拡張。
Change Log: 2026-09-19 初版作成。
"""

from fastapi.testclient import TestClient


def test_create_and_get(client: TestClient) -> None:
    """登録後に取得できることを検証する。"""
    res = client.post("/documents", json={"title": "休暇規定", "content": "年次休暇は10日"})
    assert res.status_code == 201
    doc_id = res.json()["id"]
    res = client.get(f"/documents/{doc_id}")
    assert res.status_code == 200
    assert res.json()["title"] == "休暇規定"


def test_list(client: TestClient) -> None:
    """一覧取得を検証する。"""
    client.post("/documents", json={"title": "A", "content": "a1"})
    res = client.get("/documents")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_update(client: TestClient) -> None:
    """更新を検証する。"""
    doc_id = client.post("/documents", json={"title": "旧", "content": "旧本文"}).json()["id"]
    res = client.put(f"/documents/{doc_id}", json={"title": "新", "content": "新本文"})
    assert res.status_code == 200
    assert res.json()["title"] == "新"


def test_delete(client: TestClient) -> None:
    """削除を検証する。"""
    doc_id = client.post("/documents", json={"title": "消", "content": "消本文"}).json()["id"]
    res = client.delete(f"/documents/{doc_id}")
    assert res.status_code == 204
    res = client.get(f"/documents/{doc_id}")
    assert res.status_code == 404


def test_not_found(client: TestClient) -> None:
    """存在しないIDで404を検証する。"""
    assert client.get("/documents/99999").status_code == 404
    assert client.put("/documents/99999", json={"title": "x", "content": "y"}).status_code == 404
    assert client.delete("/documents/99999").status_code == 404
