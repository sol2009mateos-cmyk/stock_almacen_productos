-- ============================================
-- StockMaster Pro - Esquema Supabase
-- Ejecutar esto en Supabase > SQL Editor > New Query
-- ============================================

-- Extensión para UUID (por si la necesitamos a futuro)
create extension if not exists "pgcrypto";

-- ============================================
-- Tabla: productos
-- ============================================
create table productos (
  id bigint generated always as identity primary key,
  nombre text not null,
  categoria text not null,
  marca text,
  precio_costo numeric(12,2) not null default 0,
  precio_venta numeric(12,2) not null default 0,
  stock integer not null default 0,
  codigo_barras text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_productos_categoria on productos(categoria);
create index idx_productos_nombre on productos(nombre);

-- ============================================
-- Tabla: config (única fila, configuración del negocio)
-- ============================================
create table config (
  id integer primary key default 1,
  nombre_negocio text not null default 'Mi Negocio',
  direccion text,
  cuit text,
  iva_porcentaje numeric(5,2) not null default 21.00,
  comprobante_prefijo text not null default 'T-',
  comprobante_numero_actual integer not null default 1,
  banco_nombre text,
  banco_cbu text,
  banco_alias text,
  constraint solo_una_fila check (id = 1)
);

insert into config (id) values (1);

-- ============================================
-- Tabla: favoritos (accesos F1-F8 del punto de venta)
-- ============================================
create table favoritos (
  id bigint generated always as identity primary key,
  slot integer not null unique check (slot between 1 and 8),
  producto_id bigint references productos(id) on delete set null
);

-- Pre-cargamos los 8 slots vacíos
insert into favoritos (slot, producto_id)
select generate_series(1,8), null;

-- ============================================
-- Tabla: ventas (cabecera de cada venta)
-- ============================================
create table ventas (
  id bigint generated always as identity primary key,
  numero_comprobante text not null unique,
  fecha timestamptz not null default now(),
  metodo_pago text not null check (metodo_pago in ('efectivo','tarjeta','transferencia')),
  cuotas integer,
  monto_recibido numeric(12,2),
  vuelto numeric(12,2),
  referencia_transferencia text,
  subtotal numeric(12,2) not null,
  iva_total numeric(12,2) not null,
  total numeric(12,2) not null
);

create index idx_ventas_fecha on ventas(fecha);

-- ============================================
-- Tabla: venta_items (detalle de productos por venta)
-- ============================================
create table venta_items (
  id bigint generated always as identity primary key,
  venta_id bigint not null references ventas(id) on delete cascade,
  producto_id bigint references productos(id) on delete set null,
  nombre_producto text not null, -- copia por si el producto se borra despues
  cantidad integer not null,
  precio_unitario numeric(12,2) not null,
  subtotal numeric(12,2) not null
);

create index idx_venta_items_venta on venta_items(venta_id);

-- ============================================
-- Trigger: updated_at automático en productos
-- ============================================
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger trg_productos_updated_at
before update on productos
for each row execute function set_updated_at();

-- ============================================
-- RLS: por ahora deshabilitado (uso individual, sin login)
-- El día de mañana que quieran multiusuario, se activa RLS
-- y se agregan policies por usuario.
-- ============================================
alter table productos disable row level security;
alter table config disable row level security;
alter table favoritos disable row level security;
alter table ventas disable row level security;
alter table venta_items disable row level security;
