"""Append-only event recording and low-cost daily rollups for ONIX."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_timestamp(value: datetime | None = None) -> str:
    current = value or utc_now()
    return current.isoformat(timespec="seconds").replace("+00:00", "Z")


def _day_bounds(day: str) -> tuple[str, str]:
    start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return iso_timestamp(start), iso_timestamp(end)


def _safe_event_id(event_id: str | None) -> str:
    candidate = (event_id or "").strip()
    if 16 <= len(candidate) <= 128 and all(
        character.isalnum() or character in "._:-" for character in candidate
    ):
        return candidate
    return uuid4().hex


def record_usage(
    connection,
    slug: str,
    occurred: str,
    request_count: int = 0,
    event_count: int = 0,
    response_bytes: int = 0,
    latency_ms: int = 0,
) -> None:
    day = occurred[:10]
    connection.execute(
        """
        INSERT INTO uso_diario
            (negocio_slug, dia, peticiones, eventos, bytes_respuesta, latencia_total_ms)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (negocio_slug, dia) DO UPDATE SET
            peticiones = uso_diario.peticiones + excluded.peticiones,
            eventos = uso_diario.eventos + excluded.eventos,
            bytes_respuesta = uso_diario.bytes_respuesta + excluded.bytes_respuesta,
            latencia_total_ms = uso_diario.latencia_total_ms + excluded.latencia_total_ms
        """,
        (slug, day, request_count, event_count, response_bytes, latency_ms),
    )


def record_event(
    connection,
    slug: str,
    event_type: str,
    anonymous_id: str | None = None,
    is_returning: bool = False,
    source: str | None = None,
    campaign: str | None = None,
    device_class: str | None = None,
    event_id: str | None = None,
    latency_ms: int = 0,
    response_bytes: int = 0,
) -> bool:
    """Insert one event exactly once and meter its storage/processing usage."""
    occurred = iso_timestamp()
    cursor = connection.execute(
        """
        INSERT INTO eventos
            (negocio_slug, tipo_evento, visitante_hash, es_recurrente,
             dispositivo_tipo, fuente, campana, event_id, ocurrido,
             latencia_ms, respuesta_bytes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (negocio_slug, event_id) DO NOTHING
        """,
        (
            slug,
            event_type,
            anonymous_id,
            1 if is_returning else 0,
            device_class,
            source,
            campaign,
            _safe_event_id(event_id),
            occurred,
            max(0, int(latency_ms)),
            max(0, int(response_bytes)),
        ),
    )
    if getattr(cursor, "rowcount", 1) == 0:
        return False
    record_usage(
        connection,
        slug,
        occurred,
        request_count=1,
        event_count=1,
        response_bytes=response_bytes,
        latency_ms=latency_ms,
    )
    return True


def aggregate_day(connection, day: str) -> int:
    """Materialize dashboard metrics for one UTC day without scanning them live."""
    start, end = _day_bounds(day)
    rows = connection.execute(
        """
        SELECT
            negocio_slug,
            COUNT(*) AS toques,
            COUNT(DISTINCT CASE WHEN visitante_hash IS NOT NULL THEN visitante_hash END),
            COUNT(DISTINCT CASE WHEN visitante_hash IS NOT NULL AND es_recurrente = 0 THEN visitante_hash END),
            COUNT(DISTINCT CASE WHEN visitante_hash IS NOT NULL AND es_recurrente = 1 THEN visitante_hash END),
            COALESCE(AVG(latencia_ms), 0),
            COALESCE(SUM(respuesta_bytes), 0)
        FROM eventos
        WHERE ocurrido >= ? AND ocurrido < ?
        GROUP BY negocio_slug
        """,
        (start, end),
    ).fetchall()

    for row in rows:
        slug, taps, unique_visitors, new_visitors, returning_visitors, avg_latency, bytes_total = row
        leads = connection.execute(
            """
            SELECT COUNT(*) FROM leads_clientes
            WHERE negocio_slug=? AND fecha_captacion >= ? AND fecha_captacion < ?
            """,
            (slug, start, end),
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO metricas_diarias
                (negocio_slug, dia, toques, visitantes_unicos,
                 visitantes_nuevos, visitantes_recurrentes, leads,
                 latencia_media_ms, bytes_respuesta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (negocio_slug, dia) DO UPDATE SET
                toques = excluded.toques,
                visitantes_unicos = excluded.visitantes_unicos,
                visitantes_nuevos = excluded.visitantes_nuevos,
                visitantes_recurrentes = excluded.visitantes_recurrentes,
                leads = excluded.leads,
                latencia_media_ms = excluded.latencia_media_ms,
                bytes_respuesta = excluded.bytes_respuesta,
                actualizado = CURRENT_TIMESTAMP
            """,
            (
                slug,
                day,
                taps,
                unique_visitors,
                new_visitors,
                returning_visitors,
                leads,
                round(float(avg_latency), 2),
                bytes_total,
            ),
        )
    return len(rows)
