import os
from pathlib import Path


CONFIG_CANDIDATES = ("email-skill.env", ".env")

BASE_REQUIRED = (
    "EMAIL_SKILL_FROM",
    "EMAIL_SKILL_ALLOWED_RECIPIENTS",
)

SMTP_REQUIRED = (
    "EMAIL_SKILL_SMTP_HOST",
    "EMAIL_SKILL_SMTP_PORT",
    "EMAIL_SKILL_SMTP_USER",
    "EMAIL_SKILL_SMTP_PASSWORD",
)

RESEND_REQUIRED = (
    "EMAIL_SKILL_RESEND_API_KEY",
)

SES_REQUIRED = (
    "EMAIL_SKILL_AWS_REGION",
)


def _parse_env_file(path):
    values = {}
    if not path or not Path(path).exists():
        return values

    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config():
    """Load config without searching the filesystem.

    Precedence:
    1. Process environment
    2. EMAIL_SKILL_CONFIG=/path/to/email-skill.env
    3. ./email-skill.env
    4. ./.env
    """
    loaded_from = None
    file_values = {}

    explicit = os.environ.get("EMAIL_SKILL_CONFIG")
    if explicit:
        loaded_from = explicit
        file_values = _parse_env_file(explicit)
    else:
        for candidate in CONFIG_CANDIDATES:
            if Path(candidate).exists():
                loaded_from = str(Path(candidate).resolve())
                file_values = _parse_env_file(candidate)
                break

    merged = dict(file_values)
    merged.update({key: value for key, value in os.environ.items() if value})
    return merged, loaded_from


def provider_name(config):
    provider = (config.get("EMAIL_SKILL_PROVIDER") or "").strip().lower()
    if provider:
        return provider
    if config.get("EMAIL_SKILL_RESEND_API_KEY"):
        return "resend"
    if config.get("EMAIL_SKILL_AWS_REGION"):
        return "ses"
    return "smtp"


def missing_keys(config):
    missing = [key for key in BASE_REQUIRED if not config.get(key)]
    provider = provider_name(config)
    if provider == "smtp":
        missing.extend(key for key in SMTP_REQUIRED if not config.get(key))
    elif provider == "resend":
        missing.extend(key for key in RESEND_REQUIRED if not config.get(key))
    elif provider == "ses":
        missing.extend(key for key in SES_REQUIRED if not config.get(key))
    elif provider == "dry-run":
        pass
    else:
        missing.append("EMAIL_SKILL_PROVIDER=smtp|resend|ses|dry-run")
    return missing


def allowed_recipients(config):
    return [
        value.strip().lower()
        for value in (config.get("EMAIL_SKILL_ALLOWED_RECIPIENTS") or "").split(",")
        if value.strip()
    ]


def configuration_error(missing):
    return (
        "Email skill is not configured.\n"
        "Missing:\n"
        + "\n".join(f"- {key}" for key in missing)
        + "\n\nSet these in your environment, create ./email-skill.env, "
          "or set EMAIL_SKILL_CONFIG=/path/to/email-skill.env."
    )
