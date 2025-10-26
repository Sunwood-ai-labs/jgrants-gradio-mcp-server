"""Gradio UI for jGrants MCP Server"""

import gradio as gr
import asyncio
import json
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# coreモジュールから関数をインポート
from .core import (
    _search_subsidies_internal,
    get_subsidy_detail,
    get_subsidy_overview,
    get_file_content,
    ping,
    FILES_DIR
)


def sync_search_subsidies(
    keyword: str,
    industry: str = "",
    target_area: str = "",
    employees: str = "",
    sort: str = "acceptance_end_datetime",
    order: str = "ASC",
    acceptance: int = 1
) -> tuple[str, str]:
    """補助金検索（同期版ラッパー）"""
    try:
        # asyncio.run()で非同期関数を実行
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
            return f"エラー: {result['error']}", ""

        # 結果を整形
        subsidies = result.get("subsidies", [])
        total = result.get("total_count", 0)

        if total == 0:
            return "検索結果が見つかりませんでした。", ""

        # テーブル用のデータを作成
        table_data = []
        for s in subsidies[:50]:  # 最初の50件のみ表示
            table_data.append({
                "ID": s.get("id", ""),
                "タイトル": s.get("title", ""),
                "受付開始": s.get("acceptance_start_datetime", "")[:10] if s.get("acceptance_start_datetime") else "",
                "受付終了": s.get("acceptance_end_datetime", "")[:10] if s.get("acceptance_end_datetime") else "",
                "補助上限額": s.get("subsidy_max_limit", ""),
                "対象地域": s.get("target_area_search", ""),
            })

        df = pd.DataFrame(table_data)

        summary = f"検索結果: {total}件（最初の{min(50, total)}件を表示）\n"
        summary += f"検索条件: {json.dumps(result.get('search_conditions', {}), ensure_ascii=False, indent=2)}"

        return summary, df

    except Exception as e:
        return f"エラーが発生しました: {str(e)}", ""


def sync_get_detail(subsidy_id: str) -> str:
    """補助金詳細取得（同期版ラッパー）"""
    try:
        if not subsidy_id or not subsidy_id.strip():
            return "補助金IDを入力してください。"

        result = asyncio.run(get_subsidy_detail(subsidy_id.strip()))

        if "error" in result:
            return f"エラー: {result['error']}"

        # 詳細情報を整形して表示
        output = f"# {result.get('title', '無題')}\n\n"
        output += f"**ID**: {result.get('id', '')}\n\n"
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
        output += result.get('description', '説明がありません。')[:1000] + "...\n\n"

        # ファイル情報
        files = result.get('files', {})
        if any(files.values()):
            output += "## ダウンロードされたファイル\n\n"
            output += f"保存先: `{result.get('save_directory', '')}`\n\n"

            for file_type, file_list in files.items():
                if file_list:
                    type_names = {
                        "application_guidelines": "申請ガイドライン",
                        "outline_of_grant": "補助金概要",
                        "application_form": "申請書類"
                    }
                    output += f"### {type_names.get(file_type, file_type)}\n\n"

                    for f in file_list:
                        if "error" in f:
                            output += f"- ❌ {f.get('name', '')}: {f.get('error', '')}\n"
                        else:
                            output += f"- ✅ {f.get('name', '')} ({f.get('size', 0):,} bytes)\n"
                            if "mcp_access" in f:
                                output += f"  - ファイルID: `{subsidy_id}/{f.get('name', '')}`\n"
                    output += "\n"

        output += f"\n\n**最終更新**: {result.get('last_updated', '')}\n"

        return output

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


