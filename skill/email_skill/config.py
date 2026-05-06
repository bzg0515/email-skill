import os
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CONFIG_CANDIDATES = ("email-skill.env", ".env")
SENSITIVE_KEY_PARTS = ("PASSWORD", "API_KEY", "SECRET", "TOKEN")
PLACEHOLDER_MARKERS = (
    "your-",
    "example",
    "xxxxxxxx",
    "placeholder",
)


class ConfigFilePermissionError(Exception):
    pass

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
    config_path = Path(path) if path else None
    if not config_path or not config_path.exists():
        return values

    for raw in config_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    _validate_config_file_permissions(config_path, values)
    return values


def _looks_like_placeholder(value):
    normalized = value.strip().lower()
    if not normalized:
        return True
    return any(marker in normalized for marker in PLACEHOLDER_MARKERS)


def _contains_sensitive_values(values):
    for key, value in values.items():
        key_upper = key.upper()
        if any(part in key_upper for part in SENSITIVE_KEY_PARTS):
            if not _looks_like_placeholder(value):
                return True
    return False


def _validate_config_file_permissions(path, values):
    if os.name != "posix" or not _contains_sensitive_values(values):
        return

    mode = path.stat().st_mode
    if mode & 0o077:
        raise ConfigFilePermissionError(
            f"Refusing to load {path}: it contains email credentials and is readable "
            "by group or other users. Run `chmod 600 "
            f"{path}` and try again."
        )


def load_config():
    """Load config without searching the filesystem.

    Precedence:
    1. Process environment
    2. EMAIL_SKILL_CONFIG=/path/to/email-skill.env
    3. email-skill.env next to SKILL.md
    4. .env next to SKILL.md
    """
    loaded_from = None
    file_values = {}

    explicit = os.environ.get("EMAIL_SKILL_CONFIG")
    if explicit:
        config_path = Path(explicit)
        loaded_from = str(config_path.resolve()) if config_path.exists() else explicit
        file_values = _parse_env_file(config_path)
    else:
        for candidate in CONFIG_CANDIDATES:
            config_path = SKILL_DIR / candidate
            if config_path.exists():
                loaded_from = str(config_path.resolve())
                file_values = _parse_env_file(config_path)
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
        + "\n\nSet these in your environment, create email-skill.env next to "
          "SKILL.md, or set EMAIL_SKILL_CONFIG=/path/to/email-skill.env."
    )
