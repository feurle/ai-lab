from __future__ import annotations

from typing import Any

import pytest


class FakeOpenHabClient:
    """In-memory stand-in for OpenHabClient used by the tool tests."""

    def __init__(self, states: dict[str, str] | None = None) -> None:
        self.states: dict[str, str] = states or {}
        self.commands: list[tuple[str, str]] = []
        self.fail_commands = False

    async def get_item_state(self, item_name: str) -> str:
        if item_name not in self.states:
            return "ERROR: 404 - Item not found"
        return self.states[item_name]

    async def get_all_items(self) -> list[dict[str, Any]]:
        return [
            {"name": name, "label": name.replace("_", " "), "type": "Switch", "state": state}
            for name, state in self.states.items()
        ]

    async def send_command(self, item_name: str, command: str) -> str:
        self.commands.append((item_name, command))
        if self.fail_commands:
            return "ERROR: 500 - boom"
        self.states[item_name] = command
        return f"OK: Command '{command}' sent to {item_name}"


@pytest.fixture
def fake_client() -> FakeOpenHabClient:
    return FakeOpenHabClient({"LivingRoom_Light": "ON", "Kitchen_Switch": "OFF"})


@pytest.fixture(autouse=True)
def _isolate_from_dotenv(monkeypatch, tmp_path):
    """Run tests from an empty directory so a developer's .env files are never picked up."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
