"""Runtime configuration, read from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import find_dotenv, load_dotenv

DEFAULT_BASE_URL = "http://openhab.feurle.com"
DEFAULT_TRANSPORT = "streamable-http"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8081

TRANSPORTS = ("streamable-http", "sse", "stdio")


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    """Settings for the OpenHAB connection and the MCP transport."""

    base_url: str
    api_token: str
    transport: str = DEFAULT_TRANSPORT
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from the environment.

        A ``.env`` file in the current directory (or a parent) is loaded first;
        variables already present in the environment take precedence.

        Env vars: OPENHAB_BASE_URL, OPENHAB_API_TOKEN (required),
        MCP_TRANSPORT, MCP_HOST, MCP_PORT.
        """
        load_dotenv(find_dotenv(usecwd=True), override=False)

        token = os.environ.get("OPENHAB_API_TOKEN", "").strip()
        if not token:
            raise ConfigError(
                "OPENHAB_API_TOKEN is not set. Create an API token in OpenHAB "
                "(Settings -> Users) and export it before starting the server."
            )

        transport = os.environ.get("MCP_TRANSPORT", DEFAULT_TRANSPORT)
        if transport not in TRANSPORTS:
            raise ConfigError(
                f"Invalid MCP_TRANSPORT '{transport}'. Must be one of: {', '.join(TRANSPORTS)}"
            )

        port_raw = os.environ.get("MCP_PORT", str(DEFAULT_PORT))
        try:
            port = int(port_raw)
        except ValueError as exc:
            raise ConfigError(f"Invalid MCP_PORT '{port_raw}': must be an integer") from exc

        return cls(
            base_url=os.environ.get("OPENHAB_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            api_token=token,
            transport=transport,
            host=os.environ.get("MCP_HOST", DEFAULT_HOST),
            port=port,
        )
