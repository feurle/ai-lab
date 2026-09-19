# OpenHAB MCP Server (Python)

A Python **Model Context Protocol (MCP) server** for controlling OpenHAB smart home devices through
AI/LLM clients. This is the Python port of the Spring Boot `mcp-openhab-server`, built on the official
[`mcp`](https://github.com/modelcontextprotocol/python-sdk) SDK (FastMCP) and `httpx`.

## Prerequisites

- **Python 3.11+** and [`uv`](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A reachable **OpenHAB** instance
- An OpenHAB **API token** (OpenHAB → Settings → Users → create API token)

## Quick Start

```bash
cd mcp-servers/openhab-python
cp .env.example .env        # then put your OPENHAB_API_TOKEN into .env
uv run openhab-mcp
```

Alternatively export the variables in your shell (`export OPENHAB_API_TOKEN=...`); shell
variables take precedence over `.env`.

The server listens on `http://0.0.0.0:8081/mcp` (streamable-http) by default.

## Configuration

Everything is configured via environment variables, read from the shell or from a `.env` file in the
project directory (see `.env.example`; `.env` is git-ignored). CLI flags override the transport settings.

| Variable            | Default                     | Description                                        |
|---------------------|-----------------------------|----------------------------------------------------|
| `OPENHAB_API_TOKEN` | *(required)*                | Bearer token for the OpenHAB REST API              |
| `OPENHAB_BASE_URL`  | `http://openhab.feurle.com` | Base URL of your OpenHAB instance                  |
| `MCP_TRANSPORT`     | `streamable-http`           | `streamable-http`, `sse` or `stdio`                |
| `MCP_HOST`          | `0.0.0.0`                   | Bind address (http transports only)                |
| `MCP_PORT`          | `8081`                      | Port (http transports only)                        |

```bash
# Different OpenHAB host
OPENHAB_API_TOKEN=... OPENHAB_BASE_URL=http://192.168.1.100:8080 uv run openhab-mcp

# Legacy SSE transport on another port
uv run openhab-mcp --transport sse --port 9000

# stdio (client spawns the process)
uv run openhab-mcp --transport stdio
```

## MCP Client Configuration

**HTTP (server already running):**

```json
{
  "mcpServers": {
    "openhab": {
      "url": "http://localhost:8081/mcp"
    }
  }
}
```

For `--transport sse` use `"url": "http://localhost:8081/sse"`.

**stdio (client launches the server):**

```json
{
  "mcpServers": {
    "openhab": {
      "command": "uv",
      "args": [
        "--directory", "/absolute/path/to/ai-lab/mcp-servers/openhab-python",
        "run", "openhab-mcp", "--transport", "stdio"
      ],
      "env": {
        "OPENHAB_API_TOKEN": "your-api-token-here",
        "OPENHAB_BASE_URL": "http://openhab.feurle.com"
      }
    }
  }
}
```

With Claude Code: `claude mcp add openhab --transport http http://localhost:8081/mcp`.

## Available Tools

| Tool             | Description                                                           |
|------------------|-----------------------------------------------------------------------|
| `get_item_state` | Get the current state of an item (e.g. `ON`, `OFF`)                   |
| `get_all_items`  | List all items with name, label, type and state (JSON)                |
| `turn_switch`    | Send `ON` or `OFF` to a Switch item                                   |
| `toggle_switch`  | Read the current state and send the opposite command                  |

OpenHAB errors are returned to the client as `ERROR: <status> - <body>` strings rather than raised.

## Development

```bash
uv sync                # create .venv and install deps (incl. dev group)
uv run pytest          # run tests
uv run ruff check .    # lint
uv run ruff format .   # format
```

Layout:

```
src/openhab_mcp/
├── config.py   # Settings from env vars
├── client.py   # httpx wrapper for the OpenHAB REST API
├── tools.py    # FastMCP server + tool definitions
└── server.py   # CLI entry point (openhab-mcp)
tests/          # pytest (respx mocks the OpenHAB REST API)
```

## Troubleshooting

- **`error: OPENHAB_API_TOKEN is not set`** — export the token before starting (see Quick Start).
- **`ERROR: 401 - ...` in tool results** — token is invalid or expired; create a new one in OpenHAB.
- **`ERROR: ConnectError - ...`** — OpenHAB is not reachable; check `OPENHAB_BASE_URL` and `curl $OPENHAB_BASE_URL/rest/items`.
- **Client cannot connect over HTTP** — make sure the URL ends with `/mcp` (streamable-http) or `/sse` (sse) and matches `--transport`.

## Resources

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [OpenHAB REST API](https://www.openhab.org/docs/configuration/restdocs.html)
