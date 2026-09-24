-- ONIX tracking schema for Supabase/PostgreSQL.
-- The Flask app can still bootstrap the same shape locally in SQLite.

create table if not exists clientes (
    slug text primary key,
    nombre text not null,
    sector text,
    url_destino text not null,
    activo integer not null default 1,
    creado text not null default current_timestamp::text,
    tipo_campana text not null default 'sorteo',
    premio text not null default ''
);

create table if not exists toques (
    id bigserial primary key,
    slug text not null references clientes(slug),
    fecha text not null default current_timestamp::text,
    dispositivo text,
    device_id text,
    device_hash text,
    visitor_hash text
);

create table if not exists leads_clientes (
    id bigserial primary key,
    negocio_slug text not null references clientes(slug),
    telefono text,
    email text,
    nombre text,
    fecha_captacion text not null default current_timestamp::text,
    fuente text,
    motivo text,
    acepta_campanas integer not null default 0,
    texto_consentimiento text,
    acepta_insights_sector integer not null default 0,
    texto_consentimiento_insights text,
    device_hash text,
    visitor_hash text
);

create table if not exists eventos (
    id bigserial primary key,
    negocio_slug text not null references clientes(slug),
    tipo_evento text not null,
    ocurrido text not null default current_timestamp::text,
    visitante_hash text,
    es_recurrente integer not null default 0,
    dispositivo_tipo text,
    fuente text,
    campana text
);

create index if not exists idx_toques_slug on toques(slug);
create index if not exists idx_leads_slug on leads_clientes(negocio_slug);
create index if not exists idx_toques_hash on toques(device_hash);
create index if not exists idx_toques_visitor on toques(visitor_hash);
create index if not exists idx_eventos_negocio on eventos(negocio_slug, ocurrido);
