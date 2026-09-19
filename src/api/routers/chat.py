# -*- coding: utf-8 -*-
"""src/api/routers/chat.py - AIチャットAPI.

Why: 質問に対してRAG回答を返すため。
What: POST /chatを提供する。
Assumption / Dependencies: FastAPI、RAG chain。
I/O: 入力=質問JSON、出力=回答JSON。
Caution: DB／LLM障害時は500系で返す。
Future Work: 会話履歴対応。
Change Log: 2026-09-19 初版作成。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.rag.chain import answer_question
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """質問に回答する。

    Args:
        payload: 質問内容。
        db: DBセッション。

    Returns:
        ChatResponse: 回答と参照ID。

    Raises:
        HTTPException: 内部障害時500。
    """
    try:
        answer, source_ids = answer_question(db, payload.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="回答生成に失敗しました") from exc
    return ChatResponse(answer=answer, source_ids=source_ids)
