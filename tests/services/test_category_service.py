import unittest

from category_service import filter_valid_parent_categories


class CategoryServiceTests(unittest.TestCase):
    def test_filter_valid_parent_categories_excludes_current_category_and_descendants(self):
        categories = [
            {"id": 1, "name": "Root", "parent_id": None},
            {"id": 2, "name": "Child", "parent_id": 1},
            {"id": 3, "name": "Grandchild", "parent_id": 2},
            {"id": 4, "name": "Sibling", "parent_id": 1},
        ]

        valid = filter_valid_parent_categories(categories, {2, 3})

        self.assertEqual([category["id"] for category in valid], [1, 4])
