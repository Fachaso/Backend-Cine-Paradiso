DROP DATABASE IF EXISTS cine_paradiso;
CREATE DATABASE cine_paradiso;
USE cine_paradiso;

-- 1. Sucursales (Cine Paradiso)
CREATE TABLE sucursales (
    id_sucursal INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100) NOT NULL
);

-- 2. Salas por sucursal
CREATE TABLE salas (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    id_sucursal INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    capacidad INT NOT NULL,
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal) ON DELETE CASCADE
);

-- 3. Asientos / Butacas de cada sala
CREATE TABLE asientos (
    id_asiento INT AUTO_INCREMENT PRIMARY KEY,
    id_sala INT NOT NULL,
    fila VARCHAR(5) NOT NULL,
    numero INT NOT NULL,
    FOREIGN KEY (id_sala) REFERENCES salas(id_sala) ON DELETE CASCADE,
    CONSTRAINT uq_asiento_sala UNIQUE (id_sala, fila, numero)
);

-- 4. Películas (Cargadas exclusivamente desde OMDb / TMDb vía Backend)
CREATE TABLE peliculas (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    sinopsis TEXT,
    poster_url VARCHAR(255),
    genero VARCHAR(50) NOT NULL,
    duracion_min INT NOT NULL,
    clasificacion VARCHAR(20) NOT NULL
);

-- 5. Funciones
CREATE TABLE funciones (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    id_pelicula INT NOT NULL,
    id_sala INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    precio_entrada DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_sala) REFERENCES salas(id_sala) ON DELETE CASCADE
);

-- 6. Usuarios y Roles (ADMIN y CLIENTE)
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('CLIENTE', 'ADMIN') NOT NULL DEFAULT 'CLIENTE'
);

-- 7. Compras
CREATE TABLE compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_compra DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto_total DECIMAL(10,2) NOT NULL,
    codigo_qr VARCHAR(100) NOT NULL UNIQUE,
    estado_qr ENUM('PENDIENTE', 'USADO', 'CANCELADO') NOT NULL DEFAULT 'PENDIENTE',
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- 8. Entradas (Relación entre Compra, Función y Asiento)
-- Nota: Si una compra se cancela (estado_qr = CANCELADO), se eliminan sus filas en 'entradas' para liberar las butacas.
CREATE TABLE entradas (
    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_funcion INT NOT NULL,
    id_asiento INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
    FOREIGN KEY (id_funcion) REFERENCES funciones(id_funcion) ON DELETE CASCADE,
    FOREIGN KEY (id_asiento) REFERENCES asientos(id_asiento) ON DELETE CASCADE,
    CONSTRAINT uq_funcion_asiento UNIQUE (id_funcion, id_asiento)
);

-- 9. Servicios (Comida, Bebidas, Combos, Estacionamiento, Acceso VIP)
CREATE TABLE servicios (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    tipo ENUM('COMIDA', 'BEBIDA', 'COMBO', 'ESTACIONAMIENTO', 'VIP', 'OTRO') NOT NULL,
    precio DECIMAL(10,2) NOT NULL
);

-- 10. Detalle de servicios agregados a una compra
CREATE TABLE detalle_compra_servicios (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_servicio INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio) ON DELETE CASCADE
);

-- 11. Reseñas (Requerimiento deseable/opcional)
CREATE TABLE resenas (
    id_resena INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_pelicula INT NOT NULL,
    puntuacion TINYINT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
    comentario TEXT,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE,
    CONSTRAINT uq_usuario_pelicula UNIQUE (id_usuario, id_pelicula)
);