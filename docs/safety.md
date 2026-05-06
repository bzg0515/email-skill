# Safety Model

Email Skill keeps the safety boundary in code, not in the model prompt.

## Deterministic Config

The skill never searches the filesystem for credentials. It reads only:

1. Process environment.
2. `EMAIL_SKILL_CONFIG=/path/to/email-skill.env`.
3. `./email-skill.env`.
4. `./.env`.

## Recipient Allowlist

`EMAIL_SKILL_ALLOWED_RECIPIENTS` is mandatory. Every send validates the
recipient before calling SMTP, Resend, or AWS SES.

There is no bypass flag. If the list is empty, sending fails.

## Confirmed Sends

Automation sends must include:

```json
{
  "subject": "Daily digest",
  "body": "...",
  "confirmed": true
}
```

If `recipient` is omitted and exactly one address is configured in
`EMAIL_SKILL_ALLOWED_RECIPIENTS`, the sender uses that address. If multiple
addresses are allowlisted, the payload must include `recipient`.

Use this only when the automation definition itself is the user's approval:
recipient, purpose, and cadence should already be fixed.

## What This Repo Does Not Do

- No inbox reading.
- No attachments.
- No calendar invites.
- No marketing campaigns.
- No long-running scheduler.
- No webhook receiver.
