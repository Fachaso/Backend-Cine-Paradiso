# Cine Paradiso — Backlog de Producto Actualizado

**Base de alcance:** Enunciado del Proyecto Integrador IDS 2026, contrato OpenAPI 3.0.3 (`swagger.yaml` v2.1.0), esquema MySQL de 12 tablas (`schema.sql`) e implementación vigente en los repositorios **Backend-Cine-Paradiso** y **Front-Cine-Paradiso**.

**Convención de estados:**
* `[x]` Implementado y verificado en el código actual.
* `[ ]` Pendiente de integración (ramas en desarrollo) o cierre de entrega.

**Etiquetas:** `BACKEND`, `FRONTEND`, `SQL-BD`, `DEVOPS`, `DOCS`; `obligatorio` y `opcional`.

---

## Épica 0 — Preparación del proyecto y arquitectura

**Objetivo:** Disponer de una base de trabajo modular y funcional para Backend Flask, Frontend BFF Flask y MySQL 8.

### TASK-01 — Repositorio, tablero e instalación `[DEVOPS]` `[obligatorio]`
- [x] Los repositorios GitHub (`Backend-Cine-Paradiso` y `Front-Cine-Paradiso`) contienen el trabajo del equipo con acceso para el corrector.
- [x] El equipo utiliza ramas por funcionalidad y registra commits asociados a tareas.
- [x] Existen los archivos `init.sh` y `requirements.txt` para instalar las dependencias en ambos proyectos.

### TASK-02 — Esquema de base de datos `[SQL-BD]` `[obligatorio]`
- [x] El script `schema.sql` crea la base `cine_paradiso` con sus 12 tablas: `sucursales`, `salas`, `asientos`, `peliculas`, `funciones`, `usuarios`, `compras`, `entradas`, `servicios`, `detalle_compra_servicios`, `bloqueos_asientos` y `resenas`.
- [x] Se definen claves primarias, foráneas (`CASCADE` / `RESTRICT`), restricciones `UNIQUE` (`uq_asiento_sala`, `uq_funcion_asiento`, `uq_usuario_pelicula`) y valores `ENUM`.
- [x] Las funciones utilizan un único campo `fecha_hora` de tipo `DATETIME`.
- [x] Se incluye el evento programado `expirar_compras_pendientes` en MySQL para expirar compras pendientes vencidas y liberar bloqueos automáticamente.

### TASK-03 — Datos iniciales `[SQL-BD]` `[obligatorio]`
- [x] Existe un script de carga inicial (`database/`) compatible con el esquema de 12 tablas.
- [x] Se cargan sucursales, salas, asientos, un usuario administrador de prueba y servicios adicionales de ejemplo.

### TASK-04 — Base del Backend Flask `[BACKEND]` `[obligatorio]`
- [x] El Backend está estructurado en capas (`routes`, `controllers`, `services`, `repositories`, `validators`, `utils`) y expone los blueprints REST bajo `/api`.
- [x] Todas las consultas a MySQL utilizan sentencias SQL explícitas mediante `mysql-connector-python`, sin ORM ni mapeo de clases.
- [x] Las respuestas exitosas devuelven JSON con `status: "success"` y `data`; los errores manejados devuelven `status: "error"`, `code` y `message`.
- [x] Los endpoints protegidos validan la cookie de sesión de Flask y el rol requerido (`CLIENTE` o `ADMIN`).
- [x] Incluye endpoint de monitoreo `GET /api/health` y especificación `swagger.yaml`.

### TASK-05 — Base del Frontend Flask `[FRONTEND]` `[obligatorio]`
- [x] El Frontend BFF utiliza blueprints Flask (`auth`, `main`, `admin`), plantillas Jinja2 (`pages/`, `components/`) y formularios HTML.
- [x] Toda comunicación con el Backend se ejecuta desde Python con `requests`, propagando `session["backend_session"]` (sin `fetch`, `axios` ni `XMLHttpRequest` desde el navegador).
- [x] El diseño es responsive para computadoras, celulares y tablets.
- [x] Las vistas y acciones administrativas se restringen según el rol de la sesión autenticada.

---

## Épica 1 — Usuarios, autenticación y perfil

**Objetivo:** Registrar clientes, autenticar usuarios, gestionar recuperación de contraseña y mostrar historial de compras.

