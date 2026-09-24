-- ONIX scalable analytics foundation.
-- Apply after 001_initial.sql in PostgreSQL/Supabase.

alter table eventos add column if not exists event_id text;
alter table eventos add column if not exists latencia_ms integer not null default 0;
alter table eventos add column if not exists respuesta_bytes integer not null default 0;

create unique index if not exists idx_eventos_idempotency
    on eventos(negocio_slug, event_id);
create index if not exists idx_eventos_rollup
    on eventos(negocio_slug, ocurrido, visitante_hash);

create table if not exists metricas_diarias (
    negocio_slug text not null references clientes(slug),
    dia date not null,
    toques bigint not null default 0,
    visitantes_unicos bigint not null default 0,
    visitantes_nuevos bigint not null default 0,
    visitantes_recurrentes bigint not null default 0,
    leads bigint not null default 0,
    latencia_media_ms numeric(12,2) not null default 0,
    bytes_respuesta bigint not null default 0,
    actualizado timestamptz not null default now(),
    primary key (negocio_slug, dia)
);

create table if not exists uso_diario (
    negocio_slug text not null references clientes(slug),
    dia date not null,
    peticiones bigint not null default 0,
    eventos bigint not null default 0,
    bytes_respuesta bigint not null default 0,
    latencia_total_ms bigint not null default 0,
    actualizado timestamptz not null default now(),
    primary key (negocio_slug, dia)
);

create index if not exists idx_metricas_dia on metricas_diarias(dia);
create index if not exists idx_uso_dia on uso_diario(dia);
