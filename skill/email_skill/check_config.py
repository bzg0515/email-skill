#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from email_skill.config import (
    ConfigFilePermissionError,
    configuration_error,
    load_config,
    missing_keys,
    provider_name,
)


def main():
    try:
        config, loaded_from = load_config()
    except ConfigFilePermissionError as err:
        print(err, file=sys.stderr)
        return 1
    missing = missing_keys(config)
    if missing:
        print(configuration_error(missing), file=sys.stderr)
        return 1

    print(json.dumps({
        "ok": True,
        "provider": provider_name(config),
        "config_file": loaded_from,
        "from": config.get("EMAIL_SKILL_FROM"),
        "allowed_recipients": config.get("EMAIL_SKILL_ALLOWED_RECIPIENTS"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
