"""Entry point: wires settings, OpenHAB client and the MCP server together."""

from __future__ import annotations

import argparse
import logging
import sys

from openhab_mcp.client import OpenHabClient
from openhab_mcp.config import TRANSPORTS, ConfigError, Settings
from openhab_mcp.tools import create_server


def _parse_args(argv: list[str] | None, defaults: Settings) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="openhab-mcp",
        description="MCP server exposing OpenHAB items as tools. "
        "Configure the OpenHAB connection via OPENHAB_BASE_URL and OPENHAB_API_TOKEN.",
    )
    parser.add_argument(
        "--transport",
        choices=TRANSPORTS,
        default=defaults.transport,
        help=f"MCP transport (default: {defaults.transport}, env MCP_TRANSPORT)",
    )
    parser.add_argument(
        "--host",
        default=defaults.host,
        help=f"Bind address for http transports (default: {defaults.host}, env MCP_HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=defaults.port,
        help=f"Port for http transports (default: {defaults.port}, env MCP_PORT)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    # Log to stderr only: stdout is the protocol channel for the stdio transport.
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger(__name__)

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    args = _parse_args(argv, settings)

    client = OpenHabClient(settings.base_url, settings.api_token)
    mcp = create_server(client)

    log.info("Starting %s (transport=%s, openhab=%s)", mcp.name, args.transport, settings.base_url)
    if args.transport == "stdio":
        mcp.run(transport="stdio")
        return

    path = "/mcp" if args.transport == "streamable-http" else "/sse"
    log.info("Listening on http://%s:%d%s", args.host, args.port, path)
    mcp.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