### US-01 — Registro e inicio/cierre de sesión `[BACKEND]` `[obligatorio]`
**Como** visitante o usuario registrado, **quiero** crear una cuenta e iniciar o cerrar sesión **para** acceder a las funcionalidades de mi rol.

**API:** `POST /api/usuarios`, `POST /api/sesiones`, `DELETE /api/sesiones`, `GET /api/me`.  
**SQL:** `usuarios`.

- [x] Al enviar `nombre`, `email` y `password` (mínimo 6 caracteres), se crea un usuario `CLIENTE` con contraseña cifrada (`password_hash`) y devuelve `201`; un email duplicado responde `409 EMAIL_DUPLICADO`.
- [x] Al presentar credenciales válidas, `POST /api/sesiones` inicia la sesión en Flask y devuelve `200` con `id_usuario`, `nombre`, `email` y `rol` (`CLIENTE` o `ADMIN`).
- [x] `DELETE /api/sesiones` invalida la sesión activa y responde `204`.
- [x] `GET /api/me` permite verificar y recuperar los datos del usuario autenticado.

### US-02 — Pantallas de registro y acceso `[FRONTEND]` `[obligatorio]`
**Como** cliente o administrador, **quiero** registrarme e iniciar sesión desde formularios web **para** operar en el sistema.

**Rutas Front:** `GET/POST /registro`, `GET/POST /login`, `POST /logout`.

- [x] Existen formularios responsive en `pages/login_registro.html` con mensajes flash claros ante errores o confirmaciones.
- [x] Los formularios se procesan mediante rutas Flask y llamadas `requests` en `services/auth_service.py`.
- [x] Al iniciar sesión se guardan `id_usuario`, `nombre`, `rol` y `backend_session` en sesión; existe opción de cierre de sesión.

### US-03 — Perfil e historial de compras `[BACKEND]` `[FRONTEND]` `[obligatorio]`
**Como** cliente autenticado, **quiero** consultar mis datos personales, compras, entradas, servicios y películas vistas **para** hacer seguimiento de mi actividad.

**API:** `GET /api/perfil`, `GET /api/compras/{id_compra}`.  
**Rutas Front:** `GET /perfil`, `GET /mis-compras/{id_compra}`.  
**SQL:** `usuarios`, `compras`, `entradas`, `funciones`, `peliculas`, `detalle_compra_servicios`, `servicios`.

- [x] El cliente autenticado visualiza en `/perfil` sus datos, su historial de compras y el listado de películas vistas (`estado_qr == 'USADO'`).
- [x] Desde `/mis-compras/<id_compra>` (`pages/compra_detalle.html`) puede ver el detalle de entradas, servicios y el código QR renderizado en pantalla cuando `estado_qr == 'PENDIENTE'`.
- [x] Las compras canceladas se muestran con su estado correspondiente y no figuran como asistidas.

---

## Épica 2 — Catálogo y cartelera

**Objetivo:** Importar películas desde TMDb y publicarlas junto con sus funciones vigentes.

### US-04 — Importación de películas desde TMDb `[BACKEND]` `[FRONTEND]` `[obligatorio]`
**Como** administrador, **quiero** buscar películas en TMDb e incorporarlas al catálogo local **para** armar la cartelera.

**API:** `GET /api/peliculas-externas?q=...`, `POST /api/peliculas`.  
**Rutas Front:** `GET /admin/peliculas`, `POST /admin/peliculas`.  
**SQL:** `peliculas`.

- [x] El Backend consulta TMDb en paralelo (`tmdb_service.py`), normaliza clasificación por edad (priorizando `AR`, luego `ES`/`US`), duración, género y póster, y devuelve hasta 8 candidatos sin persistirlos automáticamente.
- [x] Al confirmar la importación (`POST /api/peliculas`), solo un `ADMIN` puede guardar la película en `peliculas` (`201`), rechazando duplicados (`409`).
- [x] El backoffice (`pages/admin_cargar_pelicula.html` y `components/_form_importar_pelicula.html`) incluye buscador TMDb y formulario de importación indicando si el título ya existe en el catálogo.

### US-05 — Consulta del catálogo y funciones `[BACKEND]` `[obligatorio]`
**Como** visitante, **quiero** consultar las películas y funciones disponibles **para** elegir qué función ver.

