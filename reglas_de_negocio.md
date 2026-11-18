# Documento de Alcance y Reglas de Negocio (Hito 1) — Cine Paradiso

* **Proyecto:** Sistema de Venta de Entradas de Cine — Cine Paradiso
* **Cátedra:** Introducción al Desarrollo de Software (FIUBA — 2026)
* **Arquitectura:** Frontend BFF (Flask + Jinja2) → `Python requests` → Backend API REST (Flask) → MySQL 8

---

## 1. Reglas de Negocio Vigentes

### 1.1. Sucursales, Salas y Aforo
* **Complejos y salas:** El sistema gestiona sucursales físicas (`sucursales`) y salas de proyección asociadas (`salas`). Cada sala posee un nombre único dentro de su sucursal y una capacidad entera admitida entre **1 y 200 butacas**.
* **Generación automática de butacas:** Al dar de alta una sala (`POST /api/sucursales/<id>/salas`), el sistema genera automáticamente tantos registros en `asientos` como indique su `capacidad`, distribuidos en filas correlativas de 10 columnas (`A1`–`A10`, `B1`–`B10`, etc.). Todas las butacas de una función comparten el mismo precio base definido en la función.
* **Aforo estricto (sin sobreventa):** Una butaca no puede venderse más de una vez para la misma función. Esta regla se garantiza tanto en las validaciones del Backend como mediante la restricción única `UNIQUE (id_funcion, id_asiento)` en la tabla `entradas`.
* **Restricción de eliminación de salas:** No se permite eliminar una sala (`409 Conflict`) si tiene funciones programadas o entradas asociadas.

### 1.2. Catálogo de Películas e Integración con TMDb
* **Búsqueda externa y persistencia local:** Los administradores (`ADMIN`) consultan películas en la API externa **TMDb** (`GET /api/peliculas-externas?q=...`, hasta 8 resultados por búsqueda), obteniendo título, sinopsis en español, póster (`w500`), duración en minutos (con valor por defecto de `120` min si no está informada), género principal (`"General"` por defecto) y clasificación por edad (priorizando certificaciones de Argentina `AR`, luego `ES`/`US`, con valor por defecto `"+13"`).
* **Importación controlada:** Los resultados externos no se almacenan automáticamente. Solo persisten en la tabla local `peliculas` cuando el administrador confirma su alta (`POST /api/peliculas`). No se permite duplicar películas existentes en el catálogo local (`409 Conflict`).

### 1.3. Programación de Funciones
* **Fecha y hora unificada:** Cada función asocia una película y una sala en un único campo `fecha_hora` de tipo `DATETIME` junto con su `precio_entrada` ($\ge 0$).
* **Validación temporal y zona horaria:** Al crear una función (`POST /api/funciones`), la marca temporal debe enviarse en formato ISO 8601 con zona horaria, se normaliza a hora local de Argentina (`UTC-3`) y debe ser estrictamente **futura** respecto del instante actual.
* **No solapamiento horario en una misma sala:** Antes de registrar una función, el Backend verifica todas las proyecciones existentes en la misma sala calculando el intervalo exacto de proyección `[fecha_hora, fecha_hora + duracion_min]`. Si existe intersección temporal (`inicio_nueva < fin_existente` y `fin_nueva > inicio_existente`), la operación se rechaza con `409 Conflict`.
* **Restricción de eliminación de funciones:** No se permite eliminar una función (`409 Conflict`) si ya tiene entradas vendidas asociadas.

