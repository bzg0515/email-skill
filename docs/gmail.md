# Gmail SMTP Risks And Setup

Prefer Resend or AWS SES for real automations. Use Gmail SMTP only when you are
comfortable storing a Google app password on the machine running the skill.

Gmail works through SMTP with a Google App Password. Do not use your normal
Google password.

## Risk Model

A Google app password is a real credential. If someone reads it from
`email-skill.env`, a backup, a ZIP upload, shell history, or a shared machine,
they can send email as you until you revoke that app password.

Email Skill still enforces `EMAIL_SKILL_ALLOWED_RECIPIENTS` before it sends,
but that allowlist only protects sends that go through this script. It cannot
stop an attacker who stole the app password from using it elsewhere.

If you use Gmail anyway:

- Keep `EMAIL_SKILL_ALLOWED_RECIPIENTS` limited to your own address.
- Keep `email-skill.env` ignored by git and set to `chmod 600`.
- Create an app password only for this skill.
- Revoke the app password immediately if the file may have leaked.

## 1. Turn On 2-Step Verification

In your Google Account, open **Security** and turn on **2-Step Verification**.

Google only lets you create App Passwords when 2-Step Verification is enabled.

## 2. Create An App Password

Open Google's App Passwords page:

```text
https://myaccount.google.com/apppasswords
```

Create a new app password for Email Skill. Google will show a 16-character
password. Copy it once; you will not be able to see it again.

## 3. Create `email-skill.env`

Create `email-skill.env` in the installed skill directory:

```bash
cp email-skill.env.example email-skill.env
chmod 600 email-skill.env
nano email-skill.env
```

Use:

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

Remove spaces from the app password if Google displays it grouped in chunks.

## 4. Check Configuration

```bash
python3 email_skill/check_config.py
```

## 5. Send A Test Email

Create `email_payload.json`:

```json
{
  "subject": "Email Skill test",
  "body": "Preview only.",
  "confirmed": true
}
```

Then send:

```bash
python3 email_skill/send_email.py email_payload.json
```

You should receive the test email in your Gmail inbox.
