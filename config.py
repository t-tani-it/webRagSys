# -*- coding: utf-8 -*-
"""config.py - webRagSys全体の設定値集約.

Why: 設定値を1か所に集め、環境変数で切替可能にするため。
What: DB接続、LangChain、RAG、LLM偽装フラグを定義する。
Assumption / Dependencies: python-dotenv、pydantic-settingsに依存。
I/O: 入力=.env／環境変数、出力=Settingsインスタンス。
Caution: APIキー等の機密情報を直書きしないこと。
Future Work: 環境別（dev/prod）設定ファイル分割。
Change Log: 2026-09-19 初版作成。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


# 設定値ブロック（冒頭集約）
class Settings(BaseSettings):
    """アプリケーション設定値。"""

    # 起動・DB関連の設定値
    app_name: str = "webRagSys"
    database_url: str = "postgresql://user:password@db:5432/webraq"
    test_database_url: str = "sqlite:///./test.db"

    # RAG関連の設定値（LangChain用）
    chunk_size: int = 500  # 1チャンクの文字数
    chunk_overlap: int = 50  # チャンク間の重なり文字数
    top_k: int = 3  # 類似検索の取得件数

    # LLM関連の設定値（偽装／外部切替）
    # 解説：USE_FAKE=trueは課金なしFakeを強制する。false時のみllm_providerを見る。
    use_fake: bool = True  # True=課金なしFake、False=外部LLM API
    llm_provider: str = "fake"  # fake|openai|ollama（USE_FAKE=false時のみ有効）
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    # Ollama関連の設定値（ローカルLLM用）
    ollama_base_url: str = "http://localhost:11434"  # Ollamaサーバ基底URL
    ollama_model: str = "qwen3.5:4b"  # 会話用モデル名（ollama list表記と一致）
    ollama_embed_model: str = "qwen3-embedding:0.6b"  # Embedding用モデル名
    ollama_num_ctx: int = 8192  # LLMコンテキスト長（RAG文書+質問用）
    embedding_dim: int = 8  # Fake時8、qwen3-embedding:0.6b時1024に変更する

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """設定値シングルトンを返す。

    Args:
        なし。

    Returns:
        Settings: 設定値インスタンス。

    Side Effects:
        なし（.env読込のみ）。
    """
    return Settings()
