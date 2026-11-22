# send-last

opencode command `/send-last <email-address>`: mails the last assistant answer of the current session to the given address.

- Subject: `[opencode] <session title>`
- Body: `multipart/alternative` -- the answer's raw Markdown as plain text plus a rendered HTML part (`markdown` with fenced code, tables, lists).
- Only the **text** of the answer is sent. Reasoning and tool output are left out. If the answer spans several assistant messages (text between tool calls), all text parts since your previous prompt are joined.

## Files

| File | Purpose |
| --- | --- |
| `send-last.md` | The opencode command. Tells the agent to run `~/.local/bin/send-last "$1"` and report the result only |
| `send-last` | Python script (run via `uv run --script`, dependency `markdown` resolved inline). Reads the answer from the session, builds the mail, sends it over SMTP |
| `smtp.conf.example` | Template for the SMTP settings |
| `install-user.sh` / `uninstall-user.sh` | Per-user (un)install via symlinks |

## How it works

1. `/send-last you@example.com` expands the command template; the agent runs the script with the shell tool.
2. The script validates the address and reads `OPENCODE_SESSION_ID` (set by opencode for shell commands).
3. It fetches the session messages with `opencode api get /api/session/<id>/message?order=desc`, skips the `/send-last` prompt itself, and collects the assistant text back to the previous user message.
4. It sends the mail via `smtplib` (STARTTLS on 587, implicit SSL on 465).

The address is passed as a quoted argument to the script and validated there, not interpolated into a `!` shell block, so it cannot inject shell commands.

## Install (user-wide)

```bash
./install-user.sh
```

Creates symlinks (existing non-symlink files are never overwritten):

| Link | Target |
| --- | --- |
| `~/.local/bin/send-last` | `commands/send-last/send-last` |
| `${XDG_CONFIG_HOME:-~/.config}/opencode/commands/send-last.md` | `commands/send-last/send-last.md` |

and, if missing, creates `${XDG_CONFIG_HOME:-~/.config}/send-last/smtp.conf` (mode `600`) from the example. Requires `uv`.

opencode reloads commands automatically; no restart needed.

## SMTP configuration

Edit `${XDG_CONFIG_HOME:-~/.config}/send-last/smtp.conf`:

```ini
host = smtp.gmail.com
port = 587
user = your.address@gmail.com
password = APP-PASSWORD
from = Your Name <your.address@gmail.com>
```

For Gmail enable 2-step verification and create an [app password](https://myaccount.google.com/apppasswords); the normal account password is rejected. The credentials live only in this file -- never in the repo, the opencode config, or the command.

## Uninstall

```bash
./uninstall-user.sh
```

Removes the two symlinks. `smtp.conf` is kept because it holds credentials.

## Verify

```bash
ls -l ~/.local/bin/send-last ~/.config/opencode/commands/send-last.md
~/.local/bin/send-last not-an-address     # prints the usage error
```

Then run `/send-last you@example.com` in opencode.

## Limitations

- opencode only: the script needs `OPENCODE_SESSION_ID` and `opencode api`.
- The command is executed by the agent (shell tool), so opencode may ask for permission on the first run, and the command consumes one short model turn.
- Attachments, images and tool output are not included.