**API:** `GET /api/peliculas`, `GET /api/peliculas/{id_pelicula}`, `GET /api/funciones`, `GET /api/funciones/{id_funcion}`.  
**SQL:** `peliculas`, `funciones`, `salas`, `sucursales`.

- [x] `GET /api/peliculas` admite filtrado por `genero` y `titulo`.
- [x] `GET /api/funciones` admite filtrado por `id_pelicula`, `id_sucursal` y `fecha`, devolviendo datos completos de película, sala, sucursal, `fecha_hora` y `precio_entrada`.

### US-06 — Interfaz pública de cartelera y detalle `[FRONTEND]` `[obligatorio]`
**Como** visitante, **quiero** explorar la cartelera y filtrar funciones **para** iniciar una compra.

**Rutas Front:** `GET /`, `GET /pelicula/{id_pelicula}`.

- [x] La portada (`pages/index.html`) muestra las tarjetas de películas con filtros por `genero`, `id_sucursal` y `fecha`.
- [x] La ficha de película (`pages/pelicula_detalle.html`) muestra sinopsis, póster, duración, clasificación y funciones filtrables con enlace directo a la selección de butacas.

---

## Épica 3 — Sucursales, salas y programación

**Objetivo:** Administrar salas con sus asientos y programar funciones sin solapamiento horario.

### US-07 — Consulta de sucursales y gestión de salas `[BACKEND]` `[obligatorio]`
**Como** administrador, **quiero** consultar sucursales y crear o eliminar salas **para** gestionar la capacidad del cine.

**API:** `GET /api/sucursales`, `GET /api/sucursales/{id_sucursal}/salas`, `POST /api/sucursales/{id_sucursal}/salas`, `DELETE /api/sucursales/{id_sucursal}/salas/{id_sala}`.  
**SQL:** `sucursales`, `salas`, `asientos`.

- [x] Cualquier visitante puede listar sucursales y salas.
- [x] Solo `ADMIN` puede crear salas (`capacidad` entera entre `1` y `200`, nombre único por sucursal), generando automáticamente las butacas en `asientos` por fila (`A`–`Z`, `AA`...) y número (`1`–`10`).
- [x] Solo `ADMIN` puede eliminar salas (`DELETE`), bloqueando con `409` si tienen funciones o entradas asociadas.

### US-08 — Programación y eliminación de funciones `[BACKEND]` `[obligatorio]`
**Como** administrador, **quiero** programar y eliminar funciones en una sala **para** mantener la cartelera actualizada.

**API:** `GET /api/funciones`, `POST /api/funciones`, `GET /api/funciones/{id_funcion}`, `DELETE /api/funciones/{id_funcion}`.  
**SQL:** `funciones`, `peliculas`, `salas`, `sucursales`.

- [x] `POST /api/funciones` valida zona horaria, exige `fecha_hora` futura (normalizada a `UTC-3`) y `precio_entrada >= 0`.
- [x] Rechaza con `409` cualquier solapamiento horario en la misma sala calculando `[fecha_hora, fecha_hora + duracion_min]`.
- [x] `DELETE /api/funciones/{id_funcion}` permite eliminar funciones sin entradas vendidas y devuelve `409` si existen entradas asociadas.

### US-09 — Backoffice de salas y funciones `[FRONTEND]` `[obligatorio]`
**Como** administrador, **quiero** gestionar salas y funciones desde el panel web **para** configurar cada complejo.

**Rutas Front:** `GET /admin/peliculas`, `POST /admin/salas`, `POST /admin/salas/eliminar/{id_sucursal}/{id_sala}`, `POST /admin/funciones`, `POST /admin/funciones/eliminar/{id_funcion}`.

- [x] El panel administrativo (`pages/admin_cargar_pelicula.html` y componentes `_form_crear_sala.html`, `_tabla_salas.html`, `_form_crear_funcion.html`, `_tabla_funciones.html`) permite dar de alta y eliminar salas y funciones mostrando mensajes de éxito o conflicto.

---

## Épica 4 — Disponibilidad y selección de butacas

**Objetivo:** Visualizar el estado real de cada sala y seleccionar asientos disponibles sin duplicados.

### US-10 — Disponibilidad de asientos por función `[BACKEND]` `[obligatorio]`
**Como** cliente, **quiero** consultar qué butacas están disponibles u ocupadas en una función **para** elegir mis ubicaciones.

