---
name: email-skill
description: Send useful emails to the user through their local email provider. Use when the user asks to email them a summary, digest, reminder, report, or automation result.
---

# Email Skill

This skill lets AI send emails to the user through a deterministic local
configuration. Never search the filesystem for credentials.

## When To Activate

Use this skill when the user asks to:

- Email a summary, report, or digest.
- Email a reminder or recurring checklist.
- Send the result of a recurring automation.
- Send the result of an event-triggered automation.

Do not use this skill for inbox search, calendar invites, attachments,
marketing campaigns, or drafting-only tasks where no send is requested.

## Safety Rules

1. For one-off emails, show the user the subject/body first and send only after
   approval.
2. Automation sends may use `confirmed: true` only when the automation
   definition already fixes the recipient and purpose.
3. Never invent recipients. If the user did not name a recipient, ask.
4. Never send to a recipient outside `EMAIL_SKILL_ALLOWED_RECIPIENTS`.
   If the payload omits `recipient` and exactly one address is allowlisted, use
   that address. If multiple addresses are allowlisted, require `recipient`.
5. Keep email bodies concise and do not include full copyrighted source text.

## Configuration

To check configuration, run:

```bash
python3 email_skill/check_config.py
```

Run commands from the directory containing this `SKILL.md`. If the payload is
in another working directory, pass its absolute path to `send_email.py`.

The skill reads config from:

1. Environment variables already available to the process.
2. `EMAIL_SKILL_CONFIG=/path/to/email-skill.env`, if set.
3. `./email-skill.env`, if present.
4. `./.env`, if present.

If configuration is missing, ask the user to set the missing variables. Do not
search `/Users`, `/var`, `/`, temporary plugin folders, old local session
outputs, or unrelated project folders.

Required SMTP/Gmail variables:

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

For Resend:

```env
EMAIL_SKILL_PROVIDER=resend
EMAIL_SKILL_FROM=digests@yourdomain.com
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
EMAIL_SKILL_RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
```

For AWS SES:

```env
EMAIL_SKILL_PROVIDER=ses
EMAIL_SKILL_FROM=digests@yourdomain.com
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
EMAIL_SKILL_AWS_REGION=us-east-1
```

For local testing:

```env
EMAIL_SKILL_PROVIDER=dry-run
EMAIL_SKILL_FROM=digests@example.com
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
```

## Sending

Write the final payload to `email_payload.json` in the current working
directory:

```json
{
  "subject": "Digest",
  "body": "Email body",
  "confirmed": true
}
```

Then send it:

```bash
python3 email_skill/send_email.py email_payload.json
```

The sender supports:

- `EMAIL_SKILL_PROVIDER=smtp` for Gmail and generic SMTP.
- `EMAIL_SKILL_PROVIDER=resend` for Resend.
- `EMAIL_SKILL_PROVIDER=ses` for AWS SES through the AWS CLI.
- `EMAIL_SKILL_PROVIDER=dry-run` for local tests.
