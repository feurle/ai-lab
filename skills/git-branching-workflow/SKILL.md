---
name: "git-branching-workflow"
description: "Verbindlicher Branching- und Commit-Workflow (Trunk-based/GitHub Flow + Conventional Commits) für alle Projekte des Users. Anwenden bei jeder Arbeit mit Git: Branches erstellen, committen, PRs öffnen/mergen."
---

# Git Branching & Commit Workflow

Dies ist der verbindliche Git-Workflow für alle Projekte des Users. Bei jeder Arbeit mit Git (Branch erstellen, committen, PR öffnen/mergen) gilt dieses Regelwerk, sofern ein Projekt nicht explizit etwas anderes vorgibt (z.B. eine CONTRIBUTING.md im Repo, die Vorrang hat).

## Grundmodell: Trunk-based / GitHub Flow

- `trunk` ist immer deploybar. Es wird **nie direkt auf `trunk` committet**.
- Für jede in sich abgeschlossene Änderung wird ein kurzlebiger Branch von `trunk` abgezweigt.
- Kein separater `develop`-Branch. Kein Git Flow mit `release/*`-Branches.
- Branches sollen möglichst kurzlebig sein (Tage, nicht Wochen) — lieber kleine PRs als ein riesiger Branch.
- Ein Branch, der lange lebt, wird regelmäßig mit `trunk` aktuell gehalten (merge oder rebase von `trunk` rein), um Merge-Konflikte klein zu halten.

## Branch-Typen & Naming

Format: `<type>/<kurzbeschreibung-in-kebab-case>`, optional mit Ticket-Nummer: `<type>/<TICKET-ID>-<kurzbeschreibung>`

| Typ | Präfix | Verwendung |
|---|---|---|
| Feature | `feature/` | Neue Funktionalität |
| Fix | `fix/` | Bugfix (nicht dringend) |
| Hotfix | `hotfix/` | Dringender Fix, der schnell nach `trunk` und in Produktion muss |
| Chore | `chore/` | Wartung, Dependency-Updates, Tooling, Config |
| Docs | `docs/` | Reine Doku-Änderungen |
| Refactor | `refactor/` | Code-Umbau ohne Verhaltensänderung |

Beispiele: `feature/add-login`, `fix/null-check-user-service`, `chore/bump-node-20`

Wann ein neuer Branch erstellt wird:
- Immer, bevor Code-Änderungen für eine neue Aufgabe (Feature, Fix, Chore, ...) beginnen.
- Ein Branch = eine thematisch abgeschlossene Änderung. Nicht mehrere unabhängige Themen in einem Branch mischen.

## Commit Messages: Conventional Commits

Format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

- `type`: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`, `revert`
- `scope`: optional, z.B. Modul- oder Komponentenname (`feat(auth): ...`)
- `description`: Imperativ, klein geschrieben, kein Punkt am Ende, möglichst ≤ 72 Zeichen ("add x" statt "added x" oder "adds x")
- `body` (optional): erklärt das *Warum*, nicht nur das *Was*
- Breaking Changes: entweder `!` nach dem Typ (`feat!: ...`) oder Footer `BREAKING CHANGE: <erklärung>`

Beispiele:
```
feat(auth): add password reset flow
fix(api): handle null response from payment service
chore: update dependencies to latest minor versions
docs(readme): clarify local setup steps
```

Jeder Commit auf einem Feature-Branch sollte für sich sinnvoll sein; kleine "wip"-Commits sind während der Arbeit ok, werden aber vor dem Merge in einen sauberen, aussagekräftigen Verlauf gebracht (siehe Merge-Strategie).

## Pull Requests

- PRs gehen immer gegen `trunk`.
- PR-Titel folgt demselben Conventional-Commits-Format wie ein Commit (wichtig für Squash-Merge, siehe unten).
- PR-Beschreibung: kurzer Kontext (Was & Warum), ggf. Test-Hinweise. Kein Pflichtformat, aber nie leer lassen.
- Nach Approval und grünem CI: mergen.
- Branch nach dem Merge löschen.

## Merge-Strategie

- Standard: **Squash-Merge** in `trunk`. Das hält die `trunk`-Historie linear und sauber — ein Commit pro PR.
- Der Squash-Commit-Titel folgt dem Conventional-Commits-Format (siehe oben) und wird beim Mergen entsprechend gesetzt/angepasst, auch wenn die einzelnen Zwischen-Commits das nicht taten.
- Rebase-Merge ist eine Ausnahme für Fälle, in denen die einzelne Commit-Historie bewusst erhalten bleiben soll (z.B. sehr große, bewusst in Schritte gegliederte PRs). Kein Merge-Commit mit Merge-Bubble als Standard.

## Hotfixes

- Branch `hotfix/<kurzbeschreibung>` direkt von `trunk`.
- Schnellstmöglich durch Review, dann Squash-Merge nach `trunk` wie ein normaler PR.
- Danach ggf. Tag/Release wie gewohnt.

## Releases & Tags

- Da trunk-based: keine festen Release-Branches.
- Bei Bedarf wird `trunk` zu einem Release-Zeitpunkt getaggt (SemVer, z.B. `v1.4.0`).
- Der Tag wird direkt auf dem entsprechenden Merge-Commit auf `trunk` gesetzt.

## Zusammenfassung für Claude

Wenn in einem Projekt des Users mit Git gearbeitet wird:
1. Nie direkt auf `trunk` committen — immer erst einen Branch mit passendem Präfix erstellen.
2. Commit-Messages im Conventional-Commits-Format schreiben.
3. PRs gegen `trunk`, Titel im Conventional-Commits-Format.
4. Squash-Merge als Standard-Mergestrategie vorschlagen/verwenden, sofern der User nichts anderes sagt.
5. Branch nach Merge löschen.