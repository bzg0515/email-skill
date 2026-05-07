# Provider Quickstarts

Pick one provider and put its settings in `email-skill.env`.

Replace every example email address with your own before running the skill. The
example send payloads omit `recipient`; that only works when exactly one real
address is configured in `EMAIL_SKILL_ALLOWED_RECIPIENTS`.

The skill reads config from:

1. Environment variables already available to the process.
2. `EMAIL_SKILL_CONFIG=/path/to/email-skill.env`, if set.
3. `email-skill.env` next to `SKILL.md`, if present.
4. `.env` next to `SKILL.md`, if present.

It never searches the filesystem for credentials.

After creating a provider config with real credentials, run
`chmod 600 /path/to/email-skill.env`. On POSIX systems, the sender refuses
credential files that are readable by group or other users.

## Dry Run

Use this first if you just want to check that the skill works locally.

```env
EMAIL_SKILL_PROVIDER=dry-run
EMAIL_SKILL_FROM=digests@example.com
EMAIL_SKILL_FROM_NAME=Email Skill
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
```

## Recommended Providers

Prefer Resend or AWS SES for real automations. They let you create a dedicated
sender identity and rotate/revoke an API key or AWS credential without touching
your personal Gmail account.

## Resend

```env
EMAIL_SKILL_PROVIDER=resend
EMAIL_SKILL_FROM=digests@yourdomain.com
EMAIL_SKILL_FROM_NAME=Email Skill
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
EMAIL_SKILL_RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
```

## AWS SES

Install and configure the AWS CLI first:

```bash
aws configure
```

Then use:

```env
EMAIL_SKILL_PROVIDER=ses
EMAIL_SKILL_FROM=digests@yourdomain.com
EMAIL_SKILL_FROM_NAME=Email Skill
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
EMAIL_SKILL_AWS_REGION=us-east-1
# EMAIL_SKILL_AWS_CONFIGURATION_SET=my-config-set
```

SES sandbox accounts can only send to verified recipients.

## Gmail SMTP

Use Gmail SMTP only if you accept the app-password risk. A Google app password
is a real credential: if the env file leaks, someone can send email as you and
may be able to read/download mail through IMAP or POP if those protocols are
enabled. Keep `EMAIL_SKILL_ALLOWED_RECIPIENTS` limited to your address, but
remember the allowlist protects this script, not the stolen credential.

1. Turn on 2-Step Verification in your Google Account.
2. Create a Google App Password at `https://myaccount.google.com/apppasswords`.
3. Put the app password in `EMAIL_SKILL_SMTP_PASSWORD`.

```env
EMAIL_SKILL_PROVIDER=smtp
EMAIL_SKILL_FROM=you@gmail.com
EMAIL_SKILL_FROM_NAME=Your Name
EMAIL_SKILL_ALLOWED_RECIPIENTS=you@gmail.com
EMAIL_SKILL_SMTP_HOST=smtp.gmail.com
EMAIL_SKILL_SMTP_PORT=587
EMAIL_SKILL_SMTP_USER=you@gmail.com
EMAIL_SKILL_SMTP_PASSWORD=your-16-character-app-password
```

More detail: [gmail.md](./gmail.md).

## Generic SMTP

```env
EMAIL_SKILL_PROVIDER=smtp
EMAIL_SKILL_FROM=digests@yourdomain.com
EMAIL_SKILL_FROM_NAME=Email Skill
EMAIL_SKILL_ALLOWED_RECIPIENTS=your-email@example.com
EMAIL_SKILL_SMTP_HOST=smtp.example.com
EMAIL_SKILL_SMTP_PORT=587
EMAIL_SKILL_SMTP_USER=username
EMAIL_SKILL_SMTP_PASSWORD=password
# EMAIL_SKILL_SMTP_SECURE=false
```

For port `465`, set:

```env
EMAIL_SKILL_SMTP_SECURE=true
```

## Test Any Provider

From the installed skill directory, check config:

```bash
python3 email_skill/check_config.py
```

Then send:

```bash
python3 email_skill/send_email.py ../examples/direct-send.json
```
