#!/usr/bin/env python3
import json
import smtplib
import ssl
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from email_skill.config import (
    allowed_recipients,
    ConfigFilePermissionError,
    configuration_error,
    load_config,
    missing_keys,
    provider_name,
)


def read_payload(path):
    if path and path != "-":
        return json.loads(Path(path).read_text())
    return json.loads(sys.stdin.read())


def from_header(config):
    sender = config["EMAIL_SKILL_FROM"]
    name = config.get("EMAIL_SKILL_FROM_NAME")
    return f"{name} <{sender}>" if name else sender


def validate_payload(payload, config):
    recipient = (payload.get("recipient") or "").strip()
    subject = payload.get("subject") or ""
    body = payload.get("body") or ""
    confirmed = payload.get("confirmed") is True
    body_format = (payload.get("body_format") or "").strip().lower()
    html = payload.get("html") is True or body_format == "html"
    allowed = allowed_recipients(config)

    if body_format and body_format not in ("text", "html"):
        raise SystemExit("Payload body_format must be text or html.")
    if not recipient:
        if len(allowed) == 1:
            recipient = allowed[0]
        else:
            raise SystemExit(
                "Payload must include recipient when EMAIL_SKILL_ALLOWED_RECIPIENTS has multiple addresses."
            )
    if not subject or not body:
        raise SystemExit("Payload must include subject and body.")
    if not confirmed:
        raise SystemExit("Payload must include confirmed=true for automation sends.")
    if recipient.lower() not in allowed:
        raise SystemExit(f"Recipient {recipient} is not in EMAIL_SKILL_ALLOWED_RECIPIENTS.")
    return recipient, subject, body, html


def send_smtp(config, recipient, subject, body, html=False):
    msg = EmailMessage()
    msg["From"] = from_header(config)
    msg["To"] = recipient
    msg["Subject"] = subject

    if html:
        msg.set_content("This email contains HTML content.")
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    host = config["EMAIL_SKILL_SMTP_HOST"]
    port = int(config["EMAIL_SKILL_SMTP_PORT"])
    secure = (config.get("EMAIL_SKILL_SMTP_SECURE") or "").lower() == "true" or port == 465

    if secure:
        with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context()) as smtp:
            smtp.login(config["EMAIL_SKILL_SMTP_USER"], config["EMAIL_SKILL_SMTP_PASSWORD"])
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(config["EMAIL_SKILL_SMTP_USER"], config["EMAIL_SKILL_SMTP_PASSWORD"])
            smtp.send_message(msg)


def send_resend(config, recipient, subject, body, html=False):
    data = {
        "from": from_header(config),
        "to": [recipient],
        "subject": subject,
        "html" if html else "text": body,
    }
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config['EMAIL_SKILL_RESEND_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        raise SystemExit(err.read().decode("utf-8"))


def send_ses(config, recipient, subject, body, html=False):
    body_key = "Html" if html else "Text"
    content = {
        "Simple": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                body_key: {
                    "Data": body,
                    "Charset": "UTF-8",
                }
            },
        }
    }
    if html:
        content["Simple"]["Body"]["Text"] = {
            "Data": "This email contains HTML content.",
            "Charset": "UTF-8",
        }

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        json.dump(content, tmp)
        tmp_path = tmp.name

    cmd = [
        "aws",
        "sesv2",
        "send-email",
        "--region",
        config["EMAIL_SKILL_AWS_REGION"],
        "--from-email-address",
        config["EMAIL_SKILL_FROM"],
        "--destination",
        json.dumps({"ToAddresses": [recipient]}),
        "--content",
        f"file://{tmp_path}",
    ]
    if config.get("EMAIL_SKILL_AWS_CONFIGURATION_SET"):
        cmd.extend(["--configuration-set-name", config["EMAIL_SKILL_AWS_CONFIGURATION_SET"]])

    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    except FileNotFoundError:
        raise SystemExit("AWS CLI is required for EMAIL_SKILL_PROVIDER=ses. Install and configure aws.")
    except subprocess.CalledProcessError as err:
        raise SystemExit(err.stderr or err.stdout or str(err))
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return json.loads(result.stdout or "{}")


def main():
    try:
        config, _ = load_config()
    except ConfigFilePermissionError as err:
        print(err, file=sys.stderr)
        return 1
    missing = missing_keys(config)
    if missing:
        print(configuration_error(missing), file=sys.stderr)
        return 1

    payload = read_payload(sys.argv[1] if len(sys.argv) > 1 else "-")
    recipient, subject, body, html = validate_payload(payload, config)
    provider = provider_name(config)

    if provider == "dry-run":
        print("[email-skill] DRY_RUN send")
        print(f"from: {from_header(config)}")
        print(f"to: {recipient}")
        print(f"subject: {subject}")
        print(body[:1000])
        return 0
    if provider == "smtp":
        send_smtp(config, recipient, subject, body, html)
        print(json.dumps({"ok": True, "status": "sent", "provider": "smtp"}))
        return 0
    if provider == "resend":
        result = send_resend(config, recipient, subject, body, html)
        print(json.dumps({"ok": True, "status": "sent", "provider": "resend", "result": result}))
        return 0
    if provider == "ses":
        result = send_ses(config, recipient, subject, body, html)
        print(json.dumps({"ok": True, "status": "sent", "provider": "ses", "result": result}))
        return 0

    raise SystemExit("EMAIL_SKILL_PROVIDER must be smtp, resend, ses, or dry-run.")


if __name__ == "__main__":
    raise SystemExit(main())
