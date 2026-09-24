"""Create the two safe demo tenants in the configured ONIX database."""

from __future__ import annotations

try:
    from .app import DB, init_db
    from .db import open_connection
except ImportError:
    from app import DB, init_db
    from db import open_connection


DEMO_CLIENTS = (
    (
        "test-element",
        "Element Barberia",
        "barberia",
        "https://search.google.com/local/writereview?placeid=ChIJW7lH0W7nuhIRkVBgA523l_c",
        "sorteo",
        "Corte gratis",
    ),
    (
        "test-cafe",
        "Cafe Demo",
        "cafeteria",
        "https://example.com/cafe-demo",
        "oferta",
        "Cafe gratis",
    ),
)


def main() -> None:
    init_db()
    connection = open_connection(DB)
    try:
        for client in DEMO_CLIENTS:
            connection.execute(
                """
                INSERT INTO clientes
                    (slug, nombre, sector, url_destino, tipo_campana, premio)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    nombre=excluded.nombre,
                    sector=excluded.sector,
                    url_destino=excluded.url_destino,
                    tipo_campana=excluded.tipo_campana,
                    premio=excluded.premio,
                    activo=1
                """,
                client,
            )
        connection.commit()
    finally:
        connection.close()
    print("Demo tenants ready: test-element, test-cafe")


if __name__ == "__main__":
    main()