def sync_get_overview(output_format: str = "json") -> str:
    """統計情報取得（同期版ラッパー）"""
    try:
        result = asyncio.run(get_subsidy_overview(output_format))

        if "error" in result:
            return f"エラー: {result['error']}"

        if output_format == "csv":
            output = "# 補助金統計情報（CSV形式）\n\n"
            output += f"総件数: {result.get('total_count', 0)}\n"
            output += f"生成日時: {result.get('statistics_generated_at', '')}\n\n"

            if "deadline_statistics" in result:
                output += "## 締切期間別統計\n```csv\n"
                output += result["deadline_statistics"]
                output += "```\n\n"

            if "amount_statistics" in result:
                output += "## 金額規模別統計\n```csv\n"
                output += result["amount_statistics"]
                output += "```\n\n"

            if "urgent_deadlines" in result:
                output += "## 緊急締切案件\n```csv\n"
                output += result["urgent_deadlines"]
                output += "```\n\n"

            if "high_amount_subsidies" in result:
                output += "## 高額補助金\n```csv\n"
                output += result["high_amount_subsidies"]
                output += "```\n\n"

            return output

        # JSON形式
        output = "# 補助金統計情報\n\n"
        output += f"**総件数**: {result.get('total_count', 0)}\n"
        output += f"**生成日時**: {result.get('statistics_generated_at', '')}\n\n"

        output += "## 締切期間別の分布\n\n"
        deadline = result.get('by_deadline_period', {})
        output += f"- 今月締切: {deadline.get('this_month', 0)}件\n"
        output += f"- 来月締切: {deadline.get('next_month', 0)}件\n"
        output += f"- 再来月以降: {deadline.get('after_next_month', 0)}件\n\n"

        output += "## 金額規模別の分布\n\n"
        amount = result.get('by_amount_range', {})
        output += f"- 100万円以下: {amount.get('under_1m', 0)}件\n"
        output += f"- 1000万円以下: {amount.get('under_10m', 0)}件\n"
        output += f"- 1億円以下: {amount.get('under_100m', 0)}件\n"
        output += f"- 1億円超: {amount.get('over_100m', 0)}件\n"
        output += f"- 金額未設定: {amount.get('unspecified', 0)}件\n\n"

        urgent = result.get('urgent_deadlines', [])
        if urgent:
            output += f"## 緊急締切案件（14日以内: {len(urgent)}件）\n\n"
            for u in urgent[:10]:
                output += f"- **{u.get('title', '')}** (ID: {u.get('id', '')}, 残り{u.get('days_left', 0)}日)\n"
            output += "\n"

        high_amount = result.get('high_amount_subsidies', [])
        if high_amount:
            output += f"## 高額補助金（5000万円以上: {len(high_amount)}件）\n\n"
            for h in high_amount[:10]:
                output += f"- **{h.get('title', '')}** (ID: {h.get('id', '')}, 最大{h.get('max_amount', 0):,.0f}円)\n"
            output += "\n"

        return output

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


def sync_get_file(subsidy_id: str, filename: str, return_format: str = "markdown") -> str:
    """ファイル内容取得（同期版ラッパー）"""
    try:
        if not subsidy_id or not filename:
            return "補助金IDとファイル名を入力してください。"

        result = asyncio.run(get_file_content(
            subsidy_id.strip(),
            filename.strip(),
            return_format
        ))

        if "error" in result:
            return f"エラー: {result['error']}"

        if return_format == "markdown":
            output = f"# {result.get('filename', '')}\n\n"
            output += f"**MIMEタイプ**: {result.get('mime_type', '')}\n"
            output += f"**サイズ**: {result.get('size_bytes', 0):,} bytes\n"
            output += f"**抽出方法**: {result.get('extraction_method', 'N/A')}\n\n"
            output += "---\n\n"
            output += result.get('content_markdown', '')
            return output
        else:
            output = f"# {result.get('filename', '')}\n\n"
            output += f"**MIMEタイプ**: {result.get('mime_type', '')}\n"
            output += f"**サイズ**: {result.get('size_bytes', 0):,} bytes\n\n"
            output += "## BASE64エンコードデータ\n\n"
            output += f"```\n{result.get('content_base64', '')[:500]}...\n```\n\n"
            output += f"Data URI: `{result.get('data_uri', '')}`\n"
            return output

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


def sync_ping() -> str:
    """サーバー疎通確認（同期版ラッパー）"""
    try:
        result = asyncio.run(ping())
        return f"✅ サーバー稼働中\n\n" + json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ エラー: {str(e)}"


def list_downloaded_files() -> str:
    """ダウンロード済みファイルの一覧を表示"""
    try:
        if not FILES_DIR.exists():
            return "ファイルディレクトリが存在しません。"

        output = f"# ダウンロード済みファイル一覧\n\n"
        output += f"保存先: `{FILES_DIR}`\n\n"

        subsidy_dirs = [d for d in FILES_DIR.iterdir() if d.is_dir()]

        if not subsidy_dirs:
            return output + "\nまだファイルがダウンロードされていません。"

        for subsidy_dir in sorted(subsidy_dirs, key=lambda x: x.name):
            subsidy_id = subsidy_dir.name
            files = list(subsidy_dir.iterdir())

            if files:
                output += f"## 補助金ID: {subsidy_id}\n\n"
                for file in sorted(files, key=lambda x: x.name):
                    size = file.stat().st_size
                    output += f"- `{file.name}` ({size:,} bytes)\n"
                output += "\n"

        return output

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


