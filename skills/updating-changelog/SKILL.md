---
name: updating-changelog
description: Use while working on a feature, fix, or hotfix branch, before opening/merging its PR, or when explicitly asked to update or review the changelog
---

`CHANGELOG.md` in the repo root follows [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), in German. All entries go under `## [Unreleased]`. This repo has no automated deploy/release pipeline that cuts a dated section — that only happens manually, if/when `trunk` gets tagged for a release (see git-branching-workflow).

Add the changelog entry **inside the feature/fix/hotfix branch itself**, as part of the same PR — not as a separate step after merging. That way it lands in `trunk` together with the code change in the same squash-merge; a follow-up edit straight on `trunk` would violate the "never commit directly to `trunk`" rule from the branching workflow and risks being forgotten.

Add one bullet per user-visible change to the matching category under `[Unreleased]`:

- **Added** — neue Funktionalität
- **Changed** — Verhalten einer bestehenden Funktion ändert sich
- **Deprecated** — bald entfernte Funktionalität
- **Removed** — entfernte Funktionalität
- **Fixed** — Bugfix
- **Security** — sicherheitsrelevante Änderung

Write from the operator's perspective (what changes about the box/dashboard's behavior), not a copy of the commit message. One short bullet per change, German, e.g.:

```markdown
### Fixed

- Relais-Polarität korrigiert: das Board ist tatsächlich active-HIGH, nicht
  active-LOW wie ursprünglich angenommen.
```

Leave a category's heading in place even when empty — `[Unreleased]` always keeps all six as a template.

If rebasing/merging with `trunk` produces a conflict in `CHANGELOG.md`, it's almost always two branches appending different bullets to the same category — keep both lines rather than dropping one.
