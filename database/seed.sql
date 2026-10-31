USE cine_paradiso;

-- 1. Sucursales de Cine Paradiso
INSERT INTO sucursales (id_sucursal, nombre, direccion, ciudad) VALUES
(1, 'Cine Paradiso Central', 'Av. Corrientes 1234', 'CABA'),
(2, 'Cine Paradiso Norte', 'Av. Santa Fe 4567', 'CABA'),
(3, 'Cine Paradiso Sur', 'Calle Mitre 890', 'Avellaneda');

-- 2. Salas por sucursal
INSERT INTO salas (id_sala, id_sucursal, nombre, capacidad) VALUES
(1, 1, 'Sala 1', 30),
(2, 1, 'Sala 2', 20),
(3, 2, 'Sala 1 Norte', 20);

-- 3. Asientos de cada sala (Coinciden con la capacidad de cada sala)
-- Sala 1 (30 asientos: Filas A, B y C de 10 butacas cada una)
INSERT INTO asientos (id_sala, fila, numero) VALUES
(1, 'A', 1), (1, 'A', 2), (1, 'A', 3), (1, 'A', 4), (1, 'A', 5), (1, 'A', 6), (1, 'A', 7), (1, 'A', 8), (1, 'A', 9), (1, 'A', 10),
(1, 'B', 1), (1, 'B', 2), (1, 'B', 3), (1, 'B', 4), (1, 'B', 5), (1, 'B', 6), (1, 'B', 7), (1, 'B', 8), (1, 'B', 9), (1, 'B', 10),
(1, 'C', 1), (1, 'C', 2), (1, 'C', 3), (1, 'C', 4), (1, 'C', 5), (1, 'C', 6), (1, 'C', 7), (1, 'C', 8), (1, 'C', 9), (1, 'C', 10);

-- Sala 2 (20 asientos: Filas A y B de 10 butacas cada una)
INSERT INTO asientos (id_sala, fila, numero) VALUES
(2, 'A', 1), (2, 'A', 2), (2, 'A', 3), (2, 'A', 4), (2, 'A', 5), (2, 'A', 6), (2, 'A', 7), (2, 'A', 8), (2, 'A', 9), (2, 'A', 10),
(2, 'B', 1), (2, 'B', 2), (2, 'B', 3), (2, 'B', 4), (2, 'B', 5), (2, 'B', 6), (2, 'B', 7), (2, 'B', 8), (2, 'B', 9), (2, 'B', 10);

-- Sala 3 (20 asientos: Filas A y B de 10 butacas cada una)
INSERT INTO asientos (id_sala, fila, numero) VALUES
(3, 'A', 1), (3, 'A', 2), (3, 'A', 3), (3, 'A', 4), (3, 'A', 5), (3, 'A', 6), (3, 'A', 7), (3, 'A', 8), (3, 'A', 9), (3, 'A', 10),
(3, 'B', 1), (3, 'B', 2), (3, 'B', 3), (3, 'B', 4), (3, 'B', 5), (3, 'B', 6), (3, 'B', 7), (3, 'B', 8), (3, 'B', 9), (3, 'B', 10);

-- 4. Usuarios iniciales (Roles ADMIN y CLIENTE)
INSERT INTO usuarios (id_usuario, nombre, email, password_hash, rol) VALUES
(1, 'Administrador', 'admin@cineparadiso.com', 'hash_admin_123', 'ADMIN'),
(2, 'Cliente Ejemplo', 'cliente@gmail.com', 'hash_cliente_123', 'CLIENTE');

-- 5. Catálogo de servicios adicionales (Comida, Bebida, Combos, Estacionamiento, VIP)
INSERT INTO servicios (id_servicio, nombre, descripcion, tipo, precio) VALUES
(1, 'Combo Popcorn + Gaseosa', 'Balde grande de pochoclos y gaseosa 500ml', 'COMBO', 3500.00),
(2, 'Pochoclos Medianos', 'Balde mediano de pochoclos dulces', 'COMIDA', 2200.00),
(3, 'Gaseosa Grande 750ml', 'Vaso de gaseosa línea Coca-Cola 750ml', 'BEBIDA', 1800.00),
(4, 'Estacionamiento', 'Estacionamiento cubierto por 3 horas', 'ESTACIONAMIENTO', 2000.00),
(5, 'Pase VIP Lounge', 'Acceso a la sala de espera VIP antes de la función', 'VIP', 1500.00);