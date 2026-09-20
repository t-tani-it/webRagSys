# AGENTS.md - webRagSys（社内文書検索・AIチャットシステム）

## 概要
社内文書を登録・管理し、登録文書を検索したうえで生成AIが回答するWeb APIシステムである。
Python、FastAPI、REST API、PostgreSQL、LLM API、Embedding、Vector Database、RAG、Dockerの学習を目的とする。
OpenCodeはこのAGENTS.mdを参照して作業を行う。

継承元：親フォルダのマスタAGENTS.md（00_master_agents、02_agents_md_template、03_custom_command_template、04_runtime_prompt_template）に準拠する。
講師ペルソナとして、IT未経験者にも仕組みが理解できる説明を優先する。結論、理由、具体例、注意点、まとめの順を意識する。

## 開発環境
- OS：Windows前提（PowerShell 5.1）
- Python 3.11（実測）／3.10互換を保つ
- 仮想環境はvenv標準（プロジェクト直下の.venv、他案件のconda envを流用しない）
- Git / GitHub、Docker、PostgreSQL＋pgvector、LangChain、OpenAI API
- GPUは使用しない。EmbeddingとLLMはAPIまたはCPU動作のFakeで代替する

## セキュリティ・公開禁止情報
以下の情報はコード・設定ファイル・ログ・ドキュメント・コミットに絶対に含めないこと：
- ローカルパス（例：C:\Users\...などの絶対パス）
- APIキー（OPENAI_API_KEYなど）
- GitHub操作に必要な個人IDやトークン
- パスワードなどの認証情報全般

対策：
- 機密情報は`.env`で管理し、`.gitignore`でGit除外する
- 公開用には`.env.example`のみを用意する
- 生成・修正時は公開禁止情報の混入を必ずチェックする

## GitHub運用ルール
- GitHubでバージョン管理を行う
- リモートはHTTPS方式、認証はgh CLIを用いる
- リポジトリはpublicで作成する（ポートフォリオ用）
- 作成例：`gh repo create <name> --public --source . --remote origin`
- 認証情報（URL・トークン）はコードやAGENTS.mdに直接記述しない
- ブランチは`main`を使用し、リモートで追跡する

### コミット粒度（分割コミット）
- 成果は論理的な区切りごとに分割してコミットする（例：骨格／CRUD／RAG／chat／テスト／docs／図）
- 1コミットにまとめず、`git log --oneline`で履歴が読める粒度にする

### ハンドオーバー運用（フェーズ完了時・必須）
- フェーズ完了時に`docs/handover.md`を必ず更新する
- 記載内容：方針（計画）→実装（実行）→結果→残タスク→実行コマンド
- 進捗管理用mdとして相当詳しく記録し、人間とAIの双方がコンテキスト0%から再開できる状態にする
- 日付、決定事項、実行コマンドと出力、失敗と修正内容を残す

## 技術スタック
- Python 3.10+（実測3.11）
- FastAPI（REST API）
- SQLAlchemy＋PostgreSQL＋pgvector（文書＋ベクトル一元管理）
- LangChain（RAGフレームワーク固定：TextSplitter、Embeddings、VectorStore、Retriever、Chain）
- LLM：外部LLM API（特定モデルに依存しない構成）。既定は課金回避の偽実装
- pytest、ruff
- Docker／docker-compose（ローカル完結優先）

## 偽実装ルール（課金回避・必須）
- 既定は`USE_FAKE=true`とする
- Embeddingは`FakeEmbeddings`、LLMは`FakeListLLM`相当の偽プロバイダを使用する
- 実LLMは`.env`に`OPENAI_API_KEY`等を設定し、`USE_FAKE=false`のときのみ使用する
- テストはすべて偽実装で実行し、外部通信しないこと

