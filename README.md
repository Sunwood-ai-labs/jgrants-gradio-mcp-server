# Jグランツ MCP Server (Gradio 5 Native)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Gradio](https://img.shields.io/badge/Gradio-5.32.0%2B-orange.svg)](https://gradio.app)
[![MCP](https://img.shields.io/badge/MCP-Native-blue.svg)](https://modelcontextprotocol.io)

デジタル庁が運用する補助金電子申請システム「**Jグランツ**」の公開APIを活用した統合アプリケーション。

**🚀 Gradio 5のネイティブMCP機能を使用:**
- 🌐 **Web UI**: ブラウザから直感的に補助金検索
- 🤖 **MCP Server**: Claude DesktopなどのLLMから自然言語で操作
- ⚡ **ワンコマンド起動**: `launch(mcp_server=True)`で両方同時に動作！


## 特徴

### 🎯 Gradio 5ネイティブMCP統合
- **シンプル設計**: `launch(mcp_server=True)`だけでUIとMCPサーバーが同時起動
- **自動変換**: Gradio関数が自動的にMCPツールに変換
- **統一コードベース**: UIとMCP APIを単一のコードで管理

### 🔍 検索・分析機能
- **高度な検索**: キーワード、業種、従業員数、地域での絞り込み
- **統計分析**: 補助金の統計情報を自動集計（締切期間別、金額規模別）
- **リアルタイム情報**: Jグランツ公開APIから最新の補助金情報を取得

### 📄 ファイル処理
- **自動ダウンロード**: 募集要項や申請書類を自動保存
- **形式変換**: PDF、Word、Excel、ZIPなど多様な形式をMarkdownに変換
- **BASE64対応**: 変換できないファイルはBASE64形式で取得可能

### 🤖 LLM統合
- **Claude Desktop対応**: MCPクライアントから直接利用可能
- **自然言語検索**: LLMから自然言語で補助金検索
- **ツール自動検出**: Gradio関数が自動的にMCPツールとして公開

### 🌐 Webアプリ
- **直感的UI**: ブラウザから簡単にアクセス
- **タブ型インターフェース**: 検索、詳細、統計、ファイル取得など機能別タブ
- **テーブル表示**: 検索結果を見やすい表形式で表示
- **Markdown対応**: 詳細情報を整形されたMarkdownで表示

## 動作確認環境

- **Claude Desktop**: v0.7.10以上
- **Python**: 3.11以上
- **FastMCP**: 2.12.2以上

## クイックスタート

### 前提条件

- Python 3.11以上
- pip (Pythonパッケージマネージャー)

### 🚀 30秒で起動（Web UI + MCPサーバー）

```bash
# 1. リポジトリをクローン
git clone https://github.com/Sunwood-ai-labs/jgrants-gradio-mcp-server.git
cd jgrants-gradio-mcp-server

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. 起動（Gradio UI + MCPサーバーが同時に動作）
python -m jgrants_mcp_server
```

**アクセス方法:**
- 🌐 **Web UI**: ブラウザで `http://localhost:7860` を開く
- 🤖 **MCP**: Claude Desktopから `http://localhost:7860` に接続

Gradio 5のネイティブMCP機能により、単一のサーバーで両方の機能を提供！

### 環境セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/digital-go-jp/jgrants-mcp-server.git
cd jgrants-mcp-server

# Python仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 環境変数（オプション）

必要に応じて以下の環境変数を設定できます：

| 環境変数 | デフォルト値 | 説明 |
|---------|------------|------|
| `JGRANTS_FILES_DIR` | `./jgrants_files` | 添付ファイル保存ディレクトリ |
| `API_BASE_URL` | `https://api.jgrants-portal.go.jp/exp/v1/public` | JグランツAPIエンドポイント |

設定例：
```bash
export JGRANTS_FILES_DIR=/tmp/jgrants_files
```

## サーバー起動

### 🚀 基本起動（Web UI + MCP統合）

```bash
# デフォルト起動（ポート7860）
python -m jgrants_mcp_server

# カスタムポート指定
python -m jgrants_mcp_server --port 8080

# 公開リンク生成（外部アクセス可能）
python -m jgrants_mcp_server --share
```

**起動後に利用可能な機能:**
- 🌐 **Web UI**: `http://localhost:7860`
- 🤖 **MCP Server**: Gradioが提供するMCPエンドポイント（Claude Desktopから接続）

### 📋 起動オプション

```bash
python -m jgrants_mcp_server --help
```

| オプション | デフォルト値 | 説明 |
|-----------|------------|------|
| `--host` | `0.0.0.0` | サーバーホスト |
| `--port` | `7860` | サーバーポート |
| `--share` | `False` | Gradio公開リンクを生成 |
| `--no-mcp` | `False` | MCP機能を無効化（Web UIのみ） |

### 🔧 MCP無効化（Web UIのみ）

```bash
# MCPサーバー機能を無効にしてWeb UIのみ起動
python -m jgrants_mcp_server --no-mcp
```

## Claude Desktop との連携

### Gradio 5ネイティブMCP接続

Gradio 5.32.0以降では、Gradioアプリが直接MCPサーバーとして動作します。

#### ステップ1: アプリを起動

```bash
python -m jgrants_mcp_server
```

起動メッセージで`MCP Server: ENABLED`が表示されることを確認してください。

#### ステップ2: Claude Desktop設定

Claude Desktop設定ファイルを編集:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "jgrants": {
      "command": "uvx",
      "args": [
        "gradio",
        "client",
        "http://localhost:7860"
      ]
    }
  }
}
```

**注意:**
- Gradio 5のMCPサーバーはHTTPベースで動作します
- `uvx`がない場合は`pip install uv`でインストール
- ポート番号は起動時に指定したポートに合わせてください

#### ステップ3: Claude Desktopを再起動

設定を保存して、Claude Desktopを完全に終了してから再起動してください。

### 接続確認

Claude Desktopを開き、新しい会話で以下のように質問してみてください：

```
補助金を検索できますか？
```

サーバーが正しく設定されていれば、利用可能なツールの一覧が表示されます。

## Gradio Webアプリの使い方

### 起動方法

```bash
# デュアルモード（MCPとGradioの両方）
python -m jgrants_mcp_server

