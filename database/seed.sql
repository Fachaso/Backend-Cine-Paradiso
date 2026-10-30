-- ============================================================================
-- PROYECTO: Cine Paradiso (Hito 1 - TASK-03 / #11)
-- ARCHIVO: seed.sql
-- DESCRIPCIÓN: Script de carga de datos iniciales (semilla) para pruebas.
-- ============================================================================

USE cine_paradiso;

-- Deshabilitar temporalmente las comprobaciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 0;

-- Limpieza preventiva de datos previos
TRUNCATE TABLE cupos_servicios_funcion;
TRUNCATE TABLE servicios;
TRUNCATE TABLE inventario_sucursal;
TRUNCATE TABLE productos;
TRUNCATE TABLE usuarios;
TRUNCATE TABLE funciones;
TRUNCATE TABLE peliculas;
TRUNCATE TABLE asientos;
TRUNCATE TABLE salas;
TRUNCATE TABLE sucursales;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 1. SUCURSALES (3 Locales requeridos)
-- ============================================================================
INSERT INTO sucursales (id_sucursal, nombre, direccion, ciudad, estado) VALUES
(1, 'Cine Paradiso Central', 'Av. Corrientes 1234', 'CABA', 'ACTIVO'),
(2, 'Cine Paradiso Norte', 'Av. Cabildo 2450 (Belgrano)', 'CABA', 'ACTIVO'),
(3, 'Cine Paradiso Sur', 'Calle Mitre 890', 'Avellaneda', 'ACTIVO');

-- ============================================================================
-- 2. SALAS
-- ============================================================================
INSERT INTO salas (id_sala, id_sucursal, nombre, capacidad, estado) VALUES
(1, 1, 'Sala 1 - Splendid IMAX', 32, 'ACTIVO'),
(2, 1, 'Sala 2 - Royal Dolby', 24, 'ACTIVO'),
(3, 2, 'Sala 3 - Lumière 35mm', 32, 'ACTIVO'),
(4, 2, 'Sala 4 - Studio Vintage', 24, 'ACTIVO'),
(5, 3, 'Sala 5 - Classic Retro', 32, 'ACTIVO');

-- ============================================================================
-- 3. GRILLA MATRICIAL DE ASIENTOS (Filas A-D x Números 1-8 / 1-6)
-- ============================================================================

-- Sala 1 (32 Asientos)
INSERT INTO asientos (id_sala, fila, numero, tipo, estado) VALUES
(1, 'A', '1', 'NORMAL', 'ACTIVO'), (1, 'A', '2', 'NORMAL', 'ACTIVO'), (1, 'A', '3', 'NORMAL', 'ACTIVO'), (1, 'A', '4', 'NORMAL', 'ACTIVO'),
(1, 'A', '5', 'NORMAL', 'ACTIVO'), (1, 'A', '6', 'NORMAL', 'ACTIVO'), (1, 'A', '7', 'NORMAL', 'ACTIVO'), (1, 'A', '8', 'NORMAL', 'ACTIVO'),
(1, 'B', '1', 'NORMAL', 'ACTIVO'), (1, 'B', '2', 'NORMAL', 'ACTIVO'), (1, 'B', '3', 'NORMAL', 'ACTIVO'), (1, 'B', '4', 'NORMAL', 'ACTIVO'),
(1, 'B', '5', 'NORMAL', 'ACTIVO'), (1, 'B', '6', 'NORMAL', 'ACTIVO'), (1, 'B', '7', 'NORMAL', 'ACTIVO'), (1, 'B', '8', 'NORMAL', 'ACTIVO'),
(1, 'C', '1', 'NORMAL', 'ACTIVO'), (1, 'C', '2', 'NORMAL', 'ACTIVO'), (1, 'C', '3', 'VIP', 'ACTIVO'),    (1, 'C', '4', 'VIP', 'ACTIVO'),
(1, 'C', '5', 'VIP', 'ACTIVO'),    (1, 'C', '6', 'VIP', 'ACTIVO'),    (1, 'C', '7', 'NORMAL', 'ACTIVO'), (1, 'C', '8', 'NORMAL', 'ACTIVO'),
(1, 'D', '1', 'DISCAPACITADO', 'ACTIVO'), (1, 'D', '2', 'DISCAPACITADO', 'ACTIVO'), (1, 'D', '3', 'NORMAL', 'ACTIVO'), (1, 'D', '4', 'NORMAL', 'ACTIVO'),
(1, 'D', '5', 'NORMAL', 'ACTIVO'), (1, 'D', '6', 'NORMAL', 'ACTIVO'), (1, 'D', '7', 'NORMAL', 'ACTIVO'), (1, 'D', '8', 'NORMAL', 'ACTIVO');

-- Sala 2 (24 Asientos)
INSERT INTO asientos (id_sala, fila, numero, tipo, estado) VALUES
(2, 'A', '1', 'NORMAL', 'ACTIVO'), (2, 'A', '2', 'NORMAL', 'ACTIVO'), (2, 'A', '3', 'NORMAL', 'ACTIVO'), (2, 'A', '4', 'NORMAL', 'ACTIVO'), (2, 'A', '5', 'NORMAL', 'ACTIVO'), (2, 'A', '6', 'NORMAL', 'ACTIVO'), (2, 'A', '7', 'NORMAL', 'ACTIVO'), (2, 'A', '8', 'NORMAL', 'ACTIVO'),
(2, 'B', '1', 'NORMAL', 'ACTIVO'), (2, 'B', '2', 'NORMAL', 'ACTIVO'), (2, 'B', '3', 'VIP', 'ACTIVO'),    (2, 'B', '4', 'VIP', 'ACTIVO'),    (2, 'B', '5', 'VIP', 'ACTIVO'),    (2, 'B', '6', 'VIP', 'ACTIVO'),    (2, 'B', '7', 'NORMAL', 'ACTIVO'), (2, 'B', '8', 'NORMAL', 'ACTIVO'),
(2, 'C', '1', 'DISCAPACITADO', 'ACTIVO'), (2, 'C', '2', 'DISCAPACITADO', 'ACTIVO'), (2, 'C', '3', 'NORMAL', 'ACTIVO'), (2, 'C', '4', 'NORMAL', 'ACTIVO'), (2, 'C', '5', 'NORMAL', 'ACTIVO'), (2, 'C', '6', 'NORMAL', 'ACTIVO'), (2, 'C', '7', 'NORMAL', 'ACTIVO'), (2, 'C', '8', 'NORMAL', 'ACTIVO');

-- Sala 3 (32 Asientos)
INSERT INTO asientos (id_sala, fila, numero, tipo, estado) VALUES
(3, 'A', '1', 'NORMAL', 'ACTIVO'), (3, 'A', '2', 'NORMAL', 'ACTIVO'), (3, 'A', '3', 'NORMAL', 'ACTIVO'), (3, 'A', '4', 'NORMAL', 'ACTIVO'), (3, 'A', '5', 'NORMAL', 'ACTIVO'), (3, 'A', '6', 'NORMAL', 'ACTIVO'), (3, 'A', '7', 'NORMAL', 'ACTIVO'), (3, 'A', '8', 'NORMAL', 'ACTIVO'),
(3, 'B', '1', 'NORMAL', 'ACTIVO'), (3, 'B', '2', 'NORMAL', 'ACTIVO'), (3, 'B', '3', 'NORMAL', 'ACTIVO'), (3, 'B', '4', 'NORMAL', 'ACTIVO'), (3, 'B', '5', 'NORMAL', 'ACTIVO'), (3, 'B', '6', 'NORMAL', 'ACTIVO'), (3, 'B', '7', 'NORMAL', 'ACTIVO'), (3, 'B', '8', 'NORMAL', 'ACTIVO'),
(3, 'C', '1', 'NORMAL', 'ACTIVO'), (3, 'C', '2', 'NORMAL', 'ACTIVO'), (3, 'C', '3', 'VIP', 'ACTIVO'),    (3, 'C', '4', 'VIP', 'ACTIVO'),    (3, 'C', '5', 'VIP', 'ACTIVO'),    (3, 'C', '6', 'VIP', 'ACTIVO'),    (3, 'C', '7', 'NORMAL', 'ACTIVO'), (3, 'C', '8', 'NORMAL', 'ACTIVO'),
(3, 'D', '1', 'DISCAPACITADO', 'ACTIVO'), (3, 'D', '2', 'DISCAPACITADO', 'ACTIVO'), (3, 'D', '3', 'NORMAL', 'ACTIVO'), (3, 'D', '4', 'NORMAL', 'ACTIVO'), (3, 'D', '5', 'NORMAL', 'ACTIVO'), (3, 'D', '6', 'NORMAL', 'ACTIVO'), (3, 'D', '7', 'NORMAL', 'ACTIVO'), (3, 'D', '8', 'NORMAL', 'ACTIVO');

-- Sala 4 (24 Asientos)
INSERT INTO asientos (id_sala, fila, numero, tipo, estado) VALUES
(4, 'A', '1', 'NORMAL', 'ACTIVO'), (4, 'A', '2', 'NORMAL', 'ACTIVO'), (4, 'A', '3', 'NORMAL', 'ACTIVO'), (4, 'A', '4', 'NORMAL', 'ACTIVO'), (4, 'A', '5', 'NORMAL', 'ACTIVO'), (4, 'A', '6', 'NORMAL', 'ACTIVO'), (4, 'A', '7', 'NORMAL', 'ACTIVO'), (4, 'A', '8', 'NORMAL', 'ACTIVO'),
(4, 'B', '1', 'NORMAL', 'ACTIVO'), (4, 'B', '2', 'NORMAL', 'ACTIVO'), (4, 'B', '3', 'VIP', 'ACTIVO'),    (4, 'B', '4', 'VIP', 'ACTIVO'),    (4, 'B', '5', 'VIP', 'ACTIVO'),    (4, 'B', '6', 'VIP', 'ACTIVO'),    (4, 'B', '7', 'NORMAL', 'ACTIVO'), (4, 'B', '8', 'NORMAL', 'ACTIVO'),
(4, 'C', '1', 'DISCAPACITADO', 'ACTIVO'), (4, 'C', '2', 'DISCAPACITADO', 'ACTIVO'), (4, 'C', '3', 'NORMAL', 'ACTIVO'), (4, 'C', '4', 'NORMAL', 'ACTIVO'), (4, 'C', '5', 'NORMAL', 'ACTIVO'), (4, 'C', '6', 'NORMAL', 'ACTIVO'), (4, 'C', '7', 'NORMAL', 'ACTIVO'), (4, 'C', '8', 'NORMAL', 'ACTIVO');

-- Sala 5 (32 Asientos)
INSERT INTO asientos (id_sala, fila, numero, tipo, estado) VALUES
(5, 'A', '1', 'NORMAL', 'ACTIVO'), (5, 'A', '2', 'NORMAL', 'ACTIVO'), (5, 'A', '3', 'NORMAL', 'ACTIVO'), (5, 'A', '4', 'NORMAL', 'ACTIVO'), (5, 'A', '5', 'NORMAL', 'ACTIVO'), (5, 'A', '6', 'NORMAL', 'ACTIVO'), (5, 'A', '7', 'NORMAL', 'ACTIVO'), (5, 'A', '8', 'NORMAL', 'ACTIVO'),
(5, 'B', '1', 'NORMAL', 'ACTIVO'), (5, 'B', '2', 'NORMAL', 'ACTIVO'), (5, 'B', '3', 'NORMAL', 'ACTIVO'), (5, 'B', '4', 'NORMAL', 'ACTIVO'), (5, 'B', '5', 'NORMAL', 'ACTIVO'), (5, 'B', '6', 'NORMAL', 'ACTIVO'), (5, 'B', '7', 'NORMAL', 'ACTIVO'), (5, 'B', '8', 'NORMAL', 'ACTIVO'),
(5, 'C', '1', 'NORMAL', 'ACTIVO'), (5, 'C', '2', 'NORMAL', 'ACTIVO'), (5, 'C', '3', 'VIP', 'ACTIVO'),    (5, 'C', '4', 'VIP', 'ACTIVO'),    (5, 'C', '5', 'VIP', 'ACTIVO'),    (5, 'C', '6', 'VIP', 'ACTIVO'),    (5, 'C', '7', 'NORMAL', 'ACTIVO'), (5, 'C', '8', 'NORMAL', 'ACTIVO'),
(5, 'D', '1', 'DISCAPACITADO', 'ACTIVO'), (5, 'D', '2', 'DISCAPACITADO', 'ACTIVO'), (5, 'D', '3', 'NORMAL', 'ACTIVO'), (5, 'D', '4', 'NORMAL', 'ACTIVO'), (5, 'D', '5', 'NORMAL', 'ACTIVO'), (5, 'D', '6', 'NORMAL', 'ACTIVO'), (5, 'D', '7', 'NORMAL', 'ACTIVO'), (5, 'D', '8', 'NORMAL', 'ACTIVO');

-- ============================================================================
-- 4. PELÍCULAS CLÁSICAS / RETRO
-- ============================================================================
INSERT INTO peliculas (id_pelicula, titulo, sinopsis, poster_url, genero, duracion_min, clasificacion, estado) VALUES
(1, 'Cinema Paradiso (1988)', 'Un viaje nostálgico al corazón del cine en un pequeño pueblo siciliano. La inolvidable amistad entre Salvatore y Alfredo.', 'https://image.tmdb.org/t/p/w500/8A28E5d81b9YJ287391.jpg', 'Drama', 124, '+13', 'ACTIVO'),
(2, 'Casablanca (1942)', 'Durante la Segunda Guerra Mundial, el dueño de un club nocturno en Marruecos debe decidir entre su amor por una mujer o la causa aliada.', 'https://image.tmdb.org/t/p/w500/casablanca.jpg', 'Romance', 102, '+13', 'ACTIVO'),
(3, '2001: Odisea del Espacio (1968)', 'Una obra maestra de la ciencia ficción que explora la evolución humana y la inteligencia artificial a bordo de la Discovery One.', 'https://image.tmdb.org/t/p/w500/2001odyssey.jpg', 'Sci-Fi', 149, '+13', 'ACTIVO'),
(4, 'Taxi Driver (1976)', 'Un veterano de la guerra de Vietnam trabaja como taxista nocturno en Nueva York enfrentándose a la decadencia de la ciudad.', 'https://image.tmdb.org/t/p/w500/taxidriver.jpg', 'Drama', 114, '+16', 'ACTIVO'),
(5, 'El Padrino (1972)', 'El envejecido patriarca de una dinastía del crimen organizado trasfiere el control de su imperio clandestino a su hijo reacio.', 'https://image.tmdb.org/t/p/w500/godfather.jpg', 'Crimen', 175, '+18', 'ACTIVO'),
(6, 'Blade Runner (1982)', 'En un futuro distópico, un ex policía cazador de replicantes debe perseguir a un grupo de androides fugitivos en Los Ángeles.', 'https://image.tmdb.org/t/p/w500/bladerunner.jpg', 'Sci-Fi', 117, '+16', 'ACTIVO');

-- ============================================================================
-- 5. FUNCIONES HORARIAS PROGRAMADAS (DATETIME Unificado)
-- ============================================================================
INSERT INTO funciones (id_funcion, id_pelicula, id_sala, fecha_hora, precio_base, estado) VALUES
(1, 1, 1, '2026-10-26 18:00:00', 4500.00, 'PROGRAMADA'),
(2, 1, 1, '2026-10-26 21:00:00', 4800.00, 'PROGRAMADA'),
(3, 2, 2, '2026-10-26 19:30:00', 4200.00, 'PROGRAMADA'),
(4, 3, 3, '2026-10-27 20:00:00', 5000.00, 'PROGRAMADA'),
(5, 4, 4, '2026-10-27 22:15:00', 4500.00, 'PROGRAMADA'),
(6, 5, 5, '2026-10-28 19:00:00', 5200.00, 'PROGRAMADA');

-- ============================================================================
-- 6. USUARIOS Y ROLES (Password Hash de mock con bcrypt)
-- ============================================================================
INSERT INTO usuarios (id_usuario, nombre, email, password_hash, rol, id_sucursal, estado) VALUES
(1, 'Admin Paradiso', 'admin@cineparadiso.com', '$2b$12$K8yXW0lCgR8kF.vI4R4n1.gWqPZc0Qy9mP2hW5fH6zV.yU0t8rVbC', 'ADMIN', 1, 'ACTIVO'),
(2, 'Empleado Central', 'empleado.central@cineparadiso.com', '$2b$12$K8yXW0lCgR8kF.vI4R4n1.gWqPZc0Qy9mP2hW5fH6zV.yU0t8rVbC', 'EMPLEADO', 1, 'ACTIVO'),
(3, 'Empleado Norte', 'empleado.norte@cineparadiso.com', '$2b$12$K8yXW0lCgR8kF.vI4R4n1.gWqPZc0Qy9mP2hW5fH6zV.yU0t8rVbC', 'EMPLEADO', 2, 'ACTIVO'),
(4, 'Empleado Sur', 'empleado.sur@cineparadiso.com', '$2b$12$K8yXW0lCgR8kF.vI4R4n1.gWqPZc0Qy9mP2hW5fH6zV.yU0t8rVbC', 'EMPLEADO', 3, 'ACTIVO'),
(5, 'Martín Pérez', 'martin@example.com', '$2b$12$K8yXW0lCgR8kF.vI4R4n1.gWqPZc0Qy9mP2hW5fH6zV.yU0t8rVbC', 'CLIENTE', NULL, 'ACTIVO');

-- ============================================================================
-- 7. CATÁLOGO BASE DE SNACKS Y PRODUCTOS
-- ============================================================================
INSERT INTO productos (id_producto, nombre, descripcion, tipo, precio_base, estado) VALUES
(1, 'Combo Victoriano Popcorn', 'Pochoclos balde mediano + 1 Gaseosa 500ml', 'COMBO', 3500.00, 'ACTIVO'),
(2, 'Combo Imperial Real', 'Pochoclos balde grande + 2 Gaseosas grandes + Bombones', 'COMBO', 6200.00, 'ACTIVO'),
(3, 'Gaseosa 500ml', 'Línea Coca-Cola, Sprite o Fanta', 'BEBIDA', 1800.00, 'ACTIVO'),
(4, 'Balde Pochoclos XL', 'Pochoclos dulces o salados en balde coleccionable retro', 'COMIDA', 2900.00, 'ACTIVO'),
(5, 'Golosinas Vintage Pack', 'Selección de chocolates y confites clásicos de cine', 'COMIDA', 1500.00, 'ACTIVO');

-- ============================================================================
-- 8. INVENTARIO CENTRALIZADO POR SUCURSAL
-- ============================================================================
-- Sucursal 1 (Central)
INSERT INTO inventario_sucursal (id_sucursal, id_producto, stock_actual, stock_minimo) VALUES
(1, 1, 80, 15), (1, 2, 45, 10), (1, 3, 150, 30), (1, 4, 60, 10), (1, 5, 100, 20),
-- Sucursal 2 (Norte)
(2, 1, 60, 15), (2, 2, 30, 10), (2, 3, 120, 30), (2, 4, 40, 10), (2, 5, 80, 20),
-- Sucursal 3 (Sur)
(3, 1, 50, 15), (3, 2, 25, 10), (3, 3, 100, 30), (3, 4, 35, 10), (3, 5, 70, 20);

-- ============================================================================
-- 9. SERVICIOS ADICIONALES Y CUPOS POR FUNCIÓN
-- ============================================================================
INSERT INTO servicios (id_servicio, nombre, descripcion, tipo, precio_base, requiere_cupo, estado) VALUES
(1, 'Estacionamiento Reservado', 'Cochera fija techada dentro del predio del cine', 'ESTACIONAMIENTO', 2500.00, TRUE, 'ACTIVO'),
(2, 'Acceso VIP Lounge', 'Ingreso exclusivo a salón de espera privado con degustación', 'ACCESO_VIP', 3000.00, TRUE, 'ACTIVO'),
(3, 'Lentes 3D Retro', 'Lentes 3D coleccionables de edición especial', 'LENTES_3D', 1200.00, FALSE, 'ACTIVO');

-- Cupos asignados a la Función 1
INSERT INTO cupos_servicios_funcion (id_funcion, id_servicio, cupo_total, cupo_disponible, estado) VALUES
(1, 1, 20, 20, 'DISPONIBLE'),
(1, 2, 12, 12, 'DISPONIBLE'),
-- Cupos asignados a la Función 2
(2, 1, 20, 20, 'DISPONIBLE'),
(2, 2, 12, 12, 'DISPONIBLE');
