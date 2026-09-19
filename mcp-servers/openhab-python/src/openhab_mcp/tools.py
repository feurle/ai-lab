"""MCP tool definitions for controlling OpenHAB smart home devices."""

from __future__ import annotations

import json
import logging

from mcp.server.mcpserver import MCPServer

from openhab_mcp import __version__
from openhab_mcp.client import OpenHabClient

log = logging.getLogger(__name__)

SERVER_NAME = "mcp-openhab-server"


def create_server(client: OpenHabClient) -> MCPServer:
    """Create an MCP server whose tools operate on the given OpenHAB client."""
    mcp = MCPServer(SERVER_NAME, version=__version__)

    @mcp.tool()
    async def get_item_state(item_name: str) -> str:
        """Get the current state of an OpenHAB item by its name.
        Returns the current state as a string (e.g. "ON", "OFF").
        Use this before sending a command to check the current state.
        Example item names: 'LivingRoom_Light', 'Kitchen_Switch'.

        Args:
            item_name: The exact name of the OpenHAB item (case-sensitive)
        """
        state = await client.get_item_state(item_name)
        log.info(">>> Tool get_item_state(%s) = %s", item_name, state)
        return f"Item '{item_name}' is currently: {state}"

    @mcp.tool()
    async def get_all_items() -> str:
        """List all available OpenHAB items with their name, label, type and current state.
        Use this tool first when the user asks about their smart home devices,
        to discover which items exist and what their names are.
        """
        items = await client.get_all_items()
        log.info(">>> Tool get_all_items() returned %d items", len(items))
        return json.dumps(items, indent=2)

    @mcp.tool()
    async def turn_switch(item_name: str, command: str) -> str:
        """Send a command to an OpenHAB Switch item to turn it ON or OFF.
        Use 'ON' to turn the switch on and 'OFF' to turn it off.
        Always use get_all_items first if you don't know the exact item name.

        Args:
            item_name: The exact name of the Switch item (case-sensitive)
            command: The command to send: must be exactly 'ON' or 'OFF'
        """
        normalized = command.strip().upper()
        if normalized not in ("ON", "OFF"):
            return (
                f"ERROR: Invalid command '{command}'. "
                "Only 'ON' or 'OFF' are allowed for Switch items."
            )

        result = await client.send_command(item_name, normalized)
        log.info(">>> Tool turn_switch(%s, %s) = %s", item_name, normalized, result)
        return result

    @mcp.tool()
    async def toggle_switch(item_name: str) -> str:
        """Toggle an OpenHAB Switch item: if it's ON turn it OFF, if it's OFF turn it ON.
        Use this when the user says 'toggle', 'flip', or 'switch' without specifying on or off.

        Args:
            item_name: The exact name of the Switch item (case-sensitive)
        """
        current = await client.get_item_state(item_name)
        if "ERROR" in current:
            return f"Could not toggle: {current}"

        current = current.strip()
        new_command = "OFF" if current == "ON" else "ON"
        result = await client.send_command(item_name, new_command)
        log.info(">>> Tool toggle_switch(%s) %s -> %s", item_name, current, new_command)
        return f"Toggled '{item_name}' from {current} to {new_command}. Result: {result}"

    return mcp
