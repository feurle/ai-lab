import httpx
import pytest
import respx

from openhab_mcp.client import OpenHabClient

BASE = "http://openhab.test"


@pytest.fixture
async def client():
    c = OpenHabClient(BASE, "secret-token")
    yield c
    await c.aclose()


@respx.mock
async def test_get_item_state_success(client):
    route = respx.get(f"{BASE}/rest/items/LivingRoom_Light/state").mock(
        return_value=httpx.Response(200, text="ON")
    )

    assert await client.get_item_state("LivingRoom_Light") == "ON"

    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer secret-token"
    # OpenHAB 5 rejects Accept: application/json on the text/plain /state endpoint
    assert request.headers["Accept"] == "text/plain"
    assert "Content-Type" not in request.headers


@respx.mock
async def test_get_item_state_http_error(client):
    respx.get(f"{BASE}/rest/items/Nope/state").mock(
        return_value=httpx.Response(404, text="Item not found")
    )

    assert await client.get_item_state("Nope") == "ERROR: 404 - Item not found"


@respx.mock
async def test_get_item_state_connection_error(client):
    respx.get(f"{BASE}/rest/items/X/state").mock(side_effect=httpx.ConnectError("refused"))

    result = await client.get_item_state("X")

    assert result.startswith("ERROR: ConnectError")


@respx.mock
async def test_get_all_items_success(client):
    items = [{"name": "A", "label": "A", "type": "Switch", "state": "ON"}]
    route = respx.get(f"{BASE}/rest/items", params={"fields": "name,label,type,state"}).mock(
        return_value=httpx.Response(200, json=items)
    )

    assert await client.get_all_items() == items
    assert route.calls.last.request.headers["Accept"] == "application/json"


@respx.mock
async def test_get_all_items_error(client):
    respx.get(f"{BASE}/rest/items").mock(return_value=httpx.Response(401, text="Unauthorized"))

    assert await client.get_all_items() == [{"error": "Unauthorized"}]


@respx.mock
async def test_send_command_success(client):
    route = respx.post(f"{BASE}/rest/items/Kitchen_Switch").mock(return_value=httpx.Response(200))

    assert await client.send_command("Kitchen_Switch", "ON") == (
        "OK: Command 'ON' sent to Kitchen_Switch"
    )

    request = route.calls.last.request
    assert request.content == b"ON"
    assert request.headers["Content-Type"] == "text/plain"


@respx.mock
async def test_send_command_error(client):
    respx.post(f"{BASE}/rest/items/Kitchen_Switch").mock(
        return_value=httpx.Response(400, text="Bad command")
    )

    assert await client.send_command("Kitchen_Switch", "BLAH") == "ERROR: 400 - Bad command"
