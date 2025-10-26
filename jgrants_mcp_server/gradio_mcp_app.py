"""Gradio 5 Native MCP Server - jGrants Subsidy Search System

This module provides both a web UI and MCP server functionality using Gradio 5's native MCP support.
Simply launch with mcp_server=True to enable both modes simultaneously.
"""

import gradio as gr
import asyncio
import json
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Import core functions
from .core import (
    _search_subsidies_internal,
    get_subsidy_detail,
    get_subsidy_overview,
    get_file_content,
    ping,
    FILES_DIR
)


# ========================================
# Sync wrapper functions for Gradio
# ========================================

def search_subsidies(
    keyword: str,
    industry: str = "",
    target_area: str = "",
    employees: str = "",
    sort: str = "acceptance_end_datetime",
    order: str = "ASC",
    acceptance: int = 1
) -> Tuple[str, pd.DataFrame]:
    """
    補助金を検索します。

    Args:
        keyword: 検索キーワード（必須、2文字以上）
        industry: 業種（オプション）
        target_area: 対象地域（オプション）
        employees: 従業員数制約（オプション）
        sort: ソート順（acceptance_end_datetime/acceptance_start_datetime/created_date）
        order: 昇順/降順（ASC/DESC）
        acceptance: 受付状態（0=全て、1=受付中のみ）

    Returns:
        検索結果のサマリーとデータフレーム
    """
    try:
        result = asyncio.run(_search_subsidies_internal(
            keyword=keyword or "事業",
            industry=industry if industry else None,
            target_area_search=target_area if target_area else None,
            target_number_of_employees=employees if employees else None,
            sort=sort,
            order=order,
            acceptance=acceptance
        ))

        if "error" in result:
            return f"❌ エラー: {result['error']}", pd.DataFrame()

        subsidies = result.get("subsidies", [])
        total = result.get("total_count", 0)

        if total == 0:
            return "⚠️ 検索結果が見つかりませんでした。", pd.DataFrame()

        # テーブル用データを作成
        table_data = []
        for s in subsidies[:50]:
            table_data.append({
                "ID": s.get("id", ""),
                "タイトル": s.get("title", ""),
                "受付開始": s.get("acceptance_start_datetime", "")[:10] if s.get("acceptance_start_datetime") else "",
                "受付終了": s.get("acceptance_end_datetime", "")[:10] if s.get("acceptance_end_datetime") else "",
                "補助上限額": s.get("subsidy_max_limit", ""),
                "対象地域": s.get("target_area_search", ""),
            })

        df = pd.DataFrame(table_data)
        summary = f"✅ 検索結果: {total}件（最初の{min(50, total)}件を表示）\n"
        summary += f"📋 検索条件: {json.dumps(result.get('search_conditions', {}), ensure_ascii=False, indent=2)}"

        return summary, df

    except Exception as e:
        return f"❌ エラーが発生しました: {str(e)}", pd.DataFrame()


def get_detail(subsidy_id: str) -> str:
    """
    補助金の詳細情報を取得します。

    Args:
        subsidy_id: 補助金ID

    Returns:
        補助金の詳細情報（Markdown形式）
    """
    try:
        if not subsidy_id or not subsidy_id.strip():
            return "⚠️ 補助金IDを入力してください。"

        result = asyncio.run(get_subsidy_detail(subsidy_id.strip()))

        if "error" in result:
            return f"❌ エラー: {result['error']}"

        output = f"# {result.get('title', '無題')}\n\n"
        output += f"**ID**: `{result.get('id', '')}`\n\n"
        output += f"**ステータス**: {result.get('status', '')}\n\n"
        output += f"**補助上限額**: {result.get('subsidy_max_limit', '未設定')}\n\n"
        output += f"**受付期間**: {result.get('acceptance_start', '')} 〜 {result.get('acceptance_end', '')}\n\n"

        output += "## 対象条件\n\n"
        target = result.get('target', {})
        output += f"- **地域**: {target.get('area', '指定なし')}\n"
        output += f"- **業種**: {target.get('industry', '指定なし')}\n"
        output += f"- **従業員数**: {target.get('employees', '指定なし')}\n"
        output += f"- **利用目的**: {target.get('purpose', '指定なし')}\n\n"

        if result.get('application_url'):
            output += f"**申請URL**: {result.get('application_url')}\n\n"

        output += "## 詳細説明\n\n"
        desc = result.get('description', '説明がありません。')
        output += desc[:1000] + ("..." if len(desc) > 1000 else "") + "\n\n"

        files = result.get('files', {})
        if any(files.values()):
            output += "## 📁 ダウンロードされたファイル\n\n"
            output += f"保存先: `{result.get('save_directory', '')}`\n\n"

            type_names = {
                "application_guidelines": "📋 申請ガイドライン",
                "outline_of_grant": "📄 補助金概要",
                "application_form": "📝 申請書類"
            }

            for file_type, file_list in files.items():
                if file_list:
                    output += f"### {type_names.get(file_type, file_type)}\n\n"
                    for f in file_list:
                        if "error" in f:
                            output += f"- ❌ {f.get('name', '')}: {f.get('error', '')}\n"
                        else:
                            output += f"- ✅ `{f.get('name', '')}` ({f.get('size', 0):,} bytes)\n"
                    output += "\n"

        output += f"\n**最終更新**: {result.get('last_updated', '')}\n"
        return output

    except Exception as e:
        return f"❌ エラーが発生しました: {str(e)}"


