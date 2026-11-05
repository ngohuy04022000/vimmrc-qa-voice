"""Unit and integration tests for Web UI static serving and API documentation."""
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from api_server import app


class WebUIIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_frontend_index_serving(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("<app-root></app-root>", response.text)

    def test_frontend_static_assets_serving(self):
        dist_dir = ROOT / "web-interface_Luong" / "dist" / "web-interface" / "browser"
        js_files = list(dist_dir.glob("main-*.js"))
        if js_files:
            js_name = js_files[0].name
            response = self.client.get(f"/{js_name}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("javascript", response.headers.get("content-type", "").lower())
            self.assertGreater(len(response.content), 1000)

        css_files = list(dist_dir.glob("styles-*.css"))
        if css_files:
            css_name = css_files[0].name
            response = self.client.get(f"/{css_name}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("css", response.headers.get("content-type", "").lower())

    def test_swagger_and_openapi_docs(self):
        # Swagger UI
        docs_res = self.client.get("/docs")
        self.assertEqual(docs_res.status_code, 200)
        self.assertIn("text/html", docs_res.headers.get("content-type", ""))

        # OpenAPI schema
        openapi_res = self.client.get("/openapi.json")
        self.assertEqual(openapi_res.status_code, 200)
        schema = openapi_res.json()
        self.assertEqual(schema.get("info", {}).get("title"), "ViMMRC Voice Q&A API")
        paths = schema.get("paths", {})
        self.assertIn("/api/health", paths)
        self.assertIn("/api/retrieve", paths)
        self.assertIn("/api/answer", paths)
        self.assertIn("/api/tts", paths)
        self.assertIn("/api/stt", paths)

    def test_health_reports_frontend_served(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("frontend_served"))

    def test_api_404_routing(self):
        response = self.client.get("/api/nonexistent_endpoint")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
