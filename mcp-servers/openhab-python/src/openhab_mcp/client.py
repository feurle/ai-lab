"""HTTP client for the OpenHAB REST API.

Provides methods to query item states, list all items, and send commands to
devices. Errors from OpenHAB are returned as strings prefixed with ``ERROR:``
(mirroring the original Java implementation) rather than raised, so tool
results always reach the LLM.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)


class OpenHabClient:
    """Thin async wrapper around the OpenHAB REST API."""

    def __init__(self, base_url: str, api_token: str, timeout: float = 10.0) -> None:
        # Accept/Content-Type are set per request: the /state endpoint returns
        # text/plain and OpenHAB 5 answers 400 if a JSON response is requested.
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def get_item_state(self, item_name: str) -> str:
        """Return the current state of an item (e.g. "ON", "OFF") or an ERROR string."""
        log.info("Fetching state for item: %s", item_name)
        try:
            response = await self._http.get(
                f"/rest/items/{item_name}/state", headers={"Accept": "text/plain"}
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as exc:
            return self._error("fetching state for %s", item_name, exc)
        except httpx.HTTPError as exc:
            return self._transport_error(exc)

    async def get_all_items(self) -> list[dict[str, Any]]:
        """Return all items with name, label, type and state, or ``[{"error": ...}]``."""
        log.info("Fetching all items")
        try:
            response = await self._http.get(
                "/rest/items",
                params={"fields": "name,label,type,state"},
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            log.error("Error fetching all items: %s", exc.response.text)
            return [{"error": exc.response.text}]
        except httpx.HTTPError as exc:
            log.error("Error fetching all items: %s", exc)
            return [{"error": str(exc)}]

    async def send_command(self, item_name: str, command: str) -> str:
        """Send a command (e.g. "ON") to an item. Returns an OK or ERROR string."""
        log.info("Sending command '%s' to item: %s", command, item_name)
        try:
            response = await self._http.post(
                f"/rest/items/{item_name}",
                content=command,
                headers={"Content-Type": "text/plain"},
            )
            response.raise_for_status()
            return f"OK: Command '{command}' sent to {item_name}"
        except httpx.HTTPStatusError as exc:
            return self._error("sending command to %s", item_name, exc)
        except httpx.HTTPError as exc:
            return self._transport_error(exc)

    @staticmethod
    def _error(what: str, item_name: str, exc: httpx.HTTPStatusError) -> str:
        status = exc.response.status_code
        body = exc.response.text
        log.error("Error " + what + ": %s %s", item_name, status, body)
        return f"ERROR: {status} - {body}"

    @staticmethod
    def _transport_error(exc: httpx.HTTPError) -> str:
        log.error("HTTP error talking to OpenHAB: %s", exc)
        return f"ERROR: {exc.__class__.__name__} - {exc}"