def get_overview(output_format: str = "json") -> str:
    """
    補助金の統計情報を取得します。

    Args:
        output_format: 出力形式（json/csv）

    Returns:
        統計情報（Markdown形式）
    """
    try:
        result = asyncio.run(get_subsidy_overview(output_format))

        if "error" in result:
            return f"❌ エラー: {result['error']}"

        if output_format == "csv":
            output = "# 📊 補助金統計情報（CSV形式）\n\n"
            output += f"**総件数**: {result.get('total_count', 0)}\n"
            output += f"**生成日時**: {result.get('statistics_generated_at', '')}\n\n"

            if "deadline_statistics" in result:
                output += "## 締切期間別統計\n```csv\n"
                output += result["deadline_statistics"]
                output += "```\n\n"

            if "amount_statistics" in result:
                output += "## 金額規模別統計\n```csv\n"
                output += result["amount_statistics"]
                output += "```\n\n"

            return output

        # JSON形式
        output = "# 📊 補助金統計情報\n\n"
        output += f"**総件数**: {result.get('total_count', 0)}\n"
        output += f"**生成日時**: {result.get('statistics_generated_at', '')}\n\n"

        output += "## 📅 締切期間別の分布\n\n"
        deadline = result.get('by_deadline_period', {})
        output += f"- 今月締切: {deadline.get('this_month', 0)}件\n"
        output += f"- 来月締切: {deadline.get('next_month', 0)}件\n"
        output += f"- 再来月以降: {deadline.get('after_next_month', 0)}件\n\n"

        output += "## 💰 金額規模別の分布\n\n"
        amount = result.get('by_amount_range', {})
        output += f"- 100万円以下: {amount.get('under_1m', 0)}件\n"
        output += f"- 1000万円以下: {amount.get('under_10m', 0)}件\n"
        output += f"- 1億円以下: {amount.get('under_100m', 0)}件\n"
        output += f"- 1億円超: {amount.get('over_100m', 0)}件\n"
        output += f"- 金額未設定: {amount.get('unspecified', 0)}件\n\n"

        urgent = result.get('urgent_deadlines', [])
        if urgent:
            output += f"## ⚠️ 緊急締切案件（14日以内: {len(urgent)}件）\n\n"
            for u in urgent[:10]:
                output += f"- **{u.get('title', '')}** (残り{u.get('days_left', 0)}日)\n"
            output += "\n"

        high_amount = result.get('high_amount_subsidies', [])
        if high_amount:
            output += f"## 💎 高額補助金（5000万円以上: {len(high_amount)}件）\n\n"
            for h in high_amount[:10]:
                output += f"- **{h.get('title', '')}** ({h.get('max_amount', 0):,.0f}円)\n"

        return output

    except Exception as e:
        return f"❌ エラーが発生しました: {str(e)}"


def get_file(subsidy_id: str, filename: str, return_format: str = "markdown") -> str:
    """
    保存されたファイルの内容を取得します。

    Args:
        subsidy_id: 補助金ID
        filename: ファイル名
        return_format: 返却形式（markdown/base64）

    Returns:
        ファイル内容（Markdown形式またはBASE64）
    """
    try:
        if not subsidy_id or not filename:
            return "⚠️ 補助金IDとファイル名を入力してください。"

        result = asyncio.run(get_file_content(
            subsidy_id.strip(),
            filename.strip(),
            return_format
        ))

        if "error" in result:
            return f"❌ エラー: {result['error']}"

        if return_format == "markdown":
            output = f"# 📄 {result.get('filename', '')}\n\n"
            output += f"**MIMEタイプ**: {result.get('mime_type', '')}\n"
            output += f"**サイズ**: {result.get('size_bytes', 0):,} bytes\n"
            output += f"**抽出方法**: {result.get('extraction_method', 'N/A')}\n\n"
            output += "---\n\n"
            output += result.get('content_markdown', '')
            return output
        else:
            output = f"# 📄 {result.get('filename', '')} (BASE64)\n\n"
            output += f"**MIMEタイプ**: {result.get('mime_type', '')}\n"
            output += f"**サイズ**: {result.get('size_bytes', 0):,} bytes\n\n"
            output += "```\n" + result.get('content_base64', '')[:500] + "...\n```"
            return output

    except Exception as e:
        return f"❌ エラーが発生しました: {str(e)}"