**API:** `GET /api/funciones/{id_funcion}/asientos`.  
**SQL:** `funciones`, `salas`, `asientos`, `entradas`.

- [x] Devuelve la lista ordenada de asientos de la sala con `id_asiento`, `fila`, `numero` y `estado` (`DISPONIBLE` u `OCUPADO`), devolviendo `404` si la función no existe.

### US-12 — Interfaz de selección de butacas `[FRONTEND]` `[obligatorio]`
**Como** cliente, **quiero** elegir visualmente entre 1 y 6 butacas libres **para** continuar con mi compra.

**Rutas Front:** `GET/POST /funciones/{id_funcion}/butacas`.

- [x] La vista `pages/seleccion_butacas.html` agrupa las butacas por fila (`butacas_service.py`), diferencia libres y ocupadas, valida seleccionar entre **1 y 6 asientos** y guarda la selección en `session["compra_pendiente"]`.

---

## Épica 5 — Servicios adicionales

**Objetivo:** Administrar el catálogo de servicios y ofrecerlos como complemento opcional en la compra.

### US-13 — Catálogo y administración de servicios `[BACKEND]` `[FRONTEND]` `[obligatorio]`
**Como** administrador, **quiero** consultar, crear, modificar y dar de baja servicios **para** ofrecer complementos en el cine.

**API:** `GET /api/servicios`, `POST /api/servicios`, `GET /api/servicios/{id_servicio}`, `PATCH /api/servicios/{id_servicio}`, `DELETE /api/servicios/{id_servicio}`.  
**Ruta Front:** `GET /admin/servicios`.  
**SQL:** `servicios`, `detalle_compra_servicios`.

- [x] El Backend implementa el CRUD completo de servicios para tipos `COMIDA`, `BEBIDA`, `COMBO`, `ESTACIONAMIENTO`, `VIP` y `OTRO`, impidiendo eliminar servicios ya utilizados en compras (`409 SERVICIO_EN_USO`).
- [ ] Completar en el Frontend la plantilla `pages/admin_abm_servicios.html` (referenciada en `routes/admin_routes.py`) y las rutas `POST` para alta, edición y baja de servicios desde el backoffice.

### US-16 — Selección de servicios en la compra `[FRONTEND]` `[obligatorio]`
**Como** cliente, **quiero** agregar servicios opcionales a mis entradas **para** completar mi compra.

**Ruta Front:** `GET /compras/servicios`.

- [x] Tras elegir butacas, `pages/seleccion_servicios.html` permite elegir de `0` a `10` unidades por servicio antes de confirmar la compra.

---

## Épica 6 — Compra, comprobante y código QR

**Objetivo:** Procesar la compra de entradas y servicios, generar el QR y enviar el comprobante por correo.

### US-17 — Registro de compra de entradas y servicios `[BACKEND]` `[obligatorio]`
**Como** cliente autenticado, **quiero** confirmar mi compra de entradas y servicios **para** asegurar mis butacas.

**API:** `POST /api/compras`, `GET /api/compras/{id_compra}`.  
**SQL:** `compras`, `bloqueos_asientos`, `entradas`, `funciones`, `asientos`, `servicios`, `detalle_compra_servicios`.

- [x] Valida función, lista no vacía ni repetida de asientos pertenecientes a la sala y servicios opcionales (máx. 10 unidades por servicio).
- [x] Gestiona bloqueo temporal de asientos (`bloqueos_asientos`), verifica disponibilidad antes de emitir entradas (`409 ASIENTO_NO_DISPONIBLE` ante colisión), calcula `monto_total` en el servidor y registra precios históricos en `entradas` y `detalle_compra_servicios`.

### US-18 — Código QR y envío del comprobante por email `[BACKEND]` `[obligatorio]`
**Como** cliente, **quiero** recibir por email el detalle de mi compra junto con el código QR **para** presentarlo al ingresar a la sala.

**Servicios Backend:** `compras_service.py`, `email_service.py`, `qr_generator.py`.

- [x] Genera un `codigo_qr` único (UUID) en estado `PENDIENTE` al confirmar la compra.
- [x] Envía correo HTML y texto plano mediante **Resend** con detalle de película, función, butacas, servicios, monto total e imagen PNG del código QR embebida (`cid:qr_compra`), utilizando `Idempotency-Key` por compra.

