# Codex Guide

Codex uses skills as playbooks for repeatable work. For local email delivery,
install the full skill folder on disk and keep provider secrets in an ignored
`email-skill.env` file.

## Install Locally

```bash
mkdir -p ~/.codex/skills/email-skill
cp -R skill/. ~/.codex/skills/email-skill/
```

Restart Codex after installing a new skill.

## Configure

```bash
cp ~/.codex/skills/email-skill/email-skill.env.example ~/.codex/skills/email-skill/email-skill.env
chmod 600 ~/.codex/skills/email-skill/email-skill.env
nano ~/.codex/skills/email-skill/email-skill.env
```

Example dry-run config:

```env
EMAIL_SKILL_PROVIDER=dry-run
EMAIL_SKILL_FROM=digests@example.com
EMAIL_SKILL_FROM_NAME=Email Skill
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
```

Example Gmail config:

```env
EMAIL_SKILL_PROVIDER=smtp
EMAIL_SKILL_FROM=you@gmail.com
EMAIL_SKILL_FROM_NAME=Your Name
EMAIL_SKILL_ALLOWED_RECIPIENTS=you@gmail.com
EMAIL_SKILL_SMTP_HOST=smtp.gmail.com
EMAIL_SKILL_SMTP_PORT=587
EMAIL_SKILL_SMTP_USER=you@gmail.com
EMAIL_SKILL_SMTP_PASSWORD=your-google-app-password
```

For maximum reliability, launch Codex with an explicit config path:

```bash
export EMAIL_SKILL_CONFIG=/Users/you/.codex/skills/email-skill/email-skill.env
codex
```

## Use In A Thread

Invoke the skill with `$email-skill` or ask naturally:

```text
$email-skill Send me a short test email.
```

Codex can run the sender from any working directory; default config is loaded
from the installed skill directory next to `SKILL.md`:

```bash
cd ~/.codex/skills/email-skill
python3 email_skill/check_config.py
python3 email_skill/send_email.py /absolute/path/to/email_payload.json
```

## Use In A Codex Automation

Codex automations can run recurring tasks on a schedule. For local delivery,
the machine running Codex needs to be awake and Codex needs to be running.

Use a prompt like:

```text
Every Friday at 9am, fetch the Daring Fireball feed, summarize the most useful
items, then use $email-skill to email the digest to my allowlisted address.
Use EMAIL_SKILL_CONFIG=/Users/you/.codex/skills/email-skill/email-skill.env.
```

If your Codex environment cannot access your local skill folder or local env
file, use dry-run/report mode there or provide equivalent environment variables
through that environment's supported secret mechanism.

## Sources

- Codex plugins and skills: https://openai.com/academy/codex-plugins-and-skills/
- Codex automations: https://openai.com/academy/codex-automations/
- OpenAI skills catalog notes: https://github.com/openai/skills