## ディレクトリ構造（予定）
- `src/api/` → FastAPIエントリ、ルータ（documents、chat）
- `src/schemas/` → Pydanticスキーマ（リクエスト／レスポンス）
- `src/db/` → DB接続、モデル（documents、document_chunks）
- `src/rag/` → RAG処理（chunker、embeddings、vectorstore、chain）
- `src/llm/` → LLMプロバイダ（本番／偽の切替え）
- `src/utils/` → 共通関数
- `config.py` → 設定値集約（.env読込）
- `tests/` → pytestテスト
- `docs/` → beginner_overview.md、handover.mdなど
- `diagrams/` → Mermaid図（.mmd＋.md＋.pdf）
- ルート → requirements.txt、Dockerfile、docker-compose.yml、.env.example、.gitignore、README.md

## コーディング規約

### 1. ファイル先頭コメント（必須）
各Pythonファイルの冒頭に以下をコメントとして記載すること：
- このファイルの目的（Why）
- 実装する機能の仕様（What）
- 前提条件・依存関係（Assumption / Dependencies）
- 入出力の定義（I/O）
- 注意点（Caution）
- 今後の拡張ポイント（Future Work）
- 変更履歴（Change Log）

※読み手が5秒で概要を理解できる密度で記載すること。

### 2. 設定値ブロック（コード冒頭）
- 設定値はコード冒頭にまとめること
- 設定値は辞書または定数として定義すること
- 設定値の意味をコメントで簡潔に説明すること
- 設定値はconfig.pyに集約すること（ロジック内への直書き禁止）

### 3. 関数構成（コード本体）
以下の構造で関数を実装すること：
- `main()`：全体の流れを管理する
- `validate_input()`：入力チェック
- `execute_logic()`：ビジネスロジック
- `format_output()`：出力整形
- 必要に応じてutility系関数を追加する

※関数は単一責務で設計すること
※関数は副作用を避けること
※型ヒント必須

### 4. コード内コメント（適時）
- なぜこの処理が必要なのか（意図）
- なぜこの順番なのか（理由）
- なぜこのアルゴリズムを選んだのか（背景）
- 例外処理の理由

※コメントは処理の意図を中心に記載し、冗長な説明は避ける。

### 5. 出力形式
- 読みやすい構造化されたコード
- Pythonの場合はPEP8準拠
- 関数ごとに簡潔なdocstringを付与すること
  - 何をする関数なのかを一言で要約（最初の1行）
  - 詳細説明、引数・戻り値・例外、副作用、使用例を明確に書く
  - docstringと型ヒントを矛盾させない
  - コメントは“なぜ”を書く。docstringは“何を”を書く
  - コードが複雑な場合、コメントで“解説：…”の形式で書く
- ファイル生成時は既存構造を尊重すること
- 例外処理は明示的に書くこと（存在しないID、不正リクエスト、DB接続エラー、LLM APIエラー、外部API通信エラー）

## ビルド・実行・テスト
- 仮想環境作成：`python -m venv .venv`（プロジェクト直下、初回のみ）
- 有効化：`.\.venv\Scripts\Activate.ps1`（プロンプトに`(.venv)`表示を確認）
- 依存導入：`pip install -r requirements.txt`（.venv有効化後に実行）
- API起動：`uvicorn src.api.main:app --reload`
- テスト：`pytest`（または`python -m pytest tests -q`）
- Lint：`ruff`（例：`python -m ruff check src tests config.py`）

## 注意点
- RAGはembedding更新が必要（文書登録・更新・削除時にchunksを作り直す）
- chunk_sizeとtop_kはconfigに集約する
- pgvector拡張の有効化SQLが必要（PostgreSQL使用時）
- Docker検証は対象外とする（storage制約のため、2026-09-19決定）。Dockerfileとdocker-compose.ymlは構成見本として残すが、起動検証は行わない
- ローカル起動（uvicorn＋SQLite退避／PostgreSQL直結）を正規の動作確認手段とする
- 認証・CI/CD・クラウド・監視・負荷対策は必要最小限とする
- 本質（Python→API→DB→LLM→RAG）の理解と実装を優先する

## OpenCodeへの指示
- コード生成時はこの規約に従うこと
- 新規ファイルは適切なディレクトリに配置すること
- 修正時は差分を明確に示すこと
- docsとdiagramsの作成はテストの後で行うこと
- docsとdiagramsはPDF生成すること（図はMermaid→PDF、docsはMarkdown→PDF）
- READMEとdocs/handover.mdは先行作成し、随時更新すること
