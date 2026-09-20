# 2. シーケンス図 Rev.A — 登録と質問応答の通信 (webRagSys)

## この図は何を示すか
登録時と質問時の参加者間の送受信順序を示します。たとえるなら電話の通話記録です。

## なぜ必要か
呼出順序の誤りはRAG不動作の主因のためです。特に登録→分割→保存の順序は固定です。

## 読み方
上から下へ時間順です。実線矢印が依頼、破線矢印が返答です。

## 初心者が混乱しやすい点
- AdminとUserは役割のたとえです。認証機能はありません。同一利用者が両方行います。
- `validate_input`は空欄検査です。違反時は422で本線に入りません。
- 質問前に文書登録が必要です。未登録では類似結果が空になります。

## 実コードとの対応
- `src/api/routers/documents.py`：execute_logic_register（挿入→RAG化）
- `src/rag/chain.py`：answer_question（検索→整形→生成）

```mermaid
sequenceDiagram
    actor User
    actor Admin as 管理者
    participant Docs as documents.py
    participant Chunker as chunker.py
    participant VS as vectorstore.py
    participant Chat as chat.py
    participant Chain as chain.py
    participant LLM as provider.py

    Admin->>Docs: POST /documents タイトル＋本文
    Docs->>Docs: validate_input
    Docs->>Chunker: split_text(content)
    Chunker-->>Docs: chunks
    Docs->>VS: save_chunks(doc_id, chunks)
    VS-->>Docs: 保存完了
    Docs-->>Admin: 201 Created

    User->>Chat: POST /chat 質問
    Chat->>Chain: answer_question(db, question)
    Chain->>VS: search(question, top_k=3)
    VS-->>Chain: 類似チャンク
    Chain->>LLM: generate_answer(質問, コンテキスト)
    LLM-->>Chain: 回答文
    Chain-->>Chat: 回答＋source_ids
    Chat-->>User: JSON返却
```
