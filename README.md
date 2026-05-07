# Email Skill

**Give your AI a safe way to send emails to you.**

Email Skill is a small local skill for Claude, Cursor, Codex, cron jobs, and
other AI automation tools. You connect your own email provider, allowlist your
own address, and the AI can send useful emails without a server, MCP process,
or inbox access.

Use it for things like:

- "Every Friday morning, email me a Daring Fireball digest."
- "On the first of each month, email me how much I owe each affiliate."
- "Every weekday at 5pm, email me a summary of closed support tickets."
- "Email me a preview of this report before sending anything."

The skill keeps the sharp edges in code:

- only emails addresses in `EMAIL_SKILL_ALLOWED_RECIPIENTS`
- sends through Resend, AWS SES, SMTP/Gmail, or dry-run
- supports preview-before-send for one-off emails
- supports direct confirmed sends for automations you already approved

No MCP server. No HTTP API. No scheduler daemon. Your AI tool handles the
schedule and the thinking; this skill handles safe email delivery.

## Quickstart

```bash
git clone https://github.com/yourname/email-skill
cd email-skill
cp skill/email-skill.env.example skill/email-skill.env
chmod 600 skill/email-skill.env
```

Open `email-skill.env` in any text editor:

```bash
nano skill/email-skill.env
```

If you use VS Code:

```bash
code skill/email-skill.env
```

Or open the `email-skill/skill` folder in Finder/File Explorer and edit the
`email-skill.env` file there.

Put your sender settings in `email-skill.env`:

```env
EMAIL_SKILL_PROVIDER=dry-run
EMAIL_SKILL_FROM=digests@example.com
EMAIL_SKILL_ALLOWED_RECIPIENTS=test@example.com
```

Pick your sender setup:

- [All provider quickstarts](docs/provider-quickstarts.md)
- [Gmail SMTP risks and setup](docs/gmail.md)
- [Claude Code guide](docs/claude-code.md)
- [Claude Cowork guide](docs/claude-cowork.md)
- [Codex guide](docs/codex.md)

Check configuration:

```bash
cd skill
python3 email_skill/check_config.py
```

Send a test payload:

```bash
python3 email_skill/send_email.py ../examples/direct-send.json
```

## Example Automations

**Daring Fireball Digest**

Every Friday at 9am, fetch `https://daringfireball.net/feeds/main`, summarize
the most important Apple, developer-tools, and business-model posts, and email
the digest to your allowlisted email address.

**Affiliate Payment Reminder**

On the first day of each month, read last month's affiliate revenue source,
calculate the amount owed to each affiliate, and email your allowlisted address a
payment checklist with affiliate name, amount, and missing-data warnings.

**Daily Support Ticket Summary**

Every weekday at 5pm, summarize today's closed support tickets, grouped by
product area and follow-up needed, and email the summary to your allowlisted address.

Full copy-pasteable prompt examples are in [examples](examples).

## Sender

| Script | Purpose |
| --- | --- |
| `skill/email_skill/check_config.py` | Validate deterministic config and list missing variables. |
| `skill/email_skill/send_email.py` | Send a confirmed payload through Resend, AWS SES, SMTP/Gmail, or dry-run. |

`send_email.py` accepts a JSON file path or reads JSON from stdin.
`check_config.py` prints either the loaded config summary or a precise missing
variable list.

## Providers

Set `EMAIL_SKILL_PROVIDER` to one of:

- `dry-run` - logs the attempted send to stderr; no credentials required.
- `resend` - recommended for most users; uses `EMAIL_SKILL_RESEND_API_KEY`.
- `ses` - recommended for AWS users; uses the AWS CLI and `EMAIL_SKILL_AWS_REGION`.
- `smtp` - uses `EMAIL_SKILL_SMTP_HOST`, `EMAIL_SKILL_SMTP_PORT`,
  `EMAIL_SKILL_SMTP_USER`, and `EMAIL_SKILL_SMTP_PASSWORD`.

For Gmail, SMTP requires a Google app password. Treat that app password as a
real credential: if it leaks, someone may be able to send email as you and may
be able to read/download mail through IMAP or POP if those protocols are enabled.
Prefer Resend or AWS SES for cleaner sender isolation and easier key rotation.

See [docs/provider-quickstarts.md](docs/provider-quickstarts.md).

## How To Use With AI Automations

1. Create a recurring automation in your AI tool.
2. Tell it what to gather or summarize.
3. Tell it to send the result to your allowlisted email by running:

```bash
python3 email_skill/send_email.py email_payload.json
```

Pass JSON on stdin:

```json
{
  "subject": "Daily digest",
  "body": "<the email body>",
  "confirmed": true
}
```

Email bodies are sent as plain text by default. To intentionally send HTML,
include `"html": true` or `"body_format": "html"` in the payload.

If `recipient` is omitted and exactly one address is configured in
`EMAIL_SKILL_ALLOWED_RECIPIENTS`, the sender uses that address. If multiple
addresses are allowlisted, include `recipient` explicitly.

For one-off messages, ask the AI to show you the subject/body first and send
only after you approve.

For Claude Code, Claude Cowork, and Codex, see
[docs/environments.md](docs/environments.md). Claude/Cowork web uploads need a
ZIP whose root folder is `email-skill/`; Claude Code and Codex can install the
same folder directly on disk.

## Local State

By default, the sender reads `email-skill.env` or `.env` only from the installed
skill directory next to `SKILL.md`. Set `EMAIL_SKILL_CONFIG=/absolute/path/to/email-skill.env`
to use a config file somewhere else.

## Security Model

Email Skill is designed to reduce accidental or prompt-driven email mistakes,
not to hide credentials from a fully trusted local AI agent.

What it protects against:

- sending to a recipient outside `EMAIL_SKILL_ALLOWED_RECIPIENTS`
- sending without an explicit `confirmed: true` payload
- accidentally loading credentials from an unrelated working directory
- accidentally committing common local env files, when `.gitignore` is kept

What it does not protect against:

- a compromised machine
- malware or another local process reading your files
- an AI agent with permission to read the env file or run arbitrary commands
- a stolen provider credential being used outside this script

Treat every provider secret in `email-skill.env` as sensitive. Keep the file
private with `chmod 600`, do not put it in shared repos, do not upload it in
public ZIPs, and rotate/revoke credentials if it may have leaked.

For real automations, prefer Resend or AWS SES. They let you use a dedicated
sender identity and a revocable API key or AWS credential. Gmail SMTP works, but
it requires a Google app password; if that password leaks, someone may be able
to send mail as your Gmail account and may be able to read/download mail through
IMAP or POP if those protocols are enabled. The allowlist protects this script,
not the credential itself.

## Repo Layout

```text
email-skill/
├── skill/
│   ├── SKILL.md
│   ├── email_skill/
│   └── email-skill.env.example
├── examples/
├── docs/
└── LICENSE
```

## License

MIT