def create_gradio_app():
    """Gradioアプリケーションを作成"""

    with gr.Blocks(title="Jグランツ補助金検索システム", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🏢 Jグランツ補助金検索システム

        デジタル庁が運用する補助金電子申請システム「Jグランツ」のAPIを利用した補助金検索アプリケーションです。

        **注意**: 本アプリで取得した情報を利用・公開する際は、「Jグランツ（jGrants）からの出典」である旨を明記してください。
        """)

        with gr.Tabs():
            # タブ1: 補助金検索
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
                            choices=[(0, "全て"), (1, "受付中のみ")],
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

                search_btn = gr.Button("🔍 検索実行", variant="primary")

                search_output = gr.Textbox(label="検索結果サマリー", lines=5)
                search_table = gr.Dataframe(label="検索結果テーブル")

                search_btn.click(
                    fn=sync_search_subsidies,
                    inputs=[keyword_input, industry_input, target_area_input, employees_input, sort_input, order_input, acceptance_input],
                    outputs=[search_output, search_table]
                )

            # タブ2: 詳細取得
            with gr.Tab("📄 補助金詳細"):
                gr.Markdown("### 補助金IDを入力して詳細情報を取得")

                subsidy_id_input = gr.Textbox(
                    label="補助金ID",
                    placeholder="例: a0WJ200000CDR9HMAX"
                )
                detail_btn = gr.Button("📄 詳細取得", variant="primary")
                detail_output = gr.Markdown(label="詳細情報")

                detail_btn.click(
                    fn=sync_get_detail,
                    inputs=[subsidy_id_input],
                    outputs=[detail_output]
                )

            # タブ3: 統計情報
            with gr.Tab("📊 統計情報"):
                gr.Markdown("### 補助金の統計情報を表示")

                format_input = gr.Radio(
                    label="出力形式",
                    choices=[("JSON", "json"), ("CSV", "csv")],
                    value="json"
                )
                stats_btn = gr.Button("📊 統計取得", variant="primary")
                stats_output = gr.Markdown(label="統計情報")

                stats_btn.click(
                    fn=sync_get_overview,
                    inputs=[format_input],
                    outputs=[stats_output]
                )

            # タブ4: ファイル取得
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

                file_btn = gr.Button("📁 ファイル取得", variant="primary")
                file_output = gr.Markdown(label="ファイル内容")

                file_btn.click(
                    fn=sync_get_file,
                    inputs=[file_subsidy_id, file_filename, file_format],
                    outputs=[file_output]
                )

                gr.Markdown("---")
                list_files_btn = gr.Button("📋 ダウンロード済みファイル一覧")
                files_list_output = gr.Markdown(label="ファイル一覧")

                list_files_btn.click(
                    fn=list_downloaded_files,
                    inputs=[],
                    outputs=[files_list_output]
                )

            # タブ5: サーバー情報
            with gr.Tab("ℹ️ サーバー情報"):
                gr.Markdown("### サーバーの稼働状況を確認")

                ping_btn = gr.Button("🏓 Ping", variant="primary")
                ping_output = gr.Textbox(label="サーバー応答", lines=10)

                ping_btn.click(
                    fn=sync_ping,
                    inputs=[],
                    outputs=[ping_output]
                )

                gr.Markdown("""
                ---

                ### このアプリについて

                - **ベースURL**: https://api.jgrants-portal.go.jp/exp/v1/public
                - **公式サイト**: https://www.jgrants-portal.go.jp/
                - **API仕様**: https://developers.digital.go.jp/documents/jgrants/api/

                ### 免責事項

                本アプリは技術検証を目的としたサンプルです。以下の点にご留意ください：

                - 取得した情報を利用・公開する際は「Jグランツ（jGrants）からの出典」である旨を明記してください
                - 正式な申請前に必ず公式サイトで最新情報を確認してください
                - 過度な連続アクセスは避けてください
                """)

    return demo


def launch_gradio_app(host: str = "0.0.0.0", port: int = 7860, share: bool = False):
    """Gradioアプリを起動"""
    demo = create_gradio_app()
    demo.launch(server_name=host, server_port=port, share=share)