def list_files() -> str:
    """ダウンロード済みファイルの一覧を表示します。"""
    try:
        if not FILES_DIR.exists():
            return "⚠️ ファイルディレクトリが存在しません。"

        output = "# 📁 ダウンロード済みファイル一覧\n\n"
        output += f"保存先: `{FILES_DIR}`\n\n"

        subsidy_dirs = [d for d in FILES_DIR.iterdir() if d.is_dir()]
        if not subsidy_dirs:
            return output + "\n⚠️ まだファイルがダウンロードされていません。"

        for subsidy_dir in sorted(subsidy_dirs, key=lambda x: x.name):
            files = list(subsidy_dir.iterdir())
            if files:
                output += f"## 補助金ID: `{subsidy_dir.name}`\n\n"
                for file in sorted(files, key=lambda x: x.name):
                    size = file.stat().st_size
                    output += f"- `{file.name}` ({size:,} bytes)\n"
                output += "\n"

        return output

    except Exception as e:
        return f"❌ エラーが発生しました: {str(e)}"


def server_ping() -> str:
    """サーバーの疎通確認を行います。"""
    try:
        result = asyncio.run(ping())
        return "✅ **サーバー稼働中**\n\n```json\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n```"
    except Exception as e:
        return f"❌ エラー: {str(e)}"


# ========================================
# Gradio UI Definition
# ========================================

