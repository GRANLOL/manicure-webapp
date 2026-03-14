import unittest

import bot_keyboards.catalog as catalog_keyboards
import bot_keyboards.menus as menu_keyboards


class KeyboardTests(unittest.TestCase):
    def test_get_main_menu_adds_admin_and_master_buttons(self):
        base_markup = menu_keyboards.get_main_menu(is_admin=False, is_master=False)
        extended_markup = menu_keyboards.get_main_menu(is_admin=True, is_master=True)

        base_count = sum(len(row) for row in base_markup.keyboard)
        extended_count = sum(len(row) for row in extended_markup.keyboard)

        self.assertGreater(extended_count, base_count)

    def test_build_category_tree_avoids_infinite_recursion_with_cycle(self):
        categories = [
            {"id": 1, "name": "Root", "parent_id": None},
            {"id": 2, "name": "Child", "parent_id": 1},
            {"id": 1, "name": "RootAgain", "parent_id": 2},
        ]

        tree = catalog_keyboards.build_category_tree(categories)

        self.assertTrue(len(tree) >= 2)

    def test_get_services_keyboard_adds_navigation_and_create_button(self):
        services = [{"id": index, "name": f"Service {index}", "price": str(index), "category_name": None} for index in range(25)]

        markup = catalog_keyboards.get_services_keyboard(services, page=0, page_size=20)
        callback_data = [button.callback_data for row in markup.inline_keyboard for button in row]

        self.assertIn("srv_page_1", callback_data)
        self.assertIn("add_service", callback_data)
