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
    # 解説：/docsの見出しと説明文だけ日本語化する。項目名は英語維持で互換性を保つ。
    app = FastAPI(
        title="webRagSys 社内文書検索・AIチャット",
        description=(
            "操作順：1 生存確認（GET /health）→ 2 文書登録（POST /documents）"
            "→ 3 質問（POST /chat）。先に登録しないと根拠（source_ids）が空になる。"
            "基本操作は「展開 → Try it out → 入力 → Execute → Responses確認」。"
            "schemasは入出力雛形の参照用であり実行対象ではない。"
        ),
        openapi_tags=[
            {
                "name": "documents",
                "description": (
                    "文書の登録・一覧・詳細・更新・削除。"
                    "先にPOSTで登録し返却idを控えてからchatへ進む。"
                ),
            },
            {
                "name": "chat",
                "description": (
                    "登録文書を根拠に回答する。"
                    "先にdocuments登録が必要。未登録では根拠空になる。"
                ),
            },
        ],
    )

    @app.on_event("startup")
    def startup() -> None:
        """起動時処理。"""
        try:
            init_db()
        except (OSError, RuntimeError) as exc:
            # 解説：テスト時はDB未起動でもimportできるよう記録のみ行う。
            import logging

            logging.getLogger(__name__).warning("init_db skip: %s", exc)

    @app.get(
        "/health",
        summary="生存確認（最初に実行）",
        description="サーバ生存確定用。200 body okなら以降操作可。接続不可なら起動確認に戻る。",
    )
    def health() -> dict[str, str]:
        """疎通確認用。"""
        return {"status": "ok"}

    app.include_router(documents.router)
    app.include_router(chat.router)
    return app


app = create_app()
