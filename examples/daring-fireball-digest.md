# Daring Fireball Digest

Every Friday at 9am, fetch `https://daringfireball.net/feeds/main` and email
me a concise digest.

Recipient: the single address configured in `EMAIL_SKILL_ALLOWED_RECIPIENTS`.

Focus on Apple platform changes, developer tools, AI, business implications,
and noteworthy commentary. Keep it under 700 words and include source links.

Send the final email by running:

```bash
cd /absolute/path/to/email-skill/skill
python3 email_skill/send_email.py /absolute/path/to/email_payload.json
```

Create `email_payload.json`:

```json
{
  "subject": "Daring Fireball weekly digest",
  "body": "<the digest>",
  "confirmed": true
}
```
