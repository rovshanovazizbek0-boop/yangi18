import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.database import Base
from app import models  # noqa: F401


class MigrationTests(unittest.TestCase):
    def config(self) -> Config:
        return Config(Path(__file__).parents[1] / "alembic.ini")

    def database_url(self, directory: str, name: str) -> str:
        return f"sqlite:///{(Path(directory) / name).as_posix()}"

    def test_fresh_database_reaches_head_without_schema_diff(self):
        with tempfile.TemporaryDirectory() as directory:
            url = self.database_url(directory, "fresh.db")
            with patch.dict(os.environ, {"DATABASE_URL": url}):
                command.upgrade(self.config(), "head")
                command.check(self.config())

            engine = create_engine(url)
            try:
                tables = set(inspect(engine).get_table_names())
                self.assertTrue({"alembic_version", "articles", "categories", "tools"} <= tables)
            finally:
                engine.dispose()

    def test_existing_create_all_database_can_adopt_the_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            url = self.database_url(directory, "legacy.db")
            engine = create_engine(url)
            Base.metadata.create_all(engine)
            engine.dispose()

            with patch.dict(os.environ, {"DATABASE_URL": url}):
                command.upgrade(self.config(), "head")

            engine = create_engine(url)
            try:
                self.assertIn("alembic_version", inspect(engine).get_table_names())
            finally:
                engine.dispose()


if __name__ == "__main__":
    unittest.main()
