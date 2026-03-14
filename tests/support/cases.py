import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import repositories.bookings as bookings_repo
import repositories.analytics as analytics_repo
import repositories.categories as categories_repo
import repositories.schema as schema_repo
from repositories.schema import init_db


class RepositoryTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._db_path = Path.cwd() / f".test_{next(tempfile._get_candidate_names())}.db"
        self._patches = ExitStack()
        original_connect = bookings_repo.aiosqlite.connect

        def connect_override(_path, *args, **kwargs):
            return original_connect(self._db_path, *args, **kwargs)

        for module in (schema_repo, bookings_repo, categories_repo, analytics_repo):
            self._patches.enter_context(
                patch.object(module.aiosqlite, "connect", side_effect=connect_override)
            )

        await init_db()

    async def asyncTearDown(self):
        self._patches.close()
        if self._db_path.exists():
            self._db_path.unlink()
