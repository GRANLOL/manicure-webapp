import unittest

from repositories.analytics import get_revenue_stats
from repositories.bookings import create_booking_if_available, get_all_bookings
from repositories.categories import (
    add_category,
    delete_category,
    get_all_categories,
    update_category_parent,
)
from tests.support import RepositoryTestCase


class BookingRepositoryTests(RepositoryTestCase):
    async def test_create_booking_prevents_overlap_for_same_master(self):
        created = await create_booking_if_available(
            user_id=1,
            name="Alice",
            phone="+10000000001",
            date="14.03.2026",
            time="10:00",
            master_id=1,
            duration=60,
            service_name="РњР°РЅРёРєСЋСЂ",
            price=2000,
        )
        overlapping = await create_booking_if_available(
            user_id=2,
            name="Bob",
            phone="+10000000002",
            date="14.03.2026",
            time="10:30",
            master_id=1,
            duration=60,
            service_name="РњР°РЅРёРєСЋСЂ",
            price=2000,
        )
        other_master = await create_booking_if_available(
            user_id=3,
            name="Carol",
            phone="+10000000003",
            date="14.03.2026",
            time="10:30",
            master_id=2,
            duration=60,
            service_name="РњР°РЅРёРєСЋСЂ",
            price=2000,
        )

        bookings = await get_all_bookings()

        self.assertTrue(created)
        self.assertFalse(overlapping)
        self.assertTrue(other_master)
        self.assertEqual(len(bookings), 2)

    async def test_create_booking_allows_non_overlapping_slots(self):
        first = await create_booking_if_available(
            user_id=1,
            name="Alice",
            phone="+10000000001",
            date="14.03.2026",
            time="10:00",
            master_id=1,
            duration=60,
        )
        second = await create_booking_if_available(
            user_id=2,
            name="Bob",
            phone="+10000000002",
            date="14.03.2026",
            time="11:00",
            master_id=1,
            duration=60,
        )

        self.assertTrue(first)
        self.assertTrue(second)

    async def test_revenue_stats_counts_bookings_in_period(self):
        await create_booking_if_available(
            user_id=1,
            name="Alice",
            phone="+10000000001",
            date="15.03.2026",
            time="10:00",
            master_id=1,
            duration=60,
            service_name="Маникюр",
            price=2000,
        )

        stats = await get_revenue_stats(30)

        self.assertEqual(stats["total_bookings"], 1)
        self.assertEqual(stats["total_revenue"], 2000)


class CategoryRepositoryTests(RepositoryTestCase):
    async def test_update_category_parent_rejects_descendant_cycle(self):
        await add_category("Root")
        await add_category("Child", parent_id=1)
        await add_category("Grandchild", parent_id=2)

        with self.assertRaises(ValueError):
            await update_category_parent(1, 3)

    async def test_delete_category_reparents_children_to_deleted_parent_parent(self):
        await add_category("Root")
        await add_category("Child", parent_id=1)
        await add_category("Grandchild", parent_id=2)

        await delete_category(2)
        categories = await get_all_categories()
        by_id = {category["id"]: category for category in categories}

        self.assertNotIn(2, by_id)
        self.assertEqual(by_id[3]["parent_id"], 1)
