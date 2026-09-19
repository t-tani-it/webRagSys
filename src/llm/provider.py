# -*- coding: utf-8 -*-
"""src/llm/provider.py - LLM呼出切替層.

Why: 偽実装と本番APIを1か所で切替えるため。
What: generate_answerを提供する。
Assumption / Dependencies: langchain-openaiは本番時のみ必要。
I/O: 入力=質問＋コンテキスト、出力=回答文。
Caution: 既定はFake。APIキーなしで本番指定時は例外にする。
Future Work: モデル別プロバイダ追加。
Change Log: 2026-09-19 初版作成。
"""

from config import get_settings
from src.llm.fake_provider import fake_answer

settings = get_settings()


def generate_answer(question: str, context: str) -> str:
    """回答文を生成する。

    Args:
        question: 質問文。
        context: 検索コンテキスト。

    Returns:
        str: 回答文。

    Raises:
        RuntimeError: 本番設定でAPIキー未設定の場合。

    Side Effects:
        本番時のみ外部API通信する。
    """
    if settings.use_fake or not settings.openai_api_key:
        return fake_answer(question, context)
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError("langchain-openai未導入") from exc
    # 解説：LangChainのChatモデルにプロンプトを渡して回答を得る。
    llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
    prompt = f"以下の社内文書を基に回答してください。\n\n{context}\n\n質問：{question}"
    return str(llm.invoke(prompt).content)
