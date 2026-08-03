import os
import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

os.environ["RUN_BACKGROUND_SERVICES"] = "false"
os.environ["AUTO_PUBLISH"] = "false"
os.environ["ADMIN_TOKEN"] = "1234567890123456789012345678901234567890"
os.environ["DATABASE_URL"] = "sqlite://"

from app import database  # noqa: E402

database.engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
database.SessionLocal.configure(bind=database.engine)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.models import Article, Category  # noqa: E402


TOKEN = "1234567890123456789012345678901234567890"


class AdminApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()
        cls.headers = {"X-Admin-Token": TOKEN}

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)

    def setUp(self):
        db = database.SessionLocal()
        db.query(Article).delete()
        category = db.query(Category).first()
        article = Article(
            title="Admin tahrirlash uchun sinov maqolasi",
            seo_title="Admin tahrirlash uchun sinov maqolasi SEO",
            slug="admin-tahrirlash-sinovi",
            summary="Admin panel orqali yangilanadigan yetarlicha uzun sinov xulosasi.",
            content="Admin panel tahrirlash sinovi uchun maqola matni. " * 10,
            practical_note="Bu o'zgarish administrator ishini tezlashtiradi.",
            tags=["AI", "audit"],
            importance=3,
            original_title="Original AI admin story",
            original_url="https://example.com/admin-audit",
            source_name="Example",
            category_id=category.id,
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(article)
        db.commit()
        self.article_id = article.id
        self.category_id = category.id
        db.close()

    def test_admin_requires_token(self):
        response = self.client.get("/api/admin/stats")
        self.assertEqual(response.status_code, 401)

    def test_admin_can_edit_article(self):
        response = self.client.put(
            f"/api/admin/articles/{self.article_id}",
            headers=self.headers,
            json={
                "title": "Tahrirlangan admin sinov maqolasi",
                "seo_title": "Tahrirlangan admin sinov maqolasi SEO",
                "summary": "Yangilangan va tekshiruvdan o'tgan yetarlicha uzun xulosa matni.",
                "content": "Yangilangan maqola matni va faktlari. " * 10,
                "practical_note": "Yangilangan amaliy izoh foydalanuvchiga qiymat beradi.",
                "tags": ["AI", "AI", " audit "],
                "importance": 5,
                "category_id": self.category_id,
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["tags"], ["AI", "audit"])
        self.assertEqual(response.json()["importance"], 5)

    def test_admin_rejects_invalid_importance(self):
        response = self.client.put(
            f"/api/admin/articles/{self.article_id}",
            headers=self.headers,
            json={"importance": 9},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
