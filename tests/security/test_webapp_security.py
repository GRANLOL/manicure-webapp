import hashlib
import hmac
import time
import unittest

from webapp_security import allowed_origins, verify_telegram_init_data


def build_init_data(bot_token: str, **fields: str) -> str:
    payload = {**fields}
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(payload.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    payload_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    pairs = [f"{key}={value}" for key, value in payload.items()]
    pairs.append(f"hash={payload_hash}")
    return "&".join(pairs)


class WebappSecurityTests(unittest.TestCase):
    def test_allowed_origins_includes_webapp_origin_and_default_origin(self):
        origins = allowed_origins("https://example.com/app/index.html")

        self.assertIn("https://example.com", origins)
        self.assertIn("https://granlol.github.io", origins)

    def test_verify_telegram_init_data_accepts_valid_signature(self):
        bot_token = "123:abc"
        init_data = build_init_data(
            bot_token,
            auth_date=str(int(time.time())),
            query_id="AAEAAAE",
            user='{"id":1,"first_name":"Test"}',
        )

        self.assertTrue(verify_telegram_init_data(init_data, bot_token))

    def test_verify_telegram_init_data_rejects_expired_signature(self):
        bot_token = "123:abc"
        init_data = build_init_data(
            bot_token,
            auth_date=str(int(time.time()) - 90000),
            query_id="AAEAAAE",
            user='{"id":1,"first_name":"Test"}',
        )

        self.assertFalse(verify_telegram_init_data(init_data, bot_token))

    def test_verify_telegram_init_data_rejects_tampered_signature(self):
        bot_token = "123:abc"
        init_data = build_init_data(
            bot_token,
            auth_date=str(int(time.time())),
            query_id="AAEAAAE",
            user='{"id":1,"first_name":"Test"}',
        ).replace("Test", "Hacker")

        self.assertFalse(verify_telegram_init_data(init_data, bot_token))
