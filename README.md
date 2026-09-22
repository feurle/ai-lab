# ai-lab

Current release: [v0.2.0](https://github.com/feurle/ai-lab/releases/tag/v0.2.0) (2026-09-22). See [CHANGELOG.md](CHANGELOG.md) for details.

A small lab for OpenHAB-focused MCP (Model Context Protocol) servers. There is no shared build system — each subproject under `mcp-servers/` has its own toolchain and must be built/tested from within its own directory.

- `mcp-servers/openhab-python` is the canonical, Python-based MCP server. Its `install-user.sh` registers it (stdio transport) with Claude Code, GitHub Copilot CLI and opencode for the current user.
- `mcp-servers/openhab-java` is a parallel Spring Boot implementation of the same idea, useful as a reference or alternative deployment.
- `mcp-servers/chrome-devtools` contains helper scripts/docs to install `chrome-devtools-mcp` for the current user only (npm install into `~/.local`, plus per-user MCP config entries).

Both implementations talk to an OpenHAB instance through its REST API and require an API token plus the base URL. They expose the same four tools (`get_item_state`/`getItemState`, `get_all_items`/`getAllItems`, `turn_switch`/`turnSwitch`, `toggle_switch`/`toggleSwitch`); keep behavior parity between them when changing one.

The repo root also holds reusable `skills/` in Anthropic's Claude Skill format (`SKILL.md` with YAML frontmatter, optional `references/`). That format is currently auto-loaded by Claude Code / Claude apps, but the instructional content itself is tool-agnostic and can be adapted into Copilot custom instructions, opencode config, or any other coding agent's own format:
- `git-branching-workflow` — mandatory trunk-based / GitHub Flow with Conventional Commits: never commit directly to `trunk`; branch as `<type>/<kebab-description>` (`feature/`, `fix/`, `hotfix/`, `chore/`, `docs/`, `refactor/`); commits and PR titles follow `<type>(<scope>): <description>`; PRs target `trunk`, squash-merge by default, delete branch after merge.
- `ddd-architect` — Domain-Driven Design modeling skill (strategic + tactical design, EventStorming, Java/Spring scaffolding); reference material under `skills/ddd-architect/references/`.

Run `scripts/install-skills.sh` to symlink these skills into the global, per-user skill directories that Claude Code (`~/.claude/skills/`), opencode, and GitHub Copilot CLI (both `~/.agents/skills/`) auto-discover, so they're available in every project, not just this one. `scripts/uninstall-skills.sh` removes them again.

## Python MCP server (`mcp-servers/openhab-python`)

Built on the official `mcp` SDK (FastMCP) and `httpx`. Pins Python 3.11+, uses `uv`, dev dependencies in `pyproject.toml`.

Layout (`src/openhab_mcp/`):
- `config.py` — env-based configuration (`OPENHAB_API_TOKEN`, `OPENHAB_BASE_URL`, transport settings)
- `client.py` — wraps the OpenHAB REST API via `httpx`
- `tools.py` — FastMCP tools exposed to clients (`get_item_state`, `get_all_items`, `turn_switch`, `toggle_switch`)
- `server.py` — CLI entry point (`openhab-mcp`)
- `tests/` — pytest, mocks OpenHAB responses with `respx`

Runs over `streamable-http` (default, `http://0.0.0.0:8081/mcp`), `sse`, or `stdio`.

```bash
cd mcp-servers/openhab-python
uv sync
uv run openhab-mcp                    # start server
uv run openhab-mcp --transport stdio  # or sse, with --port
uv run pytest                         # all tests
uv run pytest tests/test_<name>.py -q                # single test file
uv run pytest tests/test_<name>.py -k <pattern> -q    # single test by pattern
uv run ruff check .                   # lint
uv run ruff format .                  # format
```

OpenHAB failures are returned as strings like `ERROR: <status> - <body>` instead of being raised, so tool output stays client-friendly.

## Java MCP server (`mcp-servers/openhab-java`)

Spring Boot 4 / Spring WebFlux app using Spring AI's MCP integration, following the same flow as the Python server. Requires Java 21. Listens on `http://localhost:8081/sse`.

Key files (`src/main/java/com/feurle/ai/mcp/`):
- `McpOpenhabServer.java` — Spring Boot entry point
- `config/OpenHabConfig.java` — binds `openhab.base-url` / `openhab.api-token`
- `config/McpServerConfig.java` — registers `OpenHabTools` as MCP tool callbacks
- `client/OpenHabClient.java` — reactive `WebClient` wrapper for the OpenHAB REST API
- `tools/OpenHabTools.java` — `@Tool`-annotated methods exposed to AI clients

```bash
cd mcp-servers/openhab-java
./gradlew bootRun          # start server
./gradlew test             # all tests
./gradlew test --tests "*OpenHabTools*"          # single test class
./gradlew test --tests "com.feurle.ai.mcp.*"     # package pattern
./gradlew spotlessCheck    # check formatting (Google Java Format via Spotless)
./gradlew spotlessApply    # apply formatting
./gradlew bootJar          # build executable jar (build/libs/)
./gradlew bootBuildImage   # build Docker image
```

## Configuration

Both servers read `OPENHAB_API_TOKEN` (required) and `OPENHAB_BASE_URL` (default `http://localhost:8080`) from the environment or a git-ignored `.env` file (see `.env.example` in each project). Shell environment variables override `.env` values. The Python server also falls back to a per-user `~/.config/openhab-mcp/.env`, which `mcp-servers/openhab-python/install-user.sh` creates when registering the server user-wide (Python server only). The repo deliberately ships no project-scoped MCP client config (`.mcp.json`, `opencode.jsonc`). Register servers once per user with the `install-user.sh` script in `mcp-servers/openhab-python` or `mcp-servers/chrome-devtools`; they are then available in every project.

## Conventions

- Root-level configuration is intentionally minimal; don't add broad app scaffolding here unless the repo is intentionally expanded.
- When changing an MCP tool contract, update the corresponding project README and, if the launch command changes, the server's `install-user.sh`.
- Prefer surgical changes within each `mcp-servers/*` project rather than root-level changes; this is not a conventional full-stack app.
