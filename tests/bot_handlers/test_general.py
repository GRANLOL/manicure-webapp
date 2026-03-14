import unittest
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import bot_handlers.general as general_handlers
from tests.support import make_message


class GeneralHandlerTests(unittest.IsolatedAsyncioTestCase):
    async def test_start_handler_opens_master_panel_for_master(self):
        message = make_message(user_id=10)

        with patch.object(general_handlers, "getenv", return_value=None), \
             patch.dict(general_handlers.salon_config, {"use_masters": True}, clear=False), \
             patch.object(general_handlers.database, "get_master_by_telegram_id", AsyncMock(return_value={"id": 1})):
            await general_handlers.start_handler(message)

        message.answer.assert_awaited_once_with(ANY, reply_markup=general_handlers.keyboards.master_menu)

    async def test_start_handler_uses_client_menu_for_regular_user(self):
        message = make_message(user_id=10)

        with patch.object(general_handlers, "getenv", return_value=None), \
             patch.dict(general_handlers.salon_config, {"use_masters": False, "welcome_text": "hello"}, clear=False), \
             patch.object(general_handlers.keyboards, "get_main_menu", return_value="menu"), \
             patch.object(general_handlers.keyboards, "get_booking_launch_keyboard", return_value="launch"):
            await general_handlers.start_handler(message)

        self.assertEqual(message.answer.await_count, 2)
        message.answer.assert_any_await("hello", reply_markup="launch")
        message.answer.assert_any_await("Меню клиента обновлено.", reply_markup="menu")

    async def test_client_menu_handler_refreshes_launch_and_reply_keyboards(self):
        message = make_message(user_id=1, text="👤 Меню клиента")

        with patch.object(general_handlers, "getenv", return_value="1"), \
             patch.dict(general_handlers.salon_config, {"use_masters": False}, clear=False), \
             patch.object(general_handlers.keyboards, "get_main_menu", return_value="menu"), \
             patch.object(general_handlers.keyboards, "get_booking_launch_keyboard", return_value="launch"):
            await general_handlers.client_menu_handler(message)

        self.assertEqual(message.answer.await_count, 2)
        message.answer.assert_any_await("Вы переключились в главное меню клиента.", reply_markup="launch")
        message.answer.assert_any_await("Меню клиента обновлено.", reply_markup="menu")

    async def test_export_excel_handler_sends_document_for_admin(self):
        message = make_message(user_id=1)
        fake_df = MagicMock()

        with patch.object(general_handlers, "getenv", return_value="1"), \
             patch.object(general_handlers.database, "get_all_bookings", AsyncMock(return_value=[("A", "B", "C", "D", "E")])), \
             patch.object(general_handlers.pd, "DataFrame", return_value=fake_df), \
             patch.object(general_handlers, "FSInputFile", return_value="excel-file"), \
             patch.object(general_handlers.os, "remove") as remove_mock:
            await general_handlers.export_excel_handler(message)

        fake_df.to_excel.assert_called_once()
        message.answer_document.assert_awaited_once_with("excel-file", caption=ANY)
        remove_mock.assert_called_once()
