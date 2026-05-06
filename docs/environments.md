# Environment Setup

Choose the guide for the AI tool you use:

- [Claude Code](./claude-code.md) - filesystem skill under
  `~/.claude/skills/email-skill` or project `.claude/skills/email-skill`.
- [Claude Cowork](./claude-cowork.md) - ZIP upload through Claude's Skills UI.
- [Codex](./codex.md) - filesystem skill under `~/.codex/skills/email-skill`
  or a Codex workspace/automation.

The sender itself is identical in every environment. It reads configuration in
this order:

1. Environment variables already available to the process.
2. `EMAIL_SKILL_CONFIG=/path/to/email-skill.env`, if set.
3. `./email-skill.env`, if present.
4. `./.env`, if present.

It never searches the filesystem for credentials.

Use your real email address in `EMAIL_SKILL_ALLOWED_RECIPIENTS`; do not leave
placeholder addresses in runnable config. Example payloads omit `recipient`
when exactly one address is allowlisted.
