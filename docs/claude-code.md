# Claude Code Guide

Claude Code uses filesystem skills. Install the full skill folder on disk; do
not upload a ZIP for Claude Code.

## Install

Personal install, available in all Claude Code projects:

```bash
mkdir -p ~/.claude/skills/email-skill
cp -R skill/. ~/.claude/skills/email-skill/
```

Project install, available only in the current repo:

```bash
mkdir -p .claude/skills/email-skill
cp -R /absolute/path/to/email-skill/skill/. .claude/skills/email-skill/
```

Claude Code discovers skills from personal `~/.claude/skills/`, project
`.claude/skills/`, and plugin skill folders. If the top-level skills directory
did not exist when Claude Code started, restart Claude Code once.

## Configure

Create a local config file next to `SKILL.md`:

```bash
cp ~/.claude/skills/email-skill/email-skill.env.example ~/.claude/skills/email-skill/email-skill.env
chmod 600 ~/.claude/skills/email-skill/email-skill.env
nano ~/.claude/skills/email-skill/email-skill.env
```

Use your real recipient:

```env
EMAIL_SKILL_PROVIDER=resend
EMAIL_SKILL_FROM=digests@yourdomain.com
EMAIL_SKILL_FROM_NAME=Email Skill
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
EMAIL_SKILL_RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
```

For maximum reliability, expose only the config path to Claude Code in
`.claude/settings.local.json`:

```json
{
  "env": {
    "EMAIL_SKILL_CONFIG": "/Users/you/.claude/skills/email-skill/email-skill.env"
  }
}
```

Or set it before launching Claude Code:

```bash
export EMAIL_SKILL_CONFIG=/Users/you/.claude/skills/email-skill/email-skill.env
claude
```

## Test

Ask Claude Code:

```text
Use the email-skill to check its configuration.
```

It can run the checker from any working directory; default config is loaded
from the installed skill directory next to `SKILL.md`:

```bash
python3 ~/.claude/skills/email-skill/email_skill/check_config.py
```

Then ask for a real test:

```text
Use the email-skill to send me a short test email.
```

The payload may omit `recipient` when exactly one address is configured in
`EMAIL_SKILL_ALLOWED_RECIPIENTS`.

## Sources

- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Code environment variables: https://code.claude.com/docs/en/env-vars
