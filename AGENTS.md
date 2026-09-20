# AGENTS.md

Instructions for AI coding agents (opencode, Copilot CLI, Claude Code, etc.) working in this repo. See `README.md` for human-oriented docs.

## Repo shape

Small lab for OpenHAB-focused MCP servers. **No shared build system** — each subproject under `mcp-servers/` has its own toolchain and must be built/tested from inside its own directory. Don't add root-level app scaffolding; keep changes surgical within each `mcp-servers/*` project.

- `mcp-servers/openhab-python` — canonical implementation (Python, FastMCP). Launched by root `opencode.jsonc` via `uv run openhab-mcp --transport stdio`.
- `mcp-servers/openhab-java` — parallel Spring Boot implementation, same behavior.
- `skills/` — reusable Claude Skill format (`SKILL.md` + frontmatter), tool-agnostic content adaptable to other agents' own instruction formats.

Both MCP servers expose the same four tools (`get_item_state`/`getItemState`, `get_all_items`/`getAllItems`, `turn_switch`/`turnSwitch`, `toggle_switch`/`toggleSwitch`) against the OpenHAB REST API. **Keep behavior parity between them** when changing one.

## Commands

Python server (`mcp-servers/openhab-python`):
```bash
uv sync
uv run openhab-mcp                    # start (streamable-http default)
uv run openhab-mcp --transport stdio  # or sse, with --port
uv run pytest                                        # all tests
uv run pytest tests/test_<name>.py -q                # single file
uv run pytest tests/test_<name>.py -k <pattern> -q   # single test
uv run ruff check .                   # lint
uv run ruff format .                  # format
```

Java server (`mcp-servers/openhab-java`, requires Java 21):
```bash
./gradlew bootRun
./gradlew test
./gradlew test --tests "*OpenHabTools*"
./gradlew spotlessCheck   # formatting check (Google Java Format)
./gradlew spotlessApply
./gradlew bootJar
./gradlew bootBuildImage
```

## Conventions

- Trunk-based / GitHub Flow: never commit directly to `trunk`. Branch as `<type>/<kebab-description>` (`feature/`, `fix/`, `hotfix/`, `chore/`, `docs/`, `refactor/`). Commits and PR titles use Conventional Commits: `<type>(<scope>): <description>`. PRs target `trunk`, squash-merge, delete branch after merge. Full rules in `skills/git-branching-workflow/SKILL.md`.
- OpenHAB errors are returned as strings (`ERROR: <status> - <body>`), not raised, so tool output stays client-friendly — follow this pattern in both servers.
- When changing an MCP tool contract, update the corresponding project README *and* the `opencode.jsonc` config entry.
- Config: `OPENHAB_API_TOKEN` (required) and `OPENHAB_BASE_URL` (default `http://localhost:8080`) via env or a git-ignored `.env` (see each project's `.env.example`). Shell env overrides `.env`.
- `opencode.jsonc` and `.mcp.json` at repo root register the Python server, scoped to this project. `.mcp.json` is read natively by both Claude Code and GitHub Copilot CLI (same `mcpServers` schema) — uses `${HOME}` and a relative `--directory` rather than `${CLAUDE_PROJECT_DIR}` so it works unmodified across both. Keep transport/working-directory assumptions consistent between the two files if the server path or command changes.
