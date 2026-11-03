import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.database import Base, FALLBACK_SQLITE_URL, normalize_database_url, resolve_database_url
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
                self.assertTrue(
                    {"alembic_version", "articles", "categories", "tools", "guides"}
                    <= tables
                )
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

    def test_postgres_scheme_is_normalized(self):
        self.assertEqual(
            normalize_database_url("postgres://user:pass@host:5432/db"),
            "postgresql+psycopg2://user:pass@host:5432/db",
        )
        self.assertEqual(
            normalize_database_url("postgresql://user:pass@host:5432/db"),
            "postgresql+psycopg2://user:pass@host:5432/db",
        )

    @patch("app.database.create_engine")
    def test_unreachable_postgres_falls_back_to_sqlite(self, mock_engine):
        mock_engine.side_effect = RuntimeError("connection refused")
        self.assertEqual(
            resolve_database_url("postgresql+psycopg2://user:pass@127.0.0.1:59999/db"),
            FALLBACK_SQLITE_URL,
        )


if __name__ == "__main__":
    unittest.main()