### 1.4. Usuarios, Roles y Seguridad de Contraseñas
* **Roles del sistema:** Existen únicamente dos roles: `CLIENTE` y `ADMIN`. Todo registro público (`POST /api/usuarios`) crea cuentas con rol `CLIENTE`.
* **Validación de credenciales:** El `nombre`, `email` y `password` son obligatorios. El correo electrónico se normaliza a minúsculas, debe tener formato válido y ser **único** en el sistema (`409 EMAIL_DUPLICADO` si ya existe). La contraseña debe tener una **longitud mínima de 6 caracteres** y se almacena cifrada (`password_hash`), nunca en texto plano.
* **Recuperación y restablecimiento de contraseña:**
  * Al solicitar recuperación (`POST /api/recuperar-password`), el sistema emite un token firmado temporal de **un solo uso** y validez de **30 minutos**, enviando el enlace al correo registrado.
  * Para evitar la enumeración de usuarios, el endpoint responde siempre `200 OK` con un mensaje neutro independientemente de si el correo existe o no en la base de datos.
  * Al restablecer (`POST /api/restablecer-password`), se verifica la firma y vigencia del token y se exige una nueva contraseña de al menos **6 caracteres**.

### 1.5. Ciclo de Compra, Bloqueo de Asientos y Comprobante con QR
* **Selección de butacas:** El cliente selecciona butacas libres para una única función. En la interfaz web se permite elegir entre **1 y 6 butacas** por operación; el Backend valida que la lista no esté vacía, no contenga duplicados y pertenezca a la sala de la función.
* **Bloqueo temporal y expiración automática:**
  * Al iniciar la compra, se crea un registro en `compras` con estado `PENDIENTE` y bloqueos en `bloqueos_asientos` con estado `ACTIVO` y vigencia de **10 minutos** (`vence_en = NOW() + INTERVAL 10 MINUTE`).
  * Adicionalmente, el evento programado de MySQL (`expirar_compras_pendientes`, ejecutado cada 1 segundo) marca automáticamente como `EXPIRADA` toda compra `PENDIENTE` cuyo bloqueo haya vencido, liberando los asientos.
* **Confirmación y cálculo en servidor:** En el flujo de compra (`POST /api/compras`), el Backend verifica nuevamente que los asientos no tengan entradas emitidas, congela los precios unitarios de entradas y servicios desde la base de datos, calcula `monto_total` en el servidor, emite las filas en `entradas` y pasa la compra a estado `CONFIRMADA`. Ante cualquier colisión concurrente sobre una butaca, devuelve `409 ASIENTO_NO_DISPONIBLE`.
* **Generación de QR y envío por email:** Al confirmarse la compra, se genera un identificador único `codigo_qr` (UUID) con `estado_qr = 'PENDIENTE'` y se envía un correo electrónico mediante **Resend** con el detalle de la función, butacas, servicios, monto total y la imagen PNG del código QR adjunta (utilizando `Idempotency-Key` por compra para evitar envíos duplicados). Si el servicio de correo falla, se registra la incidencia en los logs sin revertir la compra ya confirmada.

### 1.6. Servicios Adicionales
* **Catálogo global:** Los servicios adicionales (`COMIDA`, `BEBIDA`, `COMBO`, `ESTACIONAMIENTO`, `VIP`, `OTRO`) se administran de forma centralizada en la tabla `servicios` y están disponibles para complementar cualquier compra de entradas, sin distinción de sucursal ni control de stock individual.
* **Límites en compra:** Los servicios son opcionales dentro de una compra de entradas (no se admiten compras de servicios sin función ni butacas) y se permite solicitar entre **0 y 10 unidades** como máximo por servicio.
* **Restricción de eliminación de servicios:** No se puede eliminar un servicio (`409 SERVICIO_EN_USO`) si ya forma parte de `detalle_compra_servicios` en alguna compra registrada.

### 1.7. Política de Cancelación de Compras
* **Regla de los 60 minutos:** Un cliente puede cancelar únicamente sus propias compras confirmadas (`PATCH /api/compras/<id>` con `{"estado_qr": "CANCELADO"}`) siempre que el código QR se encuentre en estado `PENDIENTE` y falten **más de 60 minutos** para el inicio de la función (`funciones.fecha_hora`). Si el margen es de 60 minutos o menos, o el QR ya fue utilizado o cancelado, se rechaza con `409 COMPRA_NO_CANCELABLE`.
* **Efecto en base de datos:** La cabecera en `compras` conserva su registro histórico pasando a `estado_compra = 'CANCELADA'` y `estado_qr = 'CANCELADO'`, mientras que sus filas en `entradas` se eliminan y sus registros en `bloqueos_asientos` pasan a `'LIBERADO'` para que las butacas vuelvan a estar disponibles inmediatamente.