### US-19 — Confirmación de compra en Frontend `[FRONTEND]` `[obligatorio]`
**Como** cliente, **quiero** confirmar mi selección y ver mi comprobante **para** finalizar la operación.

**Rutas Front:** `POST /compras/servicios`, `GET /mis-compras/{id_compra}`.

- [x] Envía la compra al Backend vía `requests` (`POST /api/compras`); si ocurre `409` por butaca ocupada, redirige a la selección de butacas con aviso; si es exitosa (`201`), redirige al perfil y permite abrir el comprobante con QR.

---

## Épica 7 — Control de acceso y cancelación

**Objetivo:** Validar el ingreso en puerta mediante código QR y permitir cancelaciones dentro del plazo permitido.

### US-20 — Validación del QR al ingresar a sala `[BACKEND]` `[obligatorio]`
**Como** administrador, **quiero** validar el código QR contra la función **para** controlar el ingreso y evitar reingresos.

**API:** `PATCH /api/codigos-qr/{codigo_qr}` con `{"id_funcion": ...}`.  
**SQL:** `compras`, `entradas`, `funciones`, `peliculas`.

- [x] Solo `ADMIN` puede validar códigos QR.
- [x] Verifica existencia (`404`), `estado_qr == 'PENDIENTE'` (`409`), correspondencia con `id_funcion` (`409`) y ventana horaria habilitada (**desde 40 minutos antes** del inicio hasta el fin de la película, `409`).
- [x] Marca `estado_qr = 'USADO'` para impedir su reutilización.

### US-22 — Interfaz de control de acceso `[FRONTEND]` `[obligatorio]`
**Como** administrador, **quiero** validar códigos QR desde el backoffice **para** autorizar o denegar el ingreso en sala.

**Rutas Front:** `GET/POST /admin/validador`.

- [x] Vista `pages/admin_validador.html` restringida a `ADMIN` para seleccionar la función, ingresar el código QR y visualizar claramente si el acceso fue permitido o denegado con su motivo.

### US-23 — Cancelación de compra vigente `[BACKEND]` `[FRONTEND]` `[obligatorio]`
**Como** cliente, **quiero** cancelar mi compra con antelación suficiente **para** liberar las butacas.

**API:** `PATCH /api/compras/{id_compra}` con `{"estado_qr": "CANCELADO"}`.  
**Ruta Front:** `POST /mis-compras/{id_compra}/cancelacion`.  
**SQL:** `compras`, `entradas`, `bloqueos_asientos`, `funciones`.

- [x] Verifica que la compra pertenezca al usuario autenticado, que su `estado_qr` sea `PENDIENTE` y que falten **más de 60 minutos** para el inicio de la función (`PLAZO_CANCELACION_MINUTOS = 60`).
- [x] Cambia la compra a `estado_compra = 'CANCELADA'` y `estado_qr = 'CANCELADO'`, elimina sus registros en `entradas` y libera los bloqueos en `bloqueos_asientos`.
- [x] El Frontend ofrece el botón de cancelación desde el perfil/detalle y muestra el mensaje de confirmación o rechazo.

---

## Épica 8 — Estadísticas y reportes del administrador

**Objetivo:** Proveer indicadores operativos y descarga de reportes en PDF para la toma de decisiones.

### US-25 — Consultas de estadísticas y reporte PDF `[BACKEND]` `[obligatorio]`
**Como** administrador, **quiero** consultar métricas de ocupación, ventas, horarios y cancelaciones y exportarlas a PDF **para** analizar el rendimiento del cine.

**API:** `GET /api/estadisticas/ocupacion`, `GET /api/estadisticas/ventas-por-genero`, `GET /api/estadisticas/franjas-horarias`, `GET /api/estadisticas/cancelaciones`, `GET /api/estadisticas/reporte-pdf`.  
**SQL:** `funciones`, `salas`, `peliculas`, `entradas`, `compras`.

- [x] Calcula ocupación por función (filtrable por `id_funcion` e `id_pelicula`), ventas agrupadas por género, ventas por franja horaria y total de compras canceladas.
- [x] Genera en memoria un informe consolidado en PDF con ReportLab (`reporte_pdf_service.py`) incluyendo cancelaciones, top 5 películas más vistas y ventas por género.