# Gradioのみ
python -m jgrants_mcp_server --mode gradio
```

起動後、ブラウザで `http://localhost:7860` にアクセスしてください。

### 機能タブ

#### 🔍 補助金検索
1. **検索条件を入力**
   - キーワード（必須）: 例「IT導入」「DX」「設備投資」
   - 業種、地域、従業員数などの絞り込み条件（任意）
   - 並び順: 受付終了日時、受付開始日時、作成日時
   - 受付状態: 受付中のみ / 全て

2. **検索実行**
   - 最大50件の結果をテーブル形式で表示
   - 各行に補助金ID、タイトル、受付期間、補助上限額などを表示

#### 📄 補助金詳細
1. **補助金IDを入力**（検索結果のIDをコピー＆ペースト）
2. **詳細取得ボタンをクリック**
3. **表示される情報**
   - 補助金の詳細説明
   - 受付期間、補助上限額
   - 対象条件（地域、業種、従業員数、利用目的）
   - ダウンロードされたファイル一覧（申請ガイドライン、補助金概要、申請書類）

#### 📊 統計情報
1. **出力形式を選択**（JSON または CSV）
2. **統計取得ボタンをクリック**
3. **表示される統計**
   - 締切期間別の分布（今月、来月、再来月以降）
   - 金額規模別の分布（100万円以下、1000万円以下、1億円以下、1億円超）
   - 緊急締切案件（14日以内）
   - 高額補助金（5000万円以上）

#### 📁 ファイル取得
1. **補助金IDとファイル名を入力**
2. **形式を選択**（Markdown または BASE64）
3. **ファイル取得ボタンをクリック**
4. **ファイル内容を表示**
   - PDF、Word、Excel、ZIPなどをMarkdownに自動変換
   - 変換できない場合はBASE64形式で表示

5. **ダウンロード済みファイル一覧**
   - すべてのダウンロード済みファイルを確認

#### ℹ️ サーバー情報
- Pingボタンでサーバーの稼働状況を確認
- APIエンドポイント、バージョン情報などを表示

### 使用例

1. **IT導入補助金を検索**
   - キーワード: `IT導入`
   - 業種: `情報通信業`
   - 受付状態: `受付中のみ`
   - 検索実行 → 結果をテーブルで確認

2. **詳細を確認**
   - 気になる補助金のIDをコピー
   - 「補助金詳細」タブに移動
   - IDを貼り付けて詳細取得
   - ファイルがダウンロードされる

3. **ファイル内容を確認**
   - 「ファイル取得」タブに移動
   - 補助金IDとファイル名を入力
   - Markdown形式で内容を表示

### 公開リンクの生成

外部からアクセス可能な公開リンクを生成できます：

```bash
python -m jgrants_mcp_server --mode gradio --gradio-share
```

起動時にGradioが生成する公開URLを共有できます（72時間有効）。

## Prompts と Resources

MCPサーバーは、LLMが効果的にツールを使用できるよう、プロンプトとリソースを提供します。

### Prompts（動的ガイド）

- **`subsidy_search_guide`**: 補助金検索のベストプラクティスと推奨検索パターン
- **`api_usage_agreement`**: API利用規約と免責事項の確認

### Resources（静的リファレンス）

- **`jgrants://guidelines`**: MCPサーバー利用ガイドライン、API制限、トラブルシューティング

## 利用可能なツール

### 1. `search_subsidies`
補助金を検索します。キーワード、業種、地域、従業員数などで絞り込み可能。

**パラメータ:**
- `keyword` (str): 検索キーワード（2文字以上必須）
- `industry` (str, optional): 業種
- `target_area_search` (str, optional): 対象地域
- `target_number_of_employees` (str, optional): 従業員数制約
- `sort` (str): ソート順（`acceptance_end_datetime` / `acceptance_start_datetime` / `created_date`）
- `order` (str): 昇順/降順（`ASC` / `DESC`）
- `acceptance` (int): 受付状態（`0`: 全て / `1`: 受付中のみ）

### 2. `get_subsidy_detail`
補助金の詳細情報を取得し、添付ファイルをローカルに保存します。

**パラメータ:**
- `subsidy_id` (str): 補助金ID（18文字以下）

**返却情報:**
- 補助金の詳細情報（タイトル、補助上限額、補助率、受付期間など）
- 添付ファイルのfile:// URL（公募要領、概要資料、申請様式など）
- ファイル保存先ディレクトリのパス

### 3. `get_subsidy_overview`
補助金の統計情報を取得します（締切期間別、金額規模別の集計）。

**パラメータ:**
- `output_format` (str): 出力形式（`json` / `csv`）

### 4. `get_file_content`
保存済みの添付ファイルの内容を取得します。

**パラメータ:**
- `subsidy_id` (str): 補助金ID
- `filename` (str): ファイル名
- `return_format` (str): 返却形式（`markdown` / `base64`）

**機能:**
- PDF、Word、Excel、PowerPoint、ZIPをMarkdownに自動変換
- 変換失敗時はBASE64形式で返却

### 5. `ping`
サーバーの疎通確認を行います。

## 開発とテスト

### テスト実行

```bash
# テスト実行
pytest tests/test_core.py
```

### デバッグ

```bash
# デバッグモードで起動
python -m jgrants_mcp_server.core --log-level DEBUG
```

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 免責事項
本実装は、技術検証を目的としたサンプルコードです。以下の点にご留意ください：
- 本コードは現状のまま提供され、動作の安定性や継続的な保守を保証するものではありません
- Jグランツサービスの検索性や動作の安定性を保証するものではありません
- 実際の利用にあたっては、JグランツAPIの利用規約 (https://www.jgrants-portal.go.jp/open-api) に準じてご利用ください


