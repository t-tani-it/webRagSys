# -*- coding: utf-8 -*-
"""src/api/routers/documents.py - 文書CRUD API.

Why: 文書管理機能を提供するため。
What: 一覧・詳細・登録・更新・削除を提供する。
Assumption / Dependencies: FastAPI、SQLAlchemy。
I/O: 入力=JSON／パスID、出力=JSON。
Caution: 存在しないIDは404、不正入力は422を返す。
Future Work: ページング、カテゴリ絞込。
Change Log: 2026-09-19 初版作成。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import Document
from src.rag import chunker, vectorstore
from src.schemas.document import DocumentCreate, DocumentOut, DocumentUpdate

router = APIRouter(prefix="/documents", tags=["documents"])


def validate_input(title: str, content: str) -> None:
    """入力チェックを行う。

    Args:
        title: タイトル。
        content: 本文。

    Raises:
        HTTPException: 空文字の場合422。
    """
    if not title.strip() or not content.strip():
        raise HTTPException(status_code=422, detail="titleとcontentは必須です")


def execute_logic_register(db: Session, payload: DocumentCreate) -> Document:
    """文書登録の本体処理。

    Args:
        db: DBセッション。
        payload: 登録内容。

    Returns:
        Document: 登録行。

    Side Effects:
        documents挿入、chunks保存。
    """
    doc = Document(title=payload.title, content=payload.content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    # 解説：RAG検索用に登録直後にチャンク化する。
    vectorstore.save_chunks(db, doc.id, chunker.split_text(doc.content))
    return doc


@router.get(
    "",
    response_model=list[DocumentOut],
    summary="文書一覧を取得する",
    description="登録済み一覧。空[]は登録ゼロで正常。RAG不使用。",
    response_description="文書一覧を返す。",
)
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    """文書一覧を返す。"""
    return list(db.execute(select(Document).order_by(Document.id)).scalars().all())


@router.get(
    "/{doc_id}",
    response_model=DocumentOut,
    summary="文書詳細を取得する",
    description="控えたidを入力する。存在しない番号は404、数字以外は422。RAG不使用。",
    response_description="文書詳細を返す。",
)
def get_document(doc_id: int, db: Session = Depends(get_db)) -> Document:
    """文書詳細を返す。

    Raises:
        HTTPException: 存在しない場合404。
    """
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="文書が見つかりません")
    return doc


@router.post(
    "",
    response_model=DocumentOut,
    status_code=201,
    summary="文書を登録する",
    description=(
        "先にここで登録し返却idを控えてからchatへ進む。"
        "titleとcontentは必須で空は422。登録後に検索用情報を自動生成する。"
    ),
    response_description="登録した文書を返す。",
)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)) -> Document:
    """文書を登録する。"""
    validate_input(payload.title, payload.content)
    return execute_logic_register(db, payload)


@router.put(
    "/{doc_id}",
    response_model=DocumentOut,
    summary="文書を更新する",
    description="控えたidを指定する。更新成功後は検索用情報も置換済み。対象なしは404、空欄は422。",
    response_description="更新した文書を返す。",
)
def update_document(
    doc_id: int, payload: DocumentUpdate, db: Session = Depends(get_db)
) -> Document:
    """文書を更新する。

    Raises:
        HTTPException: 存在しない場合404。
    """
    validate_input(payload.title, payload.content)
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="文書が見つかりません")
    doc.title = payload.title
    doc.content = payload.content
    db.commit()
    db.refresh(doc)
    vectorstore.save_chunks(db, doc.id, chunker.split_text(doc.content))
    return doc


@router.delete(
    "/{doc_id}",
    status_code=204,
    summary="文書を削除する",
    description="索引削除が先、次に本体削除。204はbodyなしが正常。対象なしは404。",
    response_description="削除成功時は内容なしで返す。",
)
def delete_document(doc_id: int, db: Session = Depends(get_db)) -> None:
    """文書を削除する。

    Raises:
        HTTPException: 存在しない場合404。
    """
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="文書が見つかりません")
    vectorstore.delete_chunks(db, doc.id)
    db.delete(doc)
    db.commit()
