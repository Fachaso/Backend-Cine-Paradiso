<div align="right">
    <img width="32px" src="img/logo_intro.desarrollo.software.png">
</div>

# Cine Paradiso — Backend API REST

Sistema integral de venta de entradas de cine desarrollado como Proyecto Integrador para la cátedra **Introducción al Desarrollo de Software (FIUBA)**. Este repositorio contiene la **API REST en Flask** encargada de la lógica de negocio, autenticación por sesión, persistencia en MySQL 8, integración con TMDb, emisión de códigos QR, envío de comprobantes por correo electrónico y generación de reportes estadísticos[cite: 3, 4, 19].

---

## Enlaces del Proyecto

* **Repositorio Backend (API REST):** [Backend-Cine-Paradiso](https://github.com/Fachaso/Backend-Cine-Paradiso)
* **Repositorio Frontend (BFF Flask + Jinja2):** [Front-Cine-Paradiso](https://github.com/lutzio07/Front-Cine-Paradiso)
* **Diseño / Mockups:** [https://www.figma.com/proto/sehm8206edP58cDz0Sj8f8/Figma-basics?node-id=3825-988&p=f&t=nzzL0frzXv6JGVMO-1&scaling=min-zoom&content-scaling=fixed&page-id=3825%3A5]
* **Contrato OpenAPI:** Ver archivo [`swagger.yaml`](./swagger.yaml)[cite: 4, 5]
* **Backlog del Producto:** [backlog.md](./backlog.md)
* **Reglas de Negocio y Alcance:** [Reglas de negocio.md](./Reglas%20de%20negocio.md)
* **Esquema de Base de Datos:** [Tablas y relaciones.md](esta ubicado en el front)

---

## Integrantes del Equipo

* Ramiro Tomas Martinez — `115961` — rtmartinez@fi.uba.ar — [@Fachaso](https://github.com/Fachaso)
* Juan Francisco Misiac — `116102` — jmisiac@fi.uba.ar
* Eliel Jone Castillo — `116526` — ejone@fi.uba.ar
* Lucas Nahuel Uran — `116478` — luran@fi.uba.ar
* Matias Ezequiel Montiel — `116556` — memontiel@fi.uba.ar
* Joaquín Transillo — `116250` — jtransillo@fi.uba.ar
* Jorge Félix García Sánchez — `116133` — jfgarcias@fi.uba.ar
* Diego Oliver Yujra Cossio — `116532` — dyujra@fi.uba.ar
* Maximiliano Alexis Silva — `115666` — masilva@fi.uba.ar
* Lucio Valentín Villagra — `116288` — lvillagra@fi.uba.ar[cite: 4]

---

## Arquitectura del Sistema

La solución implementa una arquitectura desacoplada en tres capas:

```text
[ Navegador ]
      │  (HTML / Formularios GET-POST, sin fetch/AJAX)
      ▼
[ Frontend BFF — Flask + Jinja2 ]  (Puerto 5001)
      │  (HTTP JSON + Cookie de sesión vía Python requests)
      ▼
[ Backend API REST — Flask ]       (Puerto 5000)
      │  (Sentencias SQL explícitas sin ORM vía mysql-connector-python)
      ▼
[ Base de Datos — MySQL 8.0+ ]     (12 tablas + Event Scheduler)
```

### Integraciones Externas y Servicios
* **TMDb API (`tmdb_service.py`):** Consulta de películas por palabra clave con obtención paralela de detalles (duración, género, sinopsis, póster y certificación por edad priorizando Argentina `AR`) para importar al catálogo local[cite: 33].
* **Resend API (`email_service.py`):** Envío de comprobantes de compra en formato HTML y texto plano con imagen PNG del código QR embebida (`cid:qr_compra`) y control de idempotencia[cite: 40].
* **Generación de QR y PDF (`qr_generator.py`, `reporte_pdf_service.py`):** Creación de códigos QR únicos por compra y exportación en memoria de reportes estadísticos en formato PDF mediante ReportLab[cite: 36, 40].

---

## Tecnologías y Versiones Utilizadas

* **Lenguaje:** Python 3.10 o superior
* **Framework Web:** Flask `>= 3.0.0`, Flask-CORS `4.0.1`, Werkzeug `3.0.3`
* **Base de Datos:** MySQL `8.0+` con conector oficial `mysql-connector-python >= 8.0.33`
* **Cliente HTTP y Configuración:** `requests >= 2.31.0`, `python-dotenv >= 1.0.0`
* **QR, Criptografía y Reportes:** `qrcode[pil] >= 7.4.2`, `Pillow >= 10.0.0`, `cryptography >= 41.0.0`, `reportlab >= 4.0.0`
* **Testing:** `pytest >= 7.4.0`[cite: 4, 56]

---

## Estructura del Repositorio

```text
Backend-Cine-Paradiso/
├── app/
│   ├── controllers/               # Manejo de requests HTTP, parámetros y códigos de estado
│   │   ├── auth_controller.py
│   │   ├── compras_controller.py
│   │   ├── control_acceso_controller.py
│   │   ├── estadisticas_controller.py
│   │   ├── funcion_controller.py
│   │   ├── pelicula_controller.py
│   │   ├── perfil_controller.py
│   │   ├── servicio_controller.py
│   │   └── sucursal_controller.py
│   ├── repositories/              # Consultas SQL nativas explícitas contra MySQL 8
│   │   ├── asiento_repository.py
│   │   ├── compra_repository.py
│   │   ├── control_acceso_repository.py
│   │   ├── db_connection.py
│   │   ├── estadisticas_repository.py
│   │   ├── funcion_repository.py
│   │   ├── pelicula_repository.py
│   │   ├── perfil_repository.py
│   │   ├── servicio_repository.py
│   │   ├── sucursal_repository.py
│   │   ├── usuario_email_repository.py
│   │   └── usuario_repository.py
│   ├── routes/                    # Blueprints REST registrados bajo /api
│   │   ├── auth_routes.py
│   │   ├── compras_routes.py
│   │   ├── control_acceso_routes.py
│   │   ├── estadisticas_routes.py
│   │   ├── funciones_routes.py
│   │   ├── peliculas_routes.py
│   │   ├── perfil_routes.py
│   │   ├── servicios_routes.py
│   │   └── sucursales_routes.py
│   ├── services/                  # Lógica de negocio e integraciones externas
│   │   ├── auth_service.py
│   │   ├── compras_service.py
│   │   ├── control_acceso_service.py
│   │   ├── email_service.py
│   │   ├── estadisticas_service.py
│   │   ├── funciones_service.py
│   │   ├── peliculas_service.py
│   │   ├── perfil_service.py
│   │   ├── reporte_pdf_service.py
│   │   ├── servicio_service.py
│   │   ├── sucursal_service.py
│   │   └── tmdb_service.py
│   ├── utils/                     # Helpers de sesión, errores JSON y generación de QR
│   │   ├── auth.py
│   │   └── qr_generator.py
│   └── validators/                # Validación y sanitización de payloads de entrada
│       ├── compra_validator.py
│       ├── funcion_validator.py
│       ├── pelicula_validator.py
│       ├── servicio_validator.py
│       ├── sucursal_validator.py
│       └── usuario_validator.py
├── database/                      # Scripts SQL de estructura y datos iniciales
│   ├── schema.sql
│   └── seed.sql
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore
├── app.py                         # Punto de entrada de la aplicación Flask
├── Enunciado.md                   # Consigna oficial del Proyecto Integrador
├── init.sh                        # Script de instalación de dependencias
├── README.md
├── requirements.txt
├── swagger.yaml                   # Especificación OpenAPI 3.0.3
└── Tablas y relaciones.md         # Documentación detallada del modelo relacional
```[cite: 4, 19, 36, 40, 41, 53, 54, 55]

---

## Instalación y Configuración en Local

### 1. Clonar el repositorio y crear el entorno virtual
```bash
git clone [https://github.com/Fachaso/Backend-Cine-Paradiso.git](https://github.com/Fachaso/Backend-Cine-Paradiso.git)
cd Backend-Cine-Paradiso

python3 -m venv venv
source venv/bin/activate        # En Linux / macOS
# venv\Scripts\activate         # En Windows (PowerShell / CMD)
```

### 2. Instalar dependencias
Podés ejecutar el script `init.sh` o instalar directamente desde `requirements.txt`:
```bash
bash init.sh
# o bien:
pip install -r requirements.txt
```[cite: 57]

### 3. Configurar variables de entorno
Copiá el archivo de ejemplo `.env.example` a `.env` y completá tus credenciales locales:
```bash
cp .env.example .env
```

| Variable | Obligatoria | Valor por defecto / Ejemplo | Descripción |
| :--- | :---: | :--- | :--- |
| `FLASK_APP` | Sí | `app.py` | Archivo principal de la aplicación Flask. |
| `FLASK_ENV` | Sí | `development` | Entorno de ejecución (`development` / `production`). |
| `SECRET_KEY` | Sí | `clave_secreta_backend_paradiso` | Clave secreta para firmar cookies de sesión y tokens temporales. |
| `DB_HOST` | Sí | `localhost` | Host del servidor MySQL 8. |
| `DB_PORT` | Sí | `3306` | Puerto de conexión a MySQL. |
| `DB_NAME` | Sí | `cine_paradiso` | Nombre de la base de datos. |
| `DB_USER` | Sí | `root` | Usuario de MySQL con permisos sobre `cine_paradiso` y `EVENT`. |
| `DB_PASSWORD` | Sí | `root` | Contraseña del usuario de MySQL. |
| `TMDB_API_KEY` | Sí | — | API Key v3 de [The Movie Database (TMDb)](https://developer.themoviedb.org/) para búsqueda de películas. |
| `RESEND_API_KEY` | Sí | — | API Key de [Resend](https://resend.com/) para el envío de comprobantes con QR por correo. |
| `RESEND_FROM_EMAIL` | Sí | `Cine Paradiso <onboarding@resend.dev>` | Dirección remitente verificada en Resend. |
| `PORT` | No | `5000` | Puerto donde escucha el servidor Backend. |
| `FLASK_DEBUG` | No | `True` | Activa o desactiva el modo debug de Flask. |[cite: 19, 33, 40, 58]

### 4. Configurar la Base de Datos (MySQL 8)
Ejecutá primero `database/schema.sql` para crear la base de datos `cine_paradiso`, sus **12 tablas** y el evento programado `expirar_compras_pendientes`, y luego `database/seed.sql` para cargar los datos de prueba:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

**Credenciales de prueba incluidas en `seed.sql`:**
* **Administrador (`ADMIN`):** `admin@cineparadiso.com` / `admin123`
* **Sucursales precargadas:** Cine Paradiso Central (Salas 1 y 2), Cine Paradiso Norte (Sala 1 Norte) y Cine Paradiso Sur.
* **Catálogo inicial:** 5 servicios adicionales (`COMBO`, `COMIDA`, `BEBIDA`, `ESTACIONAMIENTO`, `VIP`), 5 películas y 3 funciones de ejemplo[cite: 54, 55].

---

## Ejecución

Con el entorno virtual activo y MySQL corriendo, iniciá el servidor Backend:

```bash
python app.py
```

El servicio quedará disponible en **`http://localhost:5000`**. Podés verificar que esté operativo consultando el endpoint de salud:

```bash
curl http://localhost:5000/api/health
```

Respuesta esperada (`200 OK`):
```json
{
  "status": "success",
  "message": "Backend Cine Paradiso activo y funcionando correctamente"
}
```[cite: 19]

---

## Principales Decisiones de Diseño

* **SQL nativo sin ORM:** Todas las consultas y transacciones se implementan mediante sentencias SQL explícitas en `app/repositories/`, respetando la restricción de la cátedra y manteniendo control total sobre `JOIN`, bloqueos y restricciones de integridad[cite: 3, 42].
* **Prevención de sobreventa en doble capa:** La disponibilidad de butacas se valida en el servicio de compras y se resguarda a nivel de motor mediante la restricción `UNIQUE (id_funcion, id_asiento)` en `entradas`, acompañada por bloqueos temporales en `bloqueos_asientos` y limpieza automática cada 1 segundo mediante el *Event Scheduler* de MySQL[cite: 42, 55].
* **Normalización temporal unificada (`DATETIME`):** Las fechas y horarios de funciones se almacenan en un único campo `DATETIME` normalizado a hora local de Argentina (`UTC-3`), validando antisolapamiento por sala según la duración de cada película[cite: 27, 38, 55].
* **Envío de comprobantes desacoplado de la confirmación:** El correo electrónico con el QR en PNG adjunto se despacha después de confirmar la compra en base de datos, evitando revertir operaciones válidas ante eventuales demoras de red con el proveedor de correo[cite: 32, 40].
