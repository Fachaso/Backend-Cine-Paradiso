-- ============================================================================
-- PROYECTO: Cine Paradiso (Hito 1 - Punto B)
-- CÁTEDRA: Introducción al Desarrollo de Software (Lanzillotta - FIUBA)
-- MOTOR: MySQL 8.0+ (InnoDB, UTF8mb4)
-- DESCRIPCIÓN: Script DDL completo con 26 tablas, claves foráneas, restricciones
--              de unicidad, índices optimizados y soporte para compra de entradas,
--              bloqueo temporal de 5 min, pedidos independientes de Candy Bar,
--              doble tipo de QR (Sala y Candy) y auditoría física de inventario.
-- ============================================================================

DROP DATABASE IF EXISTS cine_paradiso;
CREATE DATABASE cine_paradiso CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cine_paradiso;

-- Deshabilitar chequeo de foreign keys durante la creación de tablas
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- MÓDULO 1: CINE Y CARTELERA
-- ============================================================================

-- 1. Sucursales físicas del complejo
CREATE TABLE sucursales (
    id_sucursal INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Salas pertenecientes a una sucursal
CREATE TABLE salas (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    id_sucursal INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    capacidad INT NOT NULL,
    estado ENUM('ACTIVO', 'INACTIVO', 'MANTENIMIENTO') NOT NULL DEFAULT 'ACTIVO',
    CONSTRAINT fk_salas_sucursal FOREIGN KEY (id_sucursal) 
        REFERENCES sucursales(id_sucursal) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_sala_sucursal UNIQUE (id_sucursal, nombre)
) ENGINE=InnoDB;

-- 3. Butacas físicas de cada sala (disposición matricial fila-número)
CREATE TABLE asientos (
    id_asiento INT AUTO_INCREMENT PRIMARY KEY,
    id_sala INT NOT NULL,
    fila VARCHAR(10) NOT NULL,
    numero VARCHAR(10) NOT NULL,
    tipo ENUM('NORMAL', 'VIP', 'DISCAPACITADO') NOT NULL DEFAULT 'NORMAL',
    estado ENUM('ACTIVO', 'INACTIVO', 'DAÑADO') NOT NULL DEFAULT 'ACTIVO',
    CONSTRAINT fk_asientos_sala FOREIGN KEY (id_sala) 
        REFERENCES salas(id_sala) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_asiento_sala UNIQUE (id_sala, fila, numero)
) ENGINE=InnoDB;

-- 4. Películas registradas localmente (importadas de TMDb / OMDb)
CREATE TABLE peliculas (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    sinopsis TEXT,
    poster_url VARCHAR(255),
    genero VARCHAR(50) NOT NULL,
    duracion_min INT NOT NULL,
    clasificacion VARCHAR(20) NOT NULL,
    estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 5. Funciones horarias programadas
CREATE TABLE funciones (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    id_pelicula INT NOT NULL,
    id_sala INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    precio_base DECIMAL(10,2) NOT NULL,
    estado ENUM('PROGRAMADA', 'EN_CURSO', 'FINALIZADA', 'CANCELADA') NOT NULL DEFAULT 'PROGRAMADA',
    CONSTRAINT fk_funciones_pelicula FOREIGN KEY (id_pelicula) 
        REFERENCES peliculas(id_pelicula) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_funciones_sala FOREIGN KEY (id_sala) 
        REFERENCES salas(id_sala) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_funciones_fecha_sala (id_sala, fecha_hora)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 2: USUARIOS Y PERFILES
-- ============================================================================

-- 6. Usuarios del sistema (Clientes, Empleados y Administradores)
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('CLIENTE', 'EMPLEADO', 'ADMIN') NOT NULL DEFAULT 'CLIENTE',
    id_sucursal INT NULL, -- Asignada a empleados para limitar operaciones a su local
    estado ENUM('ACTIVO', 'INACTIVO', 'BLOQUEADO') NOT NULL DEFAULT 'ACTIVO',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_sucursal FOREIGN KEY (id_sucursal) 
        REFERENCES sucursales(id_sucursal) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 3: BLOQUEOS TEMPORALES (5 MINUTOS)
-- ============================================================================

-- 7. Reservas temporales durante el proceso de selección y pago de butacas
CREATE TABLE bloqueos_asientos (
    id_bloqueo INT AUTO_INCREMENT PRIMARY KEY,
    id_funcion INT NOT NULL,
    id_asiento INT NOT NULL,
    id_orden INT NULL, -- Vinculado cuando se crea la orden en estado PENDIENTE
    id_usuario INT NOT NULL,
    fecha_bloqueo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME NOT NULL,
    estado ENUM('ACTIVO', 'CONFIRMADO', 'CANCELADO', 'EXPIRADO') NOT NULL DEFAULT 'ACTIVO',
    CONSTRAINT fk_bloqueos_funcion FOREIGN KEY (id_funcion) 
        REFERENCES funciones(id_funcion) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_bloqueos_asiento FOREIGN KEY (id_asiento) 
        REFERENCES asientos(id_asiento) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_bloqueos_usuario FOREIGN KEY (id_usuario) 
        REFERENCES usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_bloqueo_consulta (id_funcion, id_asiento, estado, fecha_expiracion)
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 4: ÓRDENES, ENTRADAS Y CÓDIGOS QR
-- ============================================================================

-- 8. Órdenes de compra (Tanto de Cine como de Candy Bar Independiente)
CREATE TABLE ordenes (
    id_orden INT AUTO_INCREMENT PRIMARY KEY,
    tipo_orden ENUM('CINE', 'CANDYBAR_EXPRESS') NOT NULL DEFAULT 'CINE',
    id_usuario INT NOT NULL, -- Cliente titular de la orden
    id_empleado_operador INT NULL, -- Registrado si la compra fue asistida en boletería
    id_funcion INT NULL, -- NULL si es un pedido de Candy Bar independiente
    id_sucursal_retiro INT NOT NULL, -- Sucursal donde se asiste a la función o se retiran snacks
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_confirmacion DATETIME NULL,
    fecha_cancelacion DATETIME NULL,
    vencimiento_bloqueo DATETIME NOT NULL, -- Vencimiento de los 5 minutos para pagar
    estado ENUM(
        'PENDIENTE',           -- En proceso de pago (cine)
        'CONFIRMADA',          -- Pagada con éxito
        'CANCELADA',           -- Cancelada antes de 60 min
        'EXPIRADA',            -- Excedió los 5 min sin pagar
        'PENDIENTE_RETIRO',    -- Pagada, esperando entrega en Candy Bar
        'ENTREGADO',           -- Snacks entregados físicamente
        'NO_RETIRADO'          -- No retirado antes de la 01:00 AM (sin reembolso)
    ) NOT NULL DEFAULT 'PENDIENTE',
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    referencia_pago VARCHAR(100) NULL,
    CONSTRAINT fk_ordenes_usuario FOREIGN KEY (id_usuario) 
        REFERENCES usuarios(id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_ordenes_operador FOREIGN KEY (id_empleado_operador) 
        REFERENCES usuarios(id_usuario) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_ordenes_funcion FOREIGN KEY (id_funcion) 
        REFERENCES funciones(id_funcion) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_ordenes_sucursal FOREIGN KEY (id_sucursal_retiro) 
        REFERENCES sucursales(id_sucursal) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Clave foránea diferida de bloqueos_asientos hacia ordenes
ALTER TABLE bloqueos_asientos 
    ADD CONSTRAINT fk_bloqueos_orden FOREIGN KEY (id_orden) 
        REFERENCES ordenes(id_orden) ON DELETE SET NULL ON UPDATE CASCADE;

-- 9. Entradas individuales emitidas por butaca dentro de una orden de cine
CREATE TABLE entradas (
    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    id_funcion INT NOT NULL,
    id_asiento INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    estado ENUM('ACTIVA', 'UTILIZADA', 'CANCELADA', 'REASIGNADA') NOT NULL DEFAULT 'ACTIVA',
    fecha_uso DATETIME NULL,
    CONSTRAINT fk_entradas_orden FOREIGN KEY (id_orden) 
        REFERENCES ordenes(id_orden) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_entradas_funcion FOREIGN KEY (id_funcion) 
        REFERENCES funciones(id_funcion) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_entradas_asiento FOREIGN KEY (id_asiento) 
        REFERENCES asientos(id_asiento) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_funcion_asiento_activa UNIQUE (id_funcion, id_asiento)
) ENGINE=InnoDB;

-- 10. Códigos QR unificados (Soporta QR de Acceso a Sala y QR de Retiro de Snacks)
CREATE TABLE codigos_qr (
    id_qr INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL UNIQUE,
    codigo VARCHAR(100) NOT NULL UNIQUE,
    tipo ENUM('ACCESO_SALA', 'RETIRO_CANDYBAR') NOT NULL DEFAULT 'ACCESO_SALA',
    fecha_generacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_validacion DATETIME NULL,
    estado ENUM('ACTIVO', 'UTILIZADO', 'INVALIDO') NOT NULL DEFAULT 'ACTIVO',
    CONSTRAINT fk_qr_orden FOREIGN KEY (id_orden) 
        REFERENCES ordenes(id_orden) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 5: PRODUCTOS (SNACKS), INVENTARIO Y COTIZACIÓN
-- ============================================================================

-- 11. Catálogo general de productos
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    tipo ENUM('COMIDA', 'BEBIDA', 'COMBO', 'MERCHANDISING') NOT NULL DEFAULT 'COMBO',
    precio_base DECIMAL(10,2) NOT NULL,
    estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO'
) ENGINE=InnoDB;

-- 12. Existencias e inventario centralizado por sucursal
CREATE TABLE inventario_sucursal (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    id_sucursal INT NOT NULL,
    id_producto INT NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 10,
    CONSTRAINT fk_inv_sucursal FOREIGN KEY (id_sucursal) 
        REFERENCES sucursales(id_sucursal) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_inv_producto FOREIGN KEY (id_producto) 
        REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_sucursal_producto UNIQUE (id_sucursal, id_producto)
) ENGINE=InnoDB;

-- 13. Congelamiento histórico de precios al iniciar la orden o al agregar nuevos ítems
CREATE TABLE cotizacion_productos (
    id_cotizacion INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    id_producto INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    fecha_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME NOT NULL,
    CONSTRAINT fk_cotiz_orden FOREIGN KEY (id_orden) 
        REFERENCES ordenes(id_orden) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cotiz_producto FOREIGN KEY (id_producto) 
        REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_cotizacion_orden_producto UNIQUE (id_orden, id_producto)
) ENGINE=InnoDB;

-- 14. Detalle de productos seleccionados o confirmados en una orden
CREATE TABLE detalle_orden_productos (
    id_detalle_prod INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    estado ENUM('PENDIENTE', 'ENTREGADO', 'CANCELADO', 'NO_RETIRADO') NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT fk_det_prod_orden FOREIGN KEY (id_orden) 
        REFERENCES ordenes(id_orden) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_det_prod_producto FOREIGN KEY (id_producto) 
        REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 15. Auditoría de entrega física en mostrador Candy Bar
CREATE TABLE entregas_productos (
    id_entrega INT AUTO_INCREMENT PRIMARY KEY,
    id_detalle_prod INT NOT NULL,
    id_empleado INT NOT NULL,
    cantidad_entregada INT NOT NULL,
    fecha_entrega DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_entrega_detalle FOREIGN KEY (id_detalle_prod) 
        REFERENCES detalle_orden_productos(id_detalle_prod) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_entrega_empleado FOREIGN KEY (id_empleado) 
        REFERENCES usuarios(id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 6: AUDITORÍA DE REVISIÓN FÍSICA DE INVENTARIO (ENDPOINT 25)
-- ============================================================================

-- 16. Cabecera de revisión física de pedidos NO_RETIRADOS (Inspección única y definitiva)
CREATE TABLE revisiones_inventario (
    id_revision INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL UNIQUE, -- Una orden no retirable solo se revisa una única vez
    id_empleado INT NOT NULL, -- Empleado de la sucursal o Admin que ejecuta la auditoría
    fecha_revision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observacion TEXT NOT NULL,
    CONSTRAINT fk_rev_orden FOREIGN KEY (id_orden) 
        REFERENCES ordenes(id_orden) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_rev_empleado FOREIGN KEY (id_empleado) 
        REFERENCES usuarios(id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 17. Detalle de unidades declaradas recuperables vs descarte
CREATE TABLE detalle_revision_inventario (
    id_detalle_rev INT AUTO_INCREMENT PRIMARY KEY,
    id_revision INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad_recuperable INT NOT NULL, -- Unidades aptas que se reincorporan al stock
    CONSTRAINT fk_detrev_revision FOREIGN KEY (id_revision) 
        REFERENCES revisiones_inventario(id_revision) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detrev_producto FOREIGN KEY (id_producto) 
        REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 7: SERVICIOS ADICIONALES (PARKING, VIP)
-- ============================================================================

-- 18. Catálogo de servicios adicionales
CREATE TABLE servicios (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    tipo ENUM('ESTACIONAMIENTO', 'ACCESO_VIP', 'LENTES_3D', 'OTRO') NOT NULL,
    precio_base DECIMAL(10,2) NOT NULL,
    requiere_cupo BOOLEAN NOT NULL DEFAULT TRUE,
    estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO'
) ENGINE=InnoDB;

-- 19. Cupos de servicios limitados por función
CREATE TABLE cupos_servicios_funcion (
    id_cupo INT AUTO_INCREMENT PRIMARY KEY,
    id_funcion INT NOT NULL,
    id_servicio INT NOT NULL,
    cupo_total INT NOT NULL,
    cupo_disponible INT NOT NULL,
    estado ENUM('DISPONIBLE', 'AGOTADO') NOT NULL DEFAULT 'DISPONIBLE',
    CONSTRAINT fk_cupos_funcion FOREIGN KEY (id_funcion) 
        REFERENCES funciones(id_funcion) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cupos_servicio FOREIGN KEY (id_servicio) 
        REFERENCES servicios(id_servicio) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_funcion_servicio UNIQUE (id_funcion, id_servicio)
) ENGINE=InnoDB;

-- 20. Detalle de servicios contratados en una orden
CREATE TABLE detalle_orden_servicios (
    id_detalle_serv INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    id_servicio INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    estado ENUM('PENDIENTE', 'UTILIZADO', 'CANCELADO') NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT fk_det_serv_orden FOREIGN KEY (id_orden) 
        REFERENCES ordenes(id_orden) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_det_serv_servicio FOREIGN KEY (id_servicio) 
        REFERENCES servicios(id_servicio) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 21. Registro de validación y uso físico de servicios
CREATE TABLE usos_servicios (
    id_uso INT AUTO_INCREMENT PRIMARY KEY,
    id_detalle_serv INT NOT NULL,
    id_empleado INT NOT NULL,
    cantidad_utilizada INT NOT NULL,
    fecha_uso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usos_detalle FOREIGN KEY (id_detalle_serv) 
        REFERENCES detalle_orden_servicios(id_detalle_serv) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_usos_empleado FOREIGN KEY (id_empleado) 
        REFERENCES usuarios(id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- MÓDULO 8: INCIDENCIAS, CANCELACIONES Y REINTEGROS
-- ============================================================================

-- 22. Auditoría de incidencias técnicas en sala o butaca
CREATE TABLE incidencias (
    id_incidencia INT AUTO_INCREMENT PRIMARY KEY,
    id_funcion INT NOT NULL,
    id_asiento INT NULL,
    id_usuario INT NOT NULL, -- Empleado que reporta o cliente afectado
    tipo ENUM('BUTACA_ROTA', 'SONIDO_IMAGEN', 'PROBLEMA_CLIMA', 'OTRO') NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('ABIERTA', 'RESUELTA', 'DESCARTADA') NOT NULL DEFAULT 'ABIERTA',
    CONSTRAINT fk_inc_funcion FOREIGN KEY (id_funcion) 
        REFERENCES funciones(id_funcion) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_inc_asiento FOREIGN KEY (id_asiento) 
        REFERENCES asientos(id_asiento) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_inc_usuario FOREIGN KEY (id_usuario) 
        REFERENCES usuarios(id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 23. Reasignaciones de asientos para clientes afectados por incidencias
CREATE TABLE reasignaciones_entradas (
    id_reasignacion INT AUTO_INCREMENT PRIMARY KEY,
    id_entrada INT NOT NULL,
    id_incidencia INT NOT NULL,
    id_asiento_anterior INT NOT NULL,
    id_asiento_nuevo INT NOT NULL,
    id_usuario INT NOT NULL, -- Empleado administrador que autoriza el cambio
    motivo VARCHAR(255) NOT NULL,
    fecha_reasignacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reasig_entrada FOREIGN KEY (id_entrada) 
        REFERENCES entradas(id_entrada) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reasig_incidencia FOREIGN KEY (id_incidencia) 
        REFERENCES incidencias(id_incidencia) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reasig_asiento_ant FOREIGN KEY (id_asiento_anterior) 
        REFERENCES asientos(id_asiento) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reasig_asiento_nue FOREIGN KEY (id_asiento_nuevo) 
        REFERENCES asientos(id_asiento) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reasig_usuario FOREIGN KEY (id_usuario) 
        REFERENCES usuarios(id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 24. Solicitudes y registros de cancelación de órdenes (Hasta 60 min antes)
CREATE TABLE cancelaciones (
    id_cancelacion INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL UNIQUE,
    id_usuario INT NOT NULL,
    tipo ENUM('CLIENTE_AUTOGESTION', 'ADMIN_EXCEPCION', 'FUERZA_MAYOR') NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    fecha_cancelacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('SOLICITADA', 'PROCESADA', 'RECHAZADA') NOT NULL DEFAULT 'PROCESADA',
    CONSTRAINT fk_canc_orden FOREIGN KEY (id_orden) 
        REFERENCES ordenes(id_orden) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_canc_usuario FOREIGN KEY (id_usuario) 
        REFERENCES usuarios(id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 25. Comprobantes de reintegro simulado
CREATE TABLE reintegros (
    id_reintegro INT AUTO_INCREMENT PRIMARY KEY,
    id_cancelacion INT NOT NULL UNIQUE,
    importe DECIMAL(10,2) NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    estado ENUM('PENDIENTE', 'REINTEGRADO', 'FALLIDO') NOT NULL DEFAULT 'REINTEGRADO',
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_procesamiento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reint_cancelacion FOREIGN KEY (id_cancelacion) 
        REFERENCES cancelaciones(id_cancelacion) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 26. Desglose detallado de los conceptos reintegrados
CREATE TABLE conceptos_reintegro (
    id_concepto INT AUTO_INCREMENT PRIMARY KEY,
    id_reintegro INT NOT NULL,
    tipo_concepto ENUM('ENTRADA', 'PRODUCTO', 'SERVICIO') NOT NULL,
    id_referencia INT NOT NULL,
    cantidad INT NOT NULL,
    importe_unitario DECIMAL(10,2) NOT NULL,
    importe_total DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_conc_reintegro FOREIGN KEY (id_reintegro) 
        REFERENCES reintegros(id_reintegro) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Habilitar nuevamente chequeo de foreign keys
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- MÓDULO 9: RESEÑAS Y PUNTUACIONES (DESEABLE)
-- ============================================================================

CREATE TABLE reseñas (
    id_reseña INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_pelicula INT NOT NULL,
    id_funcion INT NOT NULL,
    puntuacion TINYINT CHECK (puntuacion BETWEEN 1 AND 5),
    comentario TEXT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reseña_usuario FOREIGN KEY (id_usuario) 
        REFERENCES usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_reseña_pelicula FOREIGN KEY (id_pelicula) 
        REFERENCES peliculas(id_pelicula) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reseña_funcion FOREIGN KEY (id_funcion) 
        REFERENCES funciones(id_funcion) ON DELETE RESTRICT ON UPDATE CASCADE,
    -- Garantiza que solo se pueda opinar una vez por función asistida
    CONSTRAINT uq_usuario_funcion_reseña UNIQUE (id_usuario, id_funcion)
) ENGINE=InnoDB;

-- ============================================================================
-- SEED DATA (DATOS INICIALES PARA PRUEBAS Y VALIDACIÓN DE HITO 1)
-- ============================================================================

-- Sucursales
INSERT INTO sucursales (id_sucursal, nombre, direccion, ciudad, estado) VALUES
(1, 'Cine Paradiso Central', 'Av. Corrientes 1234', 'CABA', 'ACTIVO'),
(2, 'Cine Paradiso Norte', 'Av. Santa Fe 4567', 'CABA', 'ACTIVO'),
(3, 'Cine Paradiso Sur', 'Calle Mitre 890', 'Avellaneda', 'ACTIVO');

-- Salas (Sucursal 1)
INSERT INTO salas (id_sala, id_sucursal, nombre, capacidad, estado) VALUES
(1, 1, 'Sala 1 - Victorian IMAX', 32, 'ACTIVO'),
(2, 1, 'Sala 2 - Royal 3D', 24, 'ACTIVO');

-- Asientos para Sala 1 (Matriz de 4 filas x 8 columnas = 32 asientos)
INSERT INTO asientos (id_sala, fila, numero, tipo, estado) VALUES
(1, 'A', '1', 'NORMAL', 'ACTIVO'), (1, 'A', '2', 'NORMAL', 'ACTIVO'), (1, 'A', '3', 'NORMAL', 'ACTIVO'), (1, 'A', '4', 'NORMAL', 'ACTIVO'),
(1, 'A', '5', 'NORMAL', 'ACTIVO'), (1, 'A', '6', 'NORMAL', 'ACTIVO'), (1, 'A', '7', 'NORMAL', 'ACTIVO'), (1, 'A', '8', 'NORMAL', 'ACTIVO'),
(1, 'B', '1', 'NORMAL', 'ACTIVO'), (1, 'B', '2', 'NORMAL', 'ACTIVO'), (1, 'B', '3', 'NORMAL', 'ACTIVO'), (1, 'B', '4', 'NORMAL', 'ACTIVO'),
(1, 'B', '5', 'NORMAL', 'ACTIVO'), (1, 'B', '6', 'NORMAL', 'ACTIVO'), (1, 'B', '7', 'NORMAL', 'ACTIVO'), (1, 'B', '8', 'NORMAL', 'ACTIVO'),
(1, 'C', '1', 'NORMAL', 'ACTIVO'), (1, 'C', '2', 'NORMAL', 'ACTIVO'), (1, 'C', '3', 'VIP', 'ACTIVO'),    (1, 'C', '4', 'VIP', 'ACTIVO'),
(1, 'C', '5', 'VIP', 'ACTIVO'),    (1, 'C', '6', 'VIP', 'ACTIVO'),    (1, 'C', '7', 'NORMAL', 'ACTIVO'), (1, 'C', '8', 'NORMAL', 'ACTIVO'),
(1, 'D', '1', 'DISCAPACITADO', 'ACTIVO'), (1, 'D', '2', 'DISCAPACITADO', 'ACTIVO'), (1, 'D', '3', 'NORMAL', 'ACTIVO'), (1, 'D', '4', 'NORMAL', 'ACTIVO'),
(1, 'D', '5', 'NORMAL', 'ACTIVO'), (1, 'D', '6', 'NORMAL', 'ACTIVO'), (1, 'D', '7', 'NORMAL', 'ACTIVO'), (1, 'D', '8', 'NORMAL', 'ACTIVO');

-- Películas de prueba
INSERT INTO peliculas (id_pelicula, titulo, sinopsis, poster_url, genero, duracion_min, clasificacion, estado) VALUES
(1, 'Gladiator II', 'Años después de presenciar la muerte del héroe Máximo, Lucio debe entrar al Coliseo.', 'https://image.tmdb.org/t/p/w500/gladiator2.jpg', 'Acción', 148, '+16', 'ACTIVO'),
(2, 'Indiana Jones and the Dial of Destiny', 'El arqueólogo emprende otra aventura contra el tiempo.', 'https://image.tmdb.org/t/p/w500/indy5.jpg', 'Aventura', 154, '+13', 'ACTIVO');

-- Función de prueba
INSERT INTO funciones (id_funcion, id_pelicula, id_sala, fecha_hora, precio_base, estado) VALUES
(1, 1, 1, '2026-10-26 20:00:00', 4500.00, 'PROGRAMADA');

-- Usuarios (Roles: CLIENTE, EMPLEADO, ADMIN con password de mock con hash bcrypt)
INSERT INTO usuarios (id_usuario, nombre, email, password_hash, rol, id_sucursal, estado) VALUES
(1, 'Administrador General', 'admin@cineparadiso.com', '$2b$12$K8yXW0lCgR8kF.vI4R4n1.gWqPZc0Qy9mP2hW5fH6zV.yU0t8rVbC', 'ADMIN', 1, 'ACTIVO'),
(2, 'Empleado Mostrador', 'empleado@cineparadiso.com', '$2b$12$K8yXW0lCgR8kF.vI4R4n1.gWqPZc0Qy9mP2hW5fH6zV.yU0t8rVbC', 'EMPLEADO', 1, 'ACTIVO'),
(3, 'Martín Pérez', 'martin@example.com', '$2b$12$K8yXW0lCgR8kF.vI4R4n1.gWqPZc0Qy9mP2hW5fH6zV.yU0t8rVbC', 'CLIENTE', NULL, 'ACTIVO');

-- Productos (Candy Bar)
INSERT INTO productos (id_producto, nombre, descripcion, tipo, precio_base, estado) VALUES
(1, 'Combo Victoriano Popcorn', 'Pochoclos balde mediano + 1 Gaseosa 500ml', 'COMBO', 3500.00, 'ACTIVO'),
(2, 'Combo Imperial Real', 'Pochoclos balde grande + 2 Gaseosas grandes + Bombones', 'COMBO', 6200.00, 'ACTIVO');

-- Inventario en Sucursal 1
INSERT INTO inventario_sucursal (id_sucursal, id_producto, stock_actual, stock_minimo) VALUES
(1, 1, 50, 10),
(1, 2, 30, 5);

-- Servicios Adicionales
INSERT INTO servicios (id_servicio, nombre, descripcion, tipo, precio_base, requiere_cupo, estado) VALUES
(1, 'Estacionamiento Reservado', 'Cochera fija techada dentro del predio del cine', 'ESTACIONAMIENTO', 2000.00, TRUE, 'ACTIVO'),
(2, 'Acceso VIP Lounge', 'Ingreso exclusivo a sala victoriana pre-función', 'ACCESO_VIP', 1500.00, TRUE, 'ACTIVO');

-- Cupos para la Función 1
INSERT INTO cupos_servicios_funcion (id_funcion, id_servicio, cupo_total, cupo_disponible, estado) VALUES
(1, 1, 20, 20, 'DISPONIBLE'),
(1, 2, 15, 15, 'DISPONIBLE');

select id_pelicula, titulo, genero FROM peliculas