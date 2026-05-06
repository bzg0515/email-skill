# Claude Cowork Guide

Claude/Cowork web skills are uploaded as ZIP files. The ZIP must contain the
whole `email-skill/` folder, including `SKILL.md`, `email_skill/`, and any
local `email-skill.env` you want Cowork's sandbox to read.

## Decide How To Handle Secrets

Cowork cannot read arbitrary files from your Mac after the skill is uploaded.
For real email delivery, it needs config from one of these places:

- Environment variables made available by the Cowork runtime, if your setup
  supports that.
- `EMAIL_SKILL_CONFIG`, if your setup supports setting it.
- `email-skill.env` inside the private ZIP upload.

The most foolproof path is including `email-skill.env` in your own private ZIP.
Use a sender credential scoped only to this job, keep
`EMAIL_SKILL_ALLOWED_RECIPIENTS` to your own address, and do not share that ZIP.

For organization-wide sharing, upload a code-only ZIP without
`email-skill.env`; each user should make their own private configured copy.

## Create Config

From the repo root:

```bash
cp skill/email-skill.env.example skill/email-skill.env
nano skill/email-skill.env
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

## Build The ZIP

The folder inside the ZIP must be named `email-skill/`, not `skill/`, and the
files must not be loose at the ZIP root.

```bash
rm -rf build
mkdir -p build/email-skill
cp -R skill/. build/email-skill/
cd build
zip -r email-skill.zip email-skill
```

Correct ZIP shape:

```text
email-skill.zip
└── email-skill/
    ├── SKILL.md
    ├── email-skill.env
    ├── email-skill.env.example
    └── email_skill/
        ├── check_config.py
        ├── config.py
        └── send_email.py
```

## Upload And Enable

1. Open Claude.
2. Go to `Customize > Skills`.
3. Click `+`, then `+ Create skill`.
4. Choose `Upload a skill`.
5. Upload `build/email-skill.zip`.
6. Toggle the skill on.

In Cowork on Team or Enterprise plans, skills shared with you may appear in the
directory. Install the skill from the directory, then enable it.

## Test In Cowork

Ask Cowork:

```text
Use the email-skill to check its configuration.
```

It should run:

```bash
python3 email_skill/check_config.py
```

Then ask:

```text
Use the email-skill to send me a short test email.
```

If Cowork reports missing scripts, the ZIP did not include `email_skill/`. If
it reports missing environment variables, the ZIP did not include
`email-skill.env` and no runtime env was provided.

## Sources

- Claude custom skill ZIP packaging: https://support.claude.com/en/articles/12512198-how-to-create-custom-skills
- Using skills in Claude and Cowork: https://support.claude.com/en/articles/12512180-use-skills-in-claude
