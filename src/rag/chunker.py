# -*- coding: utf-8 -*-
"""src/rag/chunker.py - 文書分割処理.

Why: 長文を検索可能な単位に分割するため（RAGの第一段階）。
What: LangChainのTextSplitter優先、なければ単純分割にフォールバックする。
Assumption / Dependencies: langchain_text_splitters任意。
I/O: 入力=本文str、出力=チャンクlist[str]。
Caution: なし。
Future Work: PDF／Word対応。
Change Log: 2026-09-19 初版作成。
"""

from config import get_settings

settings = get_settings()

# 設定値ブロック（冒頭集約）
CHUNK_SIZE = settings.chunk_size
CHUNK_OVERLAP = settings.chunk_overlap


def split_text(
    content: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """本文をチャンク分割する。

    Args:
        content: 文書本文。
        chunk_size: 1チャンクの文字数。
        overlap: 重なり文字数。

    Returns:
        list[str]: チャンク一覧。

    Side Effects:
        なし。

    Examples:
        >>> split_text("abcdef", chunk_size=4, overlap=1)
        ['abcd', 'def']
    """
    # 解説：LangChainがあればRecursiveCharacterTextSplitterを使い、なければ単純分割する。
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap
        )
        return splitter.split_text(content)
    except ImportError:
        chunks: list[str] = []
        step = max(chunk_size - overlap, 1)
        for i in range(0, len(content), step):
            chunks.append(content[i : i + chunk_size])
        return chunks
