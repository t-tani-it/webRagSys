# 4. マインドマップ Rev.A — システム概念の階層整理

## この図は何を示すか
全構成要素の所属階層を示します。たとえるなら目次です。

## なぜ必要か
未知ファイルの所属判定に使うためです。配置先の誤りを防ぎます。

## 読み方
中心から外側へ大分類から小部品へ進みます。

## 初心者が混乱しやすい点
- 初版はSQLiteをテスト用のみと記載していました。Rev.Aでローカル正規の`app.db`を追加しました。
- Postgresは本番用です。Docker対象外のため通常はSQLite側を使用します。
- `500_50`は500文字分割と50文字重なりの意味です。

## 実コードとの対応
- `config.py`：Configuration相当
- `tests/`：Tests相当、conftest.pyでSQLite分離

```mermaid
mindmap
  root((webRagSys))
    API_Layer
      main.py
        create_app
        health
      routers/documents.py
        CRUD 5件
        validate_input
      routers/chat.py
        POST chat
      schemas
        DocumentCreate Update Out
        ChatRequest Response
    Rag_Layer LangChain
      chunker.py
        split_text 500_50
      embeddings.py
        Fake既定
        OpenAI本番
      vectorstore.py
        save_chunks 置換
        search top_k 3
      chain.py
        answer_question
    Data_Layer
      Postgres pgvector 本番
        documents
        document_chunks
      SQLite ローカル正規
        app.db
        テスト用 test.db
    Llm_Layer
      provider.py 切替
      fake_provider.py
        FAKE回答
    Configuration
      config.py
        Settings集約
        USE_FAKE
        CHUNK_SIZE TOP_K
    Tests
      test_documents 5件
      test_chat RAG検証
```