### US-26 — Dashboard de administración `[FRONTEND]` `[obligatorio]`
**Como** administrador, **quiero** visualizar las estadísticas y descargar el reporte PDF desde el backoffice **para** monitorear el negocio.

**Rutas Front:** `GET /admin/dashboard`, `GET /admin/estadisticas/reporte-pdf`.

- [x] Vista `pages/admin_dashboard.html` restringida a `ADMIN` con tarjetas/tablas de indicadores, filtros por película o función y botón de descarga directa de `reporte-cine-paradiso.pdf`.

---

## Épica 9 — Reseñas de películas (deseable)

**Objetivo:** Permitir que los espectadores que asistieron a una función califiquen y comenten la película.

### US-28 — Consulta y creación de reseñas `[BACKEND]` `[FRONTEND]` `[opcional]`
**Como** cliente que asistió a una función, **quiero** puntuar y reseñar la película **para** compartir mi opinión con otros usuarios.

**API:** `GET /api/peliculas/{id_pelicula}/resenas`, `POST /api/peliculas/{id_pelicula}/resenas`.  
**SQL:** `resenas`, `usuarios`, `peliculas`, `compras`, `entradas`, `funciones`.

- [x] Tabla `resenas` definida en `schema.sql` con `puntuacion` (`1` a `5`), `comentario` opcional y restricción `UNIQUE (id_usuario, id_pelicula)`.
- [x] Contrato documentado en `swagger.yaml` v2.1.0 restringiendo la creación a usuarios con compra de esa película en estado `estado_qr = 'USADO'`.
- [ ] Integración de la rama de reseñas en el repositorio principal del Backend y sección de reseñas en `pages/pelicula_detalle.html`.

---

## Épica 10 — Calidad, documentación y entrega

**Objetivo:** Completar la documentación técnica, las pruebas integradas y la presentación final del proyecto.

### TASK-31 — Documentación técnica `[DOCS]` `[obligatorio]`
- [x] Documentación actualizada en `tablas.md`, `endpoints.md`, `hito1.md`, `backlog.md` y `swagger.yaml`.
- [ ] Actualización final de `README.md` en Backend y Frontend con arquitectura, estructura real, instalación y variables de entorno.

### TASK-32 — Informe y preparación de la defensa `[DOCS]` `[obligatorio]`
- [ ] Redacción del informe final (carátula, integrantes, resumen, introducción, solución propuesta, tecnología utilizada, decisiones de diseño, dificultades y conclusiones).
- [ ] Preparación de la demostración en vivo y defensa oral grupal e individual.

### TASK-33 — Pruebas integradas `[BACKEND]` `[FRONTEND]` `[SQL-BD]` `[obligatorio]`
- [ ] Validación integral de extremo a extremo tras el merge de recuperación de contraseña y reseñas (flujo completo de cliente, validaciones de concurrencia, QR, cancelación, backoffice admin y navegación responsive).

### US-34 — Recuperación y restablecimiento de contraseña por correo electrónico (`#77`) `[BACKEND]` `[FRONTEND]` `[funcionalidad agregada]`
**Como** usuario registrado, **quiero** solicitar un enlace de recuperación de contraseña a mi correo electrónico **para** poder definir una nueva clave y volver a ingresar a mi cuenta si la olvidé.

**API:** `POST /api/recuperar-password`, `POST /api/restablecer-password`.  
**Rutas Front:** `GET/POST /recuperar-password`, `GET/POST /restablecer-password/<token>`.  
**SQL:** `usuarios`.

- [ ] El usuario puede ingresar su email desde `/recuperar-password` y recibe una respuesta neutra sin exponer si el correo existe en la base de datos.
- [ ] Si el correo está registrado, se envía un email (vía Resend) con un enlace firmado válido por **30 minutos**.
- [ ] Desde `/restablecer-password/`, el usuario puede ingresar y confirmar una nueva contraseña (mínimo **6 caracteres**) y luego iniciar sesión con ella.
- [ ] El enlace queda invalidado de un solo uso una vez utilizada la recuperación o pasado el tiempo de expiración.
- [x] Contrato documentado en `swagger.yaml` (v2.1.0) y reglas de negocio actualizadas en `hito1.md`.
