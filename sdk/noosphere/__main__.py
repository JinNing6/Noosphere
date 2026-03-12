"""
Noosphere MCP Server 入口

支持:
  python -m noosphere        # 启动 MCP Server
  uvx noosphere-mcp          # 通过 uvx 启动
"""

from noosphere.noosphere_mcp import main

if __name__ == "__main__":
    main()
