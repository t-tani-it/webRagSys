# -*- coding: utf-8 -*-
"""src/rag/embeddings.py - Embedding生成.

Why: 質問と文書を意味ベクトル化して類似検索するため。
What: Fake（既定）とOpenAIの切替を提供する。
Assumption / Dependencies: langchain-openaiは本番時のみ必要。
I/O: 入力=text一覧、出力=ベクトル一覧。
Caution: APIキーを直書きしない。既定は課金なしFake。
Future Work: 国産Embedding対応。
Change Log: 2026-09-19 初版作成。
"""

from config import get_settings

settings = get_settings()

# 設定値ブロック（冒頭集約）
EMBEDDING_DIM = 8  # Fakeベクトル次元（models.pyと一致させる）


def _fake_vector(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """決定的な偽ベクトルを生成する。

    Args:
        text: 対象文。
        dim: 次元数。

    Returns:
        list[float]: 0〜1の偽ベクトル。

    Side Effects:
        なし。
    """
    # 解説：文字コード合計を種にした簡易ハッシュで、課金なしに再現性を保つ。
    base = sum(ord(c) for c in text) % 100
    return [((base + i * 13) % 100) / 100.0 for i in range(dim)]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """複数文をベクトル化する。

    Args:
        texts: 対象文一覧。

    Returns:
        list[list[float]]: ベクトル一覧。

    Raises:
        RuntimeError: 本番設定でAPIキー未設定の場合。

    Side Effects:
        本番時のみ外部API通信する。
    """
    if settings.use_fake or not settings.openai_api_key:
        return [_fake_vector(t) for t in texts]
    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError as exc:
        raise RuntimeError("langchain-openai未導入") from exc
    # 解説：本番のみ外部通信する。テスト時は上記Fake分岐のため呼ばれない。
    model = OpenAIEmbeddings(
        model=settings.openai_embedding_model, api_key=settings.openai_api_key
    )
    return model.embed_documents(texts)


def embed_query(text: str) -> list[float]:
    """質問文をベクトル化する。

    Args:
        text: 質問文。

    Returns:
        list[float]: 質問ベクトル。
    """
    return embed_texts([text])[0]
