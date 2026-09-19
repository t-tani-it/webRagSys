# -*- coding: utf-8 -*-
"""src/api/main.py - FastAPIエントリポイント.

Why: API全体の起動点を一元化するため。
What: app生成とルータ登録、起動時DB初期化を行う。
Assumption / Dependencies: FastAPI、routers。
I/O: 入力=HTTP、出力=JSON。
Caution: なし。
Future Work: 認証ミドルウェア追加。
Change Log: 2026-09-19 初版作成。
"""

from fastapi import FastAPI

from src.api.routers import chat, documents
from src.db.database import init_db


def create_app() -> FastAPI:
    """アプリを生成する。

    Returns:
        FastAPI: アプリインスタンス。

    Side Effects:
        ルータ登録、起動時DB初期化。
    """
    app = FastAPI(title="webRagSys")

    @app.on_event("startup")
    def startup() -> None:
        """起動時処理。"""
        try:
            init_db()
        except (OSError, RuntimeError) as exc:
            # 解説：テスト時はDB未起動でもimportできるよう記録のみ行う。
            import logging

            logging.getLogger(__name__).warning("init_db skip: %s", exc)

    @app.get("/health")
    def health() -> dict[str, str]:
        """疎通確認用。"""
        return {"status": "ok"}

    app.include_router(documents.router)
    app.include_router(chat.router)
    return app


app = create_app()