def create_gradio_app():
    """Create Gradio application with native MCP support"""

    with gr.Blocks(
        title="Jグランツ補助金検索システム",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        """
    ) as demo:

        gr.Markdown("""
        # 🏢 Jグランツ補助金検索システム

        デジタル庁が運用する補助金電子申請システム「Jグランツ」の公開APIを利用した検索システムです。

        **🚀 Gradio 5ネイティブMCP統合**: このアプリはMCPサーバーとしても機能します！
        - `launch(mcp_server=True)`で起動すると、Web UIとMCPサーバーの両方が動作します
        - Claude DesktopなどのMCPクライアントから利用可能

        **⚠️ 注意**: 取得した情報を利用・公開する際は「Jグランツ（jGrants）からの出典」である旨を明記してください。
        """)

        with gr.Tabs():
            # Tab 1: Search
            with gr.Tab("🔍 補助金検索"):
                gr.Markdown("### 検索条件を入力して補助金を検索")

                with gr.Row():
                    with gr.Column(scale=2):
                        keyword_input = gr.Textbox(
                            label="検索キーワード",
                            placeholder="例: IT導入、DX、設備投資",
                            value="事業"
                        )
                    with gr.Column(scale=1):
                        acceptance_input = gr.Radio(
                            label="受付状態",
                            choices=[("全て", 0), ("受付中のみ", 1)],
                            value=1
                        )

                with gr.Row():
                    industry_input = gr.Dropdown(
                        label="業種",
                        choices=["", "製造業", "情報通信業", "卸売業、小売業", "建設業", "宿泊業、飲食サービス業"],
                        value=""
                    )
                    target_area_input = gr.Dropdown(
                        label="対象地域",
                        choices=["", "全国", "東京都", "大阪府", "愛知県", "北海道", "福岡県"],
                        value=""
                    )
                    employees_input = gr.Dropdown(
                        label="従業員数",
                        choices=["", "従業員数の制約なし", "5名以下", "20名以下", "50名以下", "100名以下"],
                        value=""
                    )

                with gr.Row():
                    sort_input = gr.Dropdown(
                        label="並び順",
                        choices=[
                            ("受付終了日時", "acceptance_end_datetime"),
                            ("受付開始日時", "acceptance_start_datetime"),
                            ("作成日時", "created_date")
                        ],
                        value="acceptance_end_datetime"
                    )
                    order_input = gr.Radio(
                        label="昇順/降順",
                        choices=[("昇順", "ASC"), ("降順", "DESC")],
                        value="ASC"
                    )

                search_btn = gr.Button("🔍 検索実行", variant="primary", size="lg")
                search_output = gr.Textbox(label="検索結果サマリー", lines=5)
                search_table = gr.Dataframe(label="検索結果テーブル", interactive=False)

                search_btn.click(
                    fn=search_subsidies,
                    inputs=[keyword_input, industry_input, target_area_input,
                           employees_input, sort_input, order_input, acceptance_input],
                    outputs=[search_output, search_table]
                )

            # Tab 2: Detail
            with gr.Tab("📄 補助金詳細"):
                gr.Markdown("### 補助金IDを入力して詳細情報を取得")
                subsidy_id_input = gr.Textbox(
                    label="補助金ID",
                    placeholder="例: a0WJ200000CDR9HMAX"
                )
                detail_btn = gr.Button("📄 詳細取得", variant="primary", size="lg")
                detail_output = gr.Markdown(label="詳細情報")

                detail_btn.click(
                    fn=get_detail,
                    inputs=[subsidy_id_input],
                    outputs=[detail_output]
                )

            # Tab 3: Statistics
            with gr.Tab("📊 統計情報"):
                gr.Markdown("### 補助金の統計情報を表示")
                format_input = gr.Radio(
                    label="出力形式",
                    choices=[("JSON", "json"), ("CSV", "csv")],
                    value="json"
                )
                stats_btn = gr.Button("📊 統計取得", variant="primary", size="lg")
                stats_output = gr.Markdown(label="統計情報")

                stats_btn.click(
                    fn=get_overview,
                    inputs=[format_input],
                    outputs=[stats_output]
                )

            # Tab 4: File Access
            with gr.Tab("📁 ファイル取得"):
                gr.Markdown("### ダウンロード済みファイルの内容を取得")

                with gr.Row():
                    file_subsidy_id = gr.Textbox(label="補助金ID", scale=2)
                    file_filename = gr.Textbox(label="ファイル名", scale=2)
                    file_format = gr.Radio(
                        label="形式",
                        choices=[("Markdown", "markdown"), ("BASE64", "base64")],
                        value="markdown",
                        scale=1
                    )

                file_btn = gr.Button("📁 ファイル取得", variant="primary", size="lg")
                file_output = gr.Markdown(label="ファイル内容")

                file_btn.click(
                    fn=get_file,
                    inputs=[file_subsidy_id, file_filename, file_format],
                    outputs=[file_output]
                )

                gr.Markdown("---")
                list_files_btn = gr.Button("📋 ダウンロード済みファイル一覧", size="lg")
                files_list_output = gr.Markdown(label="ファイル一覧")

                list_files_btn.click(
                    fn=list_files,
                    outputs=[files_list_output]
                )

            # Tab 5: Server Info
            with gr.Tab("ℹ️ サーバー情報"):
                gr.Markdown("### サーバーの稼働状況を確認")
                ping_btn = gr.Button("🏓 Ping", variant="primary", size="lg")
                ping_output = gr.Markdown(label="サーバー応答")

                ping_btn.click(
                    fn=server_ping,
                    outputs=[ping_output]
                )

                gr.Markdown("""
                ---

                ### このアプリについて

                - **API**: https://api.jgrants-portal.go.jp/exp/v1/public
                - **公式サイト**: https://www.jgrants-portal.go.jp/
                - **MCP統合**: Gradio 5ネイティブMCPサーバー機能

                ### 免責事項

                本アプリは技術検証を目的としたサンプルです：
                - 取得情報は「Jグランツ（jGrants）からの出典」を明記してください
                - 正式申請前に公式サイトで最新情報を確認してください
                - 過度な連続アクセスは避けてください
                """)

    return demo


def launch_app(
    server_name: str = "0.0.0.0",
    server_port: int = 7860,
    share: bool = False,
    mcp_server: bool = True
):
    """
    Launch Gradio application with optional MCP server support

    Args:
        server_name: Server host
        server_port: Server port
        share: Create public link
        mcp_server: Enable MCP server mode (Gradio 5.32.0+)
    """
    demo = create_gradio_app()

    print("=" * 60)
    print("🚀 Jグランツ補助金検索システム")
    print("=" * 60)
    print(f"📱 Gradio UI: http://localhost:{server_port}")
    if mcp_server:
        print(f"🔌 MCP Server: ENABLED (Gradio native MCP)")
        print("   → Claude Desktopなどから接続可能")
    print("=" * 60)

    demo.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        mcp_server=mcp_server  # Gradio 5.32.0+ native MCP support
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Jグランツ Gradio MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=7860, help="Server port")
    parser.add_argument("--share", action="store_true", help="Create public link")
    parser.add_argument("--no-mcp", action="store_true", help="Disable MCP server mode")

    args = parser.parse_args()

    launch_app(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        mcp_server=not args.no_mcp
    )
