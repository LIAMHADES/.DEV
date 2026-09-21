import importlib
import hashlib
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1] / "projects" / "onix"
sys.path.insert(0, str(PROJECT_ROOT))
tracking_app = importlib.import_module("tracking.app")


def seed_client(url="https://example.com/menu", activo=1, nombre="Demo"):
    with sqlite3.connect(tracking_app.DB) as connection:
        connection.execute(
            "INSERT INTO clientes (slug, nombre, sector, url_destino, activo) VALUES (?, ?, ?, ?, ?)",
            ("demo", nombre, "cafeteria", url, activo),
        )
        connection.commit()


def count_rows(table):
    with sqlite3.connect(tracking_app.DB) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


class TrackingAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_db = tracking_app.DB
        self.original_password_hash = tracking_app.ADMIN_PASSWORD_HASH
        tracking_app.DB = str(Path(self.temp_dir.name) / "tracking.db")
        tracking_app.ADMIN_PASSWORD_HASH = hashlib.sha256(b"onix2026").hexdigest()
        tracking_app.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        tracking_app.init_db()
        self.client = tracking_app.app.test_client()

    def tearDown(self):
        self.client = None
        tracking_app.DB = self.original_db
        tracking_app.ADMIN_PASSWORD_HASH = self.original_password_hash
        self.temp_dir.cleanup()

    def test_nfc_route_tracks_and_embeds_safe_destination(self):
        seed_client()

        response = self.client.get("/t/demo", headers={"User-Agent": "TestPhone"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'window.location.href = "https://example.com/menu"',
            response.get_data(as_text=True),
        )
        self.assertEqual(count_rows("toques"), 1)

    def test_inactive_client_does_not_track_or_redirect(self):
        seed_client(activo=0)

        response = self.client.get("/t/demo")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(count_rows("toques"), 0)

    def test_invalid_destination_is_rejected_at_runtime(self):
        seed_client(url="javascript:alert(1)")

        response = self.client.get("/t/demo")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(count_rows("toques"), 0)

    def test_capture_validates_phone_and_persists_consent(self):
        seed_client(nombre="Cafe <Demo>")

        invalid = self.client.post("/c/demo", json={"telefono": "not-a-phone"})
        self.assertEqual(invalid.status_code, 400)

        valid = self.client.post(
            "/c/demo",
            json={
                "telefono": "+34600111222",
                "nombre": "Ana",
                "acepta_campanas": True,
                "acepta_insights_sector": True,
            },
        )

        self.assertEqual(valid.status_code, 200)
        self.assertEqual(valid.get_json(), {"ok": True})
        self.assertEqual(count_rows("leads_clientes"), 1)
        with sqlite3.connect(tracking_app.DB) as connection:
            lead = connection.execute(
                "SELECT acepta_campanas, acepta_insights_sector, texto_consentimiento, texto_consentimiento_insights FROM leads_clientes"
            ).fetchone()
        self.assertEqual(lead[0:2], (1, 1))
        self.assertIn("Cafe <Demo>", lead[2])
        self.assertIn("Cafe <Demo>", lead[3])

    def test_public_capture_routes_require_active_existing_client(self):
        self.assertEqual(
            self.client.post(
                "/menu/missing/captura", json={"email": "a@example.com"}
            ).status_code,
            404,
        )

        seed_client(activo=0)
        self.assertEqual(self.client.get("/c/demo").status_code, 404)
        self.assertEqual(self.client.get("/pedir/demo").status_code, 404)
        self.assertEqual(self.client.get("/menu/demo").status_code, 404)

    def test_menu_capture_validates_email_and_optional_phone(self):
        seed_client()

        invalid_email = self.client.post(
            "/menu/demo/captura", json={"email": "invalid"}
        )
        self.assertEqual(invalid_email.status_code, 400)

        valid = self.client.post(
            "/menu/demo/captura",
            json={"email": "a@example.com", "telefono": "+34600111222"},
        )
        self.assertEqual(valid.status_code, 200)
        self.assertEqual(count_rows("leads_clientes"), 1)

    def test_admin_uses_session_and_validates_client_data(self):
        unauthorized = self.client.post(
            "/admin/add",
            data={
                "slug": "private",
                "nombre": "Private",
                "url_destino": "https://example.com",
            },
        )
        self.assertEqual(unauthorized.status_code, 403)

        login = self.client.post("/admin/login", data={"password": "onix2026"})
        self.assertEqual(login.status_code, 302)

        valid = self.client.post(
            "/admin/add",
            data={
                "slug": "demo",
                "nombre": "Demo",
                "url_destino": "https://example.com",
            },
        )
        self.assertEqual(valid.status_code, 302)
        self.assertEqual(count_rows("clientes"), 1)

        invalid_url = self.client.post(
            "/admin/add",
            data={
                "slug": "unsafe",
                "nombre": "Unsafe",
                "url_destino": "javascript:alert(1)",
            },
        )
        self.assertEqual(invalid_url.status_code, 400)


if __name__ == "__main__":
    unittest.main()
