import pytest

from openhab_mcp.config import DEFAULT_BASE_URL, DEFAULT_PORT, ConfigError, Settings


def test_from_env_requires_token(monkeypatch):
    monkeypatch.delenv("OPENHAB_API_TOKEN", raising=False)
    with pytest.raises(ConfigError, match="OPENHAB_API_TOKEN"):
        Settings.from_env()


def test_from_env_defaults(monkeypatch):
    monkeypatch.setenv("OPENHAB_API_TOKEN", "tok")
    for var in ("OPENHAB_BASE_URL", "MCP_TRANSPORT", "MCP_HOST", "MCP_PORT"):
        monkeypatch.delenv(var, raising=False)

    s = Settings.from_env()

    assert s.api_token == "tok"
    assert s.base_url == DEFAULT_BASE_URL
    assert s.transport == "streamable-http"
    assert s.port == DEFAULT_PORT


def test_from_env_overrides_and_strips_trailing_slash(monkeypatch):
    monkeypatch.setenv("OPENHAB_API_TOKEN", "tok")
    monkeypatch.setenv("OPENHAB_BASE_URL", "http://192.168.1.10:8080/")
    monkeypatch.setenv("MCP_TRANSPORT", "stdio")
    monkeypatch.setenv("MCP_PORT", "9000")

    s = Settings.from_env()

    assert s.base_url == "http://192.168.1.10:8080"
    assert s.transport == "stdio"
    assert s.port == 9000


@pytest.mark.parametrize(
    ("var", "value"),
    [("MCP_TRANSPORT", "websocket"), ("MCP_PORT", "eighty")],
)
def test_from_env_rejects_invalid_values(monkeypatch, var, value):
    monkeypatch.setenv("OPENHAB_API_TOKEN", "tok")
    monkeypatch.setenv(var, value)
    with pytest.raises(ConfigError, match=var):
        Settings.from_env()


def test_from_env_loads_dotenv_file(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENHAB_API_TOKEN", raising=False)
    monkeypatch.delenv("OPENHAB_BASE_URL", raising=False)
    (tmp_path / ".env").write_text(
        "OPENHAB_API_TOKEN=from-dotenv\nOPENHAB_BASE_URL=http://dotenv.example\n"
    )

    s = Settings.from_env()

    assert s.api_token == "from-dotenv"
    assert s.base_url == "http://dotenv.example"


def _write_user_env(tmp_path, text):
    path = tmp_path / "xdg" / "openhab-mcp" / ".env"
    path.parent.mkdir(parents=True)
    path.write_text(text)


def test_from_env_loads_user_env_file(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENHAB_API_TOKEN", raising=False)
    monkeypatch.delenv("OPENHAB_BASE_URL", raising=False)
    _write_user_env(tmp_path, "OPENHAB_API_TOKEN=from-user\nOPENHAB_BASE_URL=http://user.example\n")

    s = Settings.from_env()

    assert s.api_token == "from-user"
    assert s.base_url == "http://user.example"


def test_project_dotenv_wins_over_user_env_file(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENHAB_API_TOKEN", raising=False)
    monkeypatch.delenv("OPENHAB_BASE_URL", raising=False)
    _write_user_env(tmp_path, "OPENHAB_API_TOKEN=from-user\nOPENHAB_BASE_URL=http://user.example\n")
    (tmp_path / ".env").write_text("OPENHAB_API_TOKEN=from-dotenv\n")

    s = Settings.from_env()

    assert s.api_token == "from-dotenv"
    assert s.base_url == "http://user.example"


def test_environment_wins_over_env_files(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENHAB_API_TOKEN", "from-shell")
    _write_user_env(tmp_path, "OPENHAB_API_TOKEN=from-user\n")
    (tmp_path / ".env").write_text("OPENHAB_API_TOKEN=from-dotenv\n")

    assert Settings.from_env().api_token == "from-shell"
