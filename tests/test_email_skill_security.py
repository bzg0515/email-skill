import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skill"))

from email_skill import config
from email_skill.config import ConfigFilePermissionError
from email_skill.send_email import validate_payload


class ConfigLoadingTests(unittest.TestCase):
    def setUp(self):
        self.old_env = os.environ.copy()
        self.old_skill_dir = config.SKILL_DIR

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_env)
        config.SKILL_DIR = self.old_skill_dir

    def test_default_config_ignores_caller_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skill"
            caller_dir = root / "caller"
            skill_dir.mkdir()
            caller_dir.mkdir()
            (skill_dir / "email-skill.env").write_text(
                "\n".join(
                    [
                        "EMAIL_SKILL_PROVIDER=dry-run",
                        "EMAIL_SKILL_FROM=trusted@example.com",
                        "EMAIL_SKILL_ALLOWED_RECIPIENTS=trusted@example.com",
                    ]
                )
            )
            (caller_dir / "email-skill.env").write_text(
                "\n".join(
                    [
                        "EMAIL_SKILL_PROVIDER=dry-run",
                        "EMAIL_SKILL_FROM=attacker@example.com",
                        "EMAIL_SKILL_ALLOWED_RECIPIENTS=attacker@example.com",
                    ]
                )
            )

            os.environ.clear()
            config.SKILL_DIR = skill_dir
            old_cwd = Path.cwd()
            try:
                os.chdir(caller_dir)
                loaded, loaded_from = config.load_config()
            finally:
                os.chdir(old_cwd)

            self.assertEqual(loaded_from, str((skill_dir / "email-skill.env").resolve()))
            self.assertEqual(loaded["EMAIL_SKILL_FROM"], "trusted@example.com")
            self.assertEqual(loaded["EMAIL_SKILL_ALLOWED_RECIPIENTS"], "trusted@example.com")

    @unittest.skipUnless(os.name == "posix", "POSIX file mode check")
    def test_rejects_group_or_world_readable_credential_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / "email-skill.env"
            env_file.write_text(
                "\n".join(
                    [
                        "EMAIL_SKILL_PROVIDER=smtp",
                        "EMAIL_SKILL_FROM=you@example.com",
                        "EMAIL_SKILL_ALLOWED_RECIPIENTS=you@example.com",
                        "EMAIL_SKILL_SMTP_HOST=smtp.example.com",
                        "EMAIL_SKILL_SMTP_PORT=587",
                        "EMAIL_SKILL_SMTP_USER=you@example.com",
                        "EMAIL_SKILL_SMTP_PASSWORD=real-secret-value",
                    ]
                )
            )
            env_file.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

            os.environ.clear()
            os.environ["EMAIL_SKILL_CONFIG"] = str(env_file)

            with self.assertRaises(ConfigFilePermissionError):
                config.load_config()

    @unittest.skipUnless(os.name == "posix", "POSIX file mode check")
    def test_allows_group_readable_placeholder_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / "email-skill.env"
            env_file.write_text(
                "\n".join(
                    [
                        "EMAIL_SKILL_PROVIDER=dry-run",
                        "EMAIL_SKILL_FROM=digests@example.com",
                        "EMAIL_SKILL_ALLOWED_RECIPIENTS=test@example.com",
                        "EMAIL_SKILL_SMTP_PASSWORD=your-app-password",
                    ]
                )
            )
            env_file.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

            os.environ.clear()
            os.environ["EMAIL_SKILL_CONFIG"] = str(env_file)

            loaded, _ = config.load_config()
            self.assertEqual(loaded["EMAIL_SKILL_PROVIDER"], "dry-run")


class PayloadValidationTests(unittest.TestCase):
    def test_html_requires_explicit_payload_flag(self):
        base_config = {
            "EMAIL_SKILL_ALLOWED_RECIPIENTS": "user@example.com",
        }
        payload = {
            "recipient": "user@example.com",
            "subject": "Digest",
            "body": "<b>still text</b>",
            "confirmed": True,
        }
        self.assertFalse(validate_payload(payload, base_config)[3])

        payload["html"] = True
        self.assertTrue(validate_payload(payload, base_config)[3])


if __name__ == "__main__":
    unittest.main()
