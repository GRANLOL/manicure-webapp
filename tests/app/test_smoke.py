import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

import bot_handlers
import main


class AppSmokeTests(unittest.IsolatedAsyncioTestCase):
    def test_router_is_aggregated(self):
        self.assertGreater(len(bot_handlers.router.sub_routers), 0)

    def test_require_webapp_auth_rejects_invalid_data(self):
        with patch.object(main, "WEBAPP_AUTH_REQUIRED", True), \
             patch.object(main, "verify_telegram_init_data", return_value=False):
            with self.assertRaises(HTTPException) as ctx:
                main.require_webapp_auth("bad")

        self.assertEqual(ctx.exception.status_code, 401)

    async def test_get_content_returns_expected_shape(self):
        with patch.object(main, "require_webapp_auth"), \
             patch.object(main, "get_all_services", AsyncMock(return_value=[{"id": 1}])), \
             patch.object(main, "get_all_categories", AsyncMock(return_value=[{"id": 2}])), \
             patch.object(main, "get_all_masters", AsyncMock(return_value=[{"id": 3}])):
            content = await main.get_content("init-data")

        self.assertIn("services", content)
        self.assertIn("categories", content)
        self.assertIn("masters", content)
        self.assertIn("booking_window", content)
