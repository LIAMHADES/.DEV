import importlib
import json
import re
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from werkzeug.security import generate_password_hash


PROJECT_ROOT = Path(__file__).resolve().parents[1] / "projects" / "onix"
sys.path.insert(0, str(PROJECT_ROOT))
tracking_app = importlib.import_module("tracking.app")


def seed_client(url="https://example.com/menu", activo=1, nombre="Demo", slug="demo"):
    with sqlite3.connect(tracking_app.DB) as connection:
        connection.execute(
            "INSERT INTO clientes (slug, nombre, sector, url_destino, activo) VALUES (?, ?, ?, ?, ?)",
            (slug, nombre, "cafeteria", url, activo),
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
        tracking_app.ADMIN_PASSWORD_HASH = generate_password_hash("onix2026")
        tracking_app.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        tracking_app.init_db()
        self.client = tracking_app.app.test_client()

    def tearDown(self):
        self.client = None
        tracking_app.DB = self.original_db
        tracking_app.ADMIN_PASSWORD_HASH = self.original_password_hash
        self.temp_dir.cleanup()

    def csrf_token(self):
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
        self.assertIsNotNone(match)
        return match.group(1)

    def test_nfc_route_tracks_and_embeds_safe_destination(self):
        seed_client()

        response = self.client.get("/t/demo", headers={"User-Agent": "TestPhone"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'window.location.href = "https://example.com/menu"',
            response.get_data(as_text=True),
        )
        self.assertIn('/onix-logo.png', response.get_data(as_text=True))
        logo_response = self.client.get('/onix-logo.png')
        self.assertEqual(logo_response.status_code, 200)
        self.assertEqual(logo_response.mimetype, "image/png")
        logo_response.close()
        self.assertEqual(count_rows("toques"), 1)

    def test_nfc_route_sets_cookie_and_marks_returning_visitor(self):
        seed_client()

        first = self.client.get("/t/demo", headers={"User-Agent": "TestPhone"})
        second = self.client.get("/t/demo", headers={"User-Agent": "TestPhone"})

        self.assertEqual(first.status_code, 200)
        self.assertIn("onix_vid_demo=", first.headers["Set-Cookie"])
        self.assertEqual(second.status_code, 200)
        self.assertEqual(count_rows("toques"), 2)
        with sqlite3.connect(tracking_app.DB) as connection:
            events = connection.execute(
                "SELECT es_recurrente, visitante_hash FROM eventos ORDER BY id"
            ).fetchall()
        self.assertEqual([event[0] for event in events], [0, 1])
        self.assertEqual(len({event[1] for event in events}), 1)

    def test_visitor_cookie_isolated_per_business(self):
        seed_client(slug="demo")
        seed_client(slug="other", nombre="Other")

        self.client.get("/t/demo")
        self.client.get("/t/other")

        with sqlite3.connect(tracking_app.DB) as connection:
            hashes = connection.execute(
                "SELECT slug, visitor_hash FROM toques ORDER BY slug"
            ).fetchall()
        self.assertEqual(len(hashes), 2)
        self.assertNotEqual(hashes[0][1], hashes[1][1])

    def test_nfc_route_preserves_element_maps_destination(self):
        destination = (
            "https://www.google.com/maps/place/Element+Barberia/"
            "@41.9771972,2.8185883,17z/data=!4m8!3m7!1s0x12bae76ed147b95b:"
            "0xf797b79d03605091!8m2!3d41.9771972!4d2.8185883!9m1!1b1!16s%2F"
            "g%2F11z5bqymc9?entry=ttu&g_ep=EgoyMDI2MDkxNi4wIKXMDSoASAFQAw%3D%3D"
        )
        seed_client(url=destination, nombre="Element Barberia")

        response = self.client.get("/t/demo")
        match = re.search(
            r"window\.location\.href = (.*?);", response.get_data(as_text=True)
        )

        self.assertIsNotNone(match)
        self.assertEqual(json.loads(match.group(1)), destination)

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

    def test_dashboard_requires_admin_session(self):
        seed_client()

        unauthorized = self.client.get("/d/demo")
        self.assertEqual(unauthorized.status_code, 302)
        self.assertEqual(unauthorized.headers["Location"], "/admin")

        self.client.post(
            "/admin/login",
            data={"password": "onix2026", "csrf_token": self.csrf_token()},
        )
        authorized = self.client.get("/d/demo")
        self.assertEqual(authorized.status_code, 200)

    def test_dashboard_counts_unique_new_and_returning_visitors(self):
        seed_client()
        self.client.get("/t/demo")
        self.client.get("/t/demo")

        self.client.post(
            "/admin/login",
            data={"password": "onix2026", "csrf_token": self.csrf_token()},
        )
        dashboard = self.client.get("/d/demo")
        body = dashboard.get_data(as_text=True)

        self.assertEqual(dashboard.status_code, 200)
        self.assertIn("Visitantes estimados</span><span>1", body)
        self.assertIn("Nuevos estimados</span><span>0", body)
        self.assertIn("Recurrentes estimados</span><span>1", body)

    def test_active_waitlist_page_sets_visitor_cookie(self):
        seed_client()

        response = self.client.get("/pedir/demo")

        self.assertEqual(response.status_code, 200)
        self.assertIn("onix_vid_demo=", response.headers["Set-Cookie"])

    def test_security_headers_are_present(self):
        response = self.client.get("/admin")

        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])

    def test_admin_mutations_require_csrf(self):
        token = self.csrf_token()
        login = self.client.post(
            "/admin/login", data={"password": "onix2026", "csrf_token": token}
        )
        self.assertEqual(login.status_code, 302)

        response = self.client.post(
            "/admin/add",
            data={
                "slug": "missing-csrf",
                "nombre": "Blocked",
                "url_destino": "https://example.com",
            },
        )
        self.assertEqual(response.status_code, 400)

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

        login = self.client.post(
            "/admin/login",
            data={"password": "onix2026", "csrf_token": self.csrf_token()},
        )
        self.assertEqual(login.status_code, 302)

        valid = self.client.post(
            "/admin/add",
            data={
                "slug": "demo",
                "nombre": "Demo",
                "url_destino": "https://example.com",
                "csrf_token": self.csrf_token(),
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
                "csrf_token": self.csrf_token(),
            },
        )
        self.assertEqual(invalid_url.status_code, 400)


if __name__ == "__main__":
    unittest.main()
