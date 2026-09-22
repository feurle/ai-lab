# Changelog

Alle nennenswerten Änderungen an diesem Repo werden hier dokumentiert.
Format angelehnt an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0] - 2026-09-22

### Added

- `mcp-servers/openhab-python/install-user.sh` / `uninstall-user.sh` registrieren den Python-OpenHAB-Server benutzerweit bei Claude Code, GitHub Copilot CLI und opencode.
- Der Python-Server liest `OPENHAB_API_TOKEN` / `OPENHAB_BASE_URL` zusätzlich aus der benutzerweiten Datei `~/.config/openhab-mcp/.env` (respektiert `XDG_CONFIG_HOME`; Priorität: Shell-Env > Projekt-`.env` > User-Datei). `install-user.sh` legt sie bei Bedarf interaktiv mit Modus `600` an, sodass der Token in keiner MCP-Client-Config landet.
- `mcp-servers/chrome-devtools/install-user.sh` / `uninstall-user.sh` installieren `chrome-devtools-mcp` nur für den aktuellen User (npm nach `~/.local`) und registrieren es bei Claude Code, GitHub Copilot CLI und opencode.

### Changed

- MCP-Server werden nur noch benutzerweit über die `install-user.sh`-Skripte registriert; nach dem Klonen einmal `mcp-servers/openhab-python/install-user.sh` ausführen.

### Removed

- Projektweite MCP-Konfiguration `opencode.jsonc` und `.mcp.json` im Repo-Root entfernt.

## [0.1.0] - 2026-09-20

### Added

- `AGENTS.md` als zentrale Instruktionsdatei für KI-Coding-Agents (Repo-Struktur, Befehle, Konventionen) ergänzt.
- `git-branching-workflow` und `updating-changelog` sind jetzt zusätzlich unter `.claude/skills/` im Projekt verlinkt, damit Claude Code sie in diesem Repo automatisch lädt.
- `scripts/install-skills.sh` / `scripts/uninstall-skills.sh` ergänzt, um alle Skills global unter `~/.claude/skills/` (Claude Code) bzw. `~/.agents/skills/` (opencode, GitHub Copilot CLI) zu (de)installieren.

### Changed

- `updating-changelog`-Skill präzisiert: Einträge werden im Feature-/Fix-/Hotfix-Branch selbst ergänzt (als Teil des PRs), nicht nachträglich auf `trunk`; falsche `deploy.sh`-Automatik-Referenz entfernt; Hinweis zum Umgang mit Merge-Konflikten in `CHANGELOG.md` ergänzt.
- Der Changelog-Prozess für dieses Repo ist jetzt verbindlich dokumentiert: Änderungen in `CHANGELOG.md` landen im selben Branch wie der Code-PR und werden bei Konflikten gemeinsam mit beiden Einträgen erhalten.

### Deprecated

### Removed

### Fixed

### Security
