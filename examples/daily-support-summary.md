# Daily Support Ticket Summary

Every weekday at 5pm, summarize today's closed support tickets and email me the
high-signal version.

Recipient: the single address configured in `EMAIL_SKILL_ALLOWED_RECIPIENTS`.

Group by product area. Include issue, resolution, customer sentiment, follow-up
needed, and any bug patterns that appeared more than once.

Send the final email by running:

```bash
cd /absolute/path/to/email-skill/skill
python3 email_skill/send_email.py /absolute/path/to/email_payload.json
```

Create `email_payload.json`:

```json
{
  "subject": "Daily support ticket summary",
  "body": "<the summary>",
  "confirmed": true
}
```
