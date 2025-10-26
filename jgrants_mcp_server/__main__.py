"""Entry point for running jgrants_mcp_server as a module

Uses Gradio 5's native MCP server support for unified web UI + MCP server functionality.
"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Jグランツ補助金検索システム (Gradio 5 + MCP統合)"
    )

    # Server configuration
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Server port (default: 7860)"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create public Gradio link"
    )
    parser.add_argument(
        "--no-mcp",
        action="store_true",
        help="Disable MCP server mode (Gradio UI only)"
    )

    args = parser.parse_args()

    # Launch Gradio app with native MCP support
    from .gradio_mcp_app import launch_app

    launch_app(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        mcp_server=not args.no_mcp
    )


if __name__ == "__main__":
    main()
