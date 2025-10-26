"""Dual Mode Launcher - MCPサーバーとGradioアプリを同時起動"""

import argparse
import threading
import logging
import time
from typing import Optional

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_mcp_server(host: str = "127.0.0.1", port: int = 8000):
    """MCPサーバーを起動"""
    try:
        logger.info(f"Starting MCP Server on {host}:{port}")
        from .core import mcp
        mcp.run(transport="streamable-http", host=host, port=port)
    except Exception as e:
        logger.error(f"MCP Server error: {e}", exc_info=True)


def run_gradio_app(host: str = "0.0.0.0", port: int = 7860, share: bool = False):
    """Gradioアプリを起動"""
    try:
        logger.info(f"Starting Gradio App on {host}:{port}")
        from .gradio_app import launch_gradio_app
        launch_gradio_app(host=host, port=port, share=share)
    except Exception as e:
        logger.error(f"Gradio App error: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(
        description="Jグランツ MCP Server & Gradio App デュアルモード起動"
    )

    # モード選択
    parser.add_argument(
        "--mode",
        choices=["mcp", "gradio", "both"],
        default="both",
        help="起動モード: mcp (MCPサーバーのみ), gradio (Gradioアプリのみ), both (両方)"
    )

    # MCPサーバー設定
    parser.add_argument(
        "--mcp-host",
        default="127.0.0.1",
        help="MCPサーバーのホスト (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--mcp-port",
        type=int,
        default=8000,
        help="MCPサーバーのポート (default: 8000)"
    )

    # Gradioアプリ設定
    parser.add_argument(
        "--gradio-host",
        default="0.0.0.0",
        help="Gradioアプリのホスト (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--gradio-port",
        type=int,
        default=7860,
        help="Gradioアプリのポート (default: 7860)"
    )
    parser.add_argument(
        "--gradio-share",
        action="store_true",
        help="Gradio公開リンクを生成"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Jグランツ補助金検索システム 起動中...")
    logger.info("=" * 60)

    threads = []

    if args.mode in ["mcp", "both"]:
        logger.info(f"✓ MCPサーバーモード: http://{args.mcp_host}:{args.mcp_port}/mcp")
        mcp_thread = threading.Thread(
            target=run_mcp_server,
            args=(args.mcp_host, args.mcp_port),
            daemon=True
        )
        threads.append(mcp_thread)
        mcp_thread.start()

    if args.mode in ["gradio", "both"]:
        # MCPサーバーが起動するまで少し待つ
        if args.mode == "both":
            time.sleep(2)

        logger.info(f"✓ Gradioアプリモード: http://{args.gradio_host}:{args.gradio_port}")
        gradio_thread = threading.Thread(
            target=run_gradio_app,
            args=(args.gradio_host, args.gradio_port, args.gradio_share),
            daemon=False  # Gradioはメインスレッド扱い
        )
        threads.append(gradio_thread)
        gradio_thread.start()

    logger.info("=" * 60)
    logger.info("✅ すべてのサーバーが起動しました")
    logger.info("=" * 60)

    if args.mode in ["gradio", "both"]:
        logger.info(f"\n📱 Gradio UI: http://localhost:{args.gradio_port}")
    if args.mode in ["mcp", "both"]:
        logger.info(f"🔌 MCP Endpoint: http://localhost:{args.mcp_port}/mcp")

    logger.info("\n終了するには Ctrl+C を押してください\n")

    # メインスレッドを維持
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        logger.info("\n停止中...")
        logger.info("サーバーを終了しました。")


if __name__ == "__main__":
    main()
