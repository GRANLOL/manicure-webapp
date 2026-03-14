import hashlib
import hmac
import time
from urllib.parse import parse_qsl, urlparse


def allowed_origins(webapp_url: str) -> list[str]:
    origins = {"https://granlol.github.io"}
    parsed = urlparse(webapp_url)
    if parsed.scheme and parsed.netloc:
        origins.add(f"{parsed.scheme}://{parsed.netloc}")
    return sorted(origins)


def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    if not init_data:
        return False

    pairs = parse_qsl(init_data, keep_blank_values=True)
    data = dict(pairs)
    received_hash = data.pop("hash", None)
    if not received_hash:
        return False

    auth_date = data.get("auth_date")
    if not auth_date:
        return False

    try:
        if time.time() - int(auth_date) > 86400:
            return False
    except ValueError:
        return False

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(calculated_hash, received_hash)
