# Chrome DevTools MCP

Helper scripts to install [`chrome-devtools-mcp`](https://www.npmjs.com/package/chrome-devtools-mcp)
**for the current user only** — no `sudo`, nothing written under `/usr/local`.

- package: `chrome-devtools-mcp` (npm)
- binary after install: `~/.local/bin/chrome-devtools-mcp`

## User-wide install

From this folder:

```bash
./install-user.sh
```

What it does:

1. `npm install --prefix ~/.local --global chrome-devtools-mcp@latest`
   → binary lands in `~/.local/bin/`, alongside `uv` and `claude`
2. Registers the server per user with each tool:

| Tool | How | Lands in |
| --- | --- | --- |
| Claude Code | `claude mcp add -s user` | `~/.claude.json` (`mcpServers`) |
| GitHub Copilot CLI | `copilot mcp add` | `~/.copilot/mcp-config.json` (`mcpServers`) |
| opencode | config file edit | `~/.config/opencode/opencode.jsonc` (`mcp`) |

Claude Code and Copilot CLI are configured through their own CLIs rather than by
editing their JSON directly — both files are tool-managed (`~/.claude.json`
holds far more than MCP config, so a script rewriting it could clobber a running
session). opencode's `opencode mcp add` is interactive and has no `remove`
counterpart, so its config file is edited instead.

### Why three places instead of one shared `~/.mcp.json`

`.mcp.json` is a *project-root* file. No tool reads `~/.mcp.json` as a global
config — an entry placed there never shows up in `claude mcp list`. Claude
Code's user scope is `~/.claude.json`, Copilot CLI keeps its own
`~/.copilot/mcp-config.json`, and opencode's `mcp` schema (`type: "local"`,
`command: [...]`) is structurally different from `mcpServers`, so the content
isn't shareable anyway.

Notes:

- All entries use the absolute path to the binary, so it works even if
  `~/.local/bin` is not on `PATH`.
- Tools that aren't installed are skipped silently.
- If the opencode config contains real JSONC comments it cannot be edited
  safely and is left untouched; the script prints the snippet to paste in.
- Existing unrelated MCP entries are preserved; re-running is idempotent.

## User-wide uninstall

```bash
./uninstall-user.sh
```

Runs `claude mcp remove -s user chrome-devtools` and
`copilot mcp remove chrome-devtools`, drops the entry from the opencode config
and from the legacy `~/.mcp.json` (written by an earlier version of the install
script), then `npm uninstall --prefix ~/.local --global chrome-devtools-mcp`.

## Verify

```bash
~/.local/bin/chrome-devtools-mcp --version
claude mcp list | grep chrome-devtools
copilot mcp get chrome-devtools
cat ~/.config/opencode/opencode.jsonc
```
