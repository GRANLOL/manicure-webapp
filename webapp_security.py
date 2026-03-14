import hashlib
import hmac
import time
from urllib.parse import parse_qsl, urlparse
import json


def allowed_origins(webapp_url: str) -> list[str]:
    origins = {"https://granlol.github.io"}
    parsed = urlparse(webapp_url)
    if parsed.scheme and parsed.netloc:
        origins.add(f"{parsed.scheme}://{parsed.netloc}")
    return sorted(origins)


def get_init_data_validation_error(init_data: str, bot_token: str) -> str | None:
    if not init_data:
        return "missing init data"

    pairs = parse_qsl(init_data, keep_blank_values=True)
    data = dict(pairs)
    received_hash = data.pop("hash", None)
    if not received_hash:
        return "missing hash"

    auth_date = data.get("auth_date")
    if not auth_date:
        return "missing auth_date"

    try:
        auth_age = time.time() - int(auth_date)
    except ValueError:
        return "invalid auth_date"

    if auth_age > 86400:
        return f"expired auth_date ({int(auth_age)}s old)"

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated_hash, received_hash):
        return "hash mismatch"

    return None


def parse_init_data(init_data: str) -> dict[str, str]:
    return dict(parse_qsl(init_data, keep_blank_values=True))


def get_user_from_init_data(init_data: str) -> dict | None:
    data = parse_init_data(init_data)
    raw_user = data.get("user")
    if not raw_user:
        return None
    try:
        return json.loads(raw_user)
    except json.JSONDecodeError:
        return None


def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    return get_init_data_validation_error(init_data, bot_token) is None
