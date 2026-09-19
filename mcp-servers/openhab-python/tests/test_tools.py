import json

import pytest

from openhab_mcp.tools import create_server


@pytest.fixture
def server(fake_client):
    return create_server(fake_client)


async def test_registers_expected_tools(server):
    names = {t.name for t in await server.list_tools()}
    assert names == {"get_item_state", "get_all_items", "turn_switch", "toggle_switch"}


async def test_get_item_state(server):
    result = await server.call_tool("get_item_state", {"item_name": "LivingRoom_Light"})
    assert result.content[0].text == "Item 'LivingRoom_Light' is currently: ON"


async def test_get_all_items_returns_json(server, fake_client):
    result = await server.call_tool("get_all_items", {})
    items = json.loads(result.content[0].text)
    assert {i["name"] for i in items} == set(fake_client.states)


@pytest.mark.parametrize("raw", ["on", " ON ", "Off"])
async def test_turn_switch_normalizes_command(server, fake_client, raw):
    result = await server.call_tool("turn_switch", {"item_name": "Kitchen_Switch", "command": raw})
    expected = raw.strip().upper()
    assert result.content[0].text == f"OK: Command '{expected}' sent to Kitchen_Switch"
    assert fake_client.commands == [("Kitchen_Switch", expected)]


async def test_turn_switch_rejects_invalid_command(server, fake_client):
    result = await server.call_tool(
        "turn_switch", {"item_name": "Kitchen_Switch", "command": "DIM"}
    )
    assert result.content[0].text == (
        "ERROR: Invalid command 'DIM'. Only 'ON' or 'OFF' are allowed for Switch items."
    )
    assert fake_client.commands == []


async def test_toggle_switch_on_to_off(server, fake_client):
    result = await server.call_tool("toggle_switch", {"item_name": "LivingRoom_Light"})
    assert result.content[0].text == (
        "Toggled 'LivingRoom_Light' from ON to OFF. "
        "Result: OK: Command 'OFF' sent to LivingRoom_Light"
    )
    assert fake_client.states["LivingRoom_Light"] == "OFF"


async def test_toggle_switch_off_to_on(server, fake_client):
    result = await server.call_tool("toggle_switch", {"item_name": "Kitchen_Switch"})
    assert result.content[0].text.startswith("Toggled 'Kitchen_Switch' from OFF to ON.")


async def test_toggle_switch_unknown_item(server, fake_client):
    result = await server.call_tool("toggle_switch", {"item_name": "Ghost"})
    assert result.content[0].text == "Could not toggle: ERROR: 404 - Item not found"
    assert fake_client.commands == []
