-- ============================================
-- Datos de PRUEBA para arrancar (no son tu inventario real)
-- Ejecutar DESPUÉS de schema.sql
-- ============================================

insert into productos (nombre, categoria, marca, precio_costo, precio_venta, stock, codigo_barras) values
('Coca Cola 2.25L', 'Bebidas', 'Coca Cola', 1800, 2500, 40, '7790895000012'),
('Cerveza Quilmes 1L', 'Bebidas', 'Quilmes', 1500, 2100, 30, '7790895000029'),
('Leche La Serenísima 1L', 'Lácteos', 'La Serenísima', 900, 1300, 50, '7790895000036'),
('Yogur Ser Frutilla', 'Lácteos', 'La Serenísima', 700, 1000, 25, '7790895000043'),
('Alfajor Arcor Triple', 'Almacén', 'Arcor', 300, 500, 60, '7790895000050'),
('Fideos Matarazzo 500g', 'Almacén', 'Matarazzo', 600, 900, 45, '7790895000067'),
('Detergente Magistral', 'Limpieza', 'Magistral', 1200, 1800, 20, '7790895000074'),
('Lavandina Ayudín 1L', 'Limpieza', 'Ayudín', 800, 1200, 35, '7790895000081'),
('Pañales Pampers G x30', 'Bebés', 'Pampers', 4500, 6200, 15, '7790895000098'),
('Ibuprofeno 400mg x10', 'Farmacia', 'Genérico', 900, 1400, 22, '7790895000104'),
('Pan Lactal Bimbo', 'Almacén', 'Bimbo', 1000, 1500, 18, '7790895000111'),
('Yerba Rosamonte 1kg', 'Almacén', 'Rosamonte', 2200, 3100, 28, '7790895000128');

-- Cargamos 2 favoritos de ejemplo (F1 y F2)
update favoritos set producto_id = (select id from productos where nombre = 'Coca Cola 2.25L') where slot = 1;
update favoritos set producto_id = (select id from productos where nombre = 'Alfajor Arcor Triple') where slot = 2;