### 1.8. Control de Acceso en Sala
* **Validación exclusiva por administrador:** Solo un usuario con rol `ADMIN` puede validar el ingreso en puerta (`PATCH /api/codigos-qr/<codigo_qr>` indicando `id_funcion`).
* **Condiciones de validez:**
  1. El código QR debe existir (`404 QR_NO_ENCONTRADO`).
  2. Su estado debe ser `'PENDIENTE'` (`409 QR_NO_VALIDO` si ya está `'USADO'` o `'CANCELADO'`).
  3. Debe pertenecer a la función que se está validando (`409 QR_FUNCION_INCORRECTA`).
  4. **Ventana horaria de ingreso:** La validación solo está habilitada entre **40 minutos antes** del inicio de la función (`fecha_hora - 40 min`) y el **fin de la película** (`fecha_hora + duracion_min`). Fuera de esa ventana se rechaza con `409 QR_FUERA_DE_HORARIO`.
* **Consumo único:** Al validarse correctamente, `estado_qr` cambia a `'USADO'`, bloqueando cualquier intento de reutilización.

### 1.9. Estadísticas, Reportes y Reseñas
* **Panel estadístico y PDF:** Los administradores disponen de consultas SQL agregadas de ocupación por función (filtrable por película o función), ventas por género, ventas por franja horaria, total de cancelaciones y descarga de un informe consolidado en **PDF** (`GET /api/estadisticas/reporte-pdf`).
* **Reseñas de películas:** Solo pueden publicar reseñas (`POST /api/peliculas/<id>/resenas`) los usuarios autenticados que cuenten con una compra de esa película cuyo código QR haya sido validado (`estado_qr = 'USADO'`). Cada reseña incluye una puntuación entera de **1 a 5** y un comentario opcional, admitiendo **como máximo una reseña por usuario y película** (`UNIQUE (id_usuario, id_pelicula)`).

---

## 2. Alcance del Proyecto

### 2.1. Dentro del Alcance (In Scope)
* **Arquitectura desacoplada:** Frontend BFF en Flask y Jinja2 que consume exclusivamente el Backend API REST en Flask mediante `Python requests` (sin peticiones AJAX/Fetch desde el navegador), persistiendo datos en MySQL 8 mediante consultas SQL explícitas sin ORM.
* **Experiencia de Cliente (`CLIENTE`):** Registro, inicio/cierre de sesión, recuperación de contraseña por correo, exploración de cartelera con filtros (género, sucursal, fecha), ficha de película, selección visual de butacas libres/ocupadas, agregado opcional de servicios adicionales, confirmación de compra con recepción de comprobante y QR por email, visualización de historial/QR en perfil, cancelación autogestionada hasta 60 minutos antes y publicación de reseñas tras asistir a la función.
* **Backoffice Administrativo (`ADMIN`):** Búsqueda e importación de películas desde TMDb, alta y baja de salas con generación automática de butacas, programación y baja de funciones con control antisolapamiento, administración del catálogo de servicios, validador de códigos QR en puerta, tablero de estadísticas y descarga de reporte en PDF.

### 2.2. Fuera del Alcance (Out of Scope)
* **Pasarelas de pago reales y facturación fiscal:** La confirmación de compra opera sin integración con procesadores bancarios/fintech reales ni emisión de comprobantes fiscales electrónicos homologados.
* **Streaming multimedia:** No se reproducen ni alojan archivos de video de películas.
* **Roles operativos intermedios y gestión de stock físico:** No existe rol `EMPLEADO`, control de inventario/stock de Candy Bar por sucursal, cupos de servicios por función ni compras de comida/bebida independientes sin función de cine.
* **Múltiples funciones en una sola compra:** Cada compra corresponde a una única función; para asistir a funciones distintas se deben realizar operaciones separadas.
