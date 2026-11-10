<div align="right">
    <img width="32px" src="img/logo_intro.desarrollo.software.png">
</div>

# Proyecto Integrador - Sistema de venta de entradas de cine

## 🔗 Estructura del Proyecto
Este sistema de venta de entradas está compuesto por dos repositorios complementarios:

*   **[Backend (API REST)](https://github.com/Fachaso/Backend-Cine-Paradiso):** Desarrollado en Flask, maneja la lógica de negocio, la conexión a la base de datos MySQL, el sistema de estadísticas y la seguridad de los endpoints.
*   **[Frontend (Interfaz de Usuario)](https://github.com/lutzio07/Front---Cine-Paradiso):** Contiene tanto la aplicación web de acceso para los usuarios finales como el backoffice para que los administradores configuren las salas y películas.

## Información de los estudiantes:

* Ramiro Tomas Martinez - 115961 - rtmartinez@fi.uba.ar - https://github.com/Fachaso
* Juan Francisco Misiac - 116102 - jmisiac@fi.uba.ar
* Eliel Jone Castillo - 116526 - ejone@fi.uba.ar
* Lucas Nahuel Uran -116478 - luran@fi.uba.ar
* Matias Ezequiel Montiel - 116556 -memontiel@fi.uba.ar
* Joaquín Transillo - 116250- jtransillo@fi.uba.ar
* Jorge Félix García Sánchez - 116133 - jfgarcias@fi.uba.ar
* Diego Oliver Yujra Cossio - 116532 - dyujra@fi.uba.ar
* Maximiliano Alexis Silva - 115666 - masilva@fi.uba.ar
* Lucio Valentín Villagra - 116288 - lvillagra@fi.uba.ar
---

## Versiones utilizadas 
* Python 3.10 o superior
* Flask 
* MySQL 
* 

## Principales decisiones de diseño

## Dificultades encontradas 

## Conclusiones

## Ejecución 

## Configuración

## Índice
* [0. Enunciado](#0-Enunciado)
* [1. Instrucciones](#1-Instrucciones)
* [2. Funcionamiento](#2-Funcionamiento)
* [3. Estructura](#3-Estructura)
* [4. Decisiones de diseño y/o complejidades de implementación](#4-Decisiones-de-diseño-yo-complejidades-de-implementación)


## 0. Enunciado



## 1. Instrucciones
### 1.1. Compilación

### 1.2. Para ejecutar


## 2. Funcionamiento


## 3. Estructura

### 3. Estructura

```text
Backend Cine-Paradiso/
├── app/
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── compras_controller.py
│   │   ├── estadisticas_controller.py
│   │   ├── funcion_controller.py
│   │   ├── pelicula_controller.py
│   │   ├── perfil_controller.py
│   │   ├── servicio_controller.py
│   │   └── sucursal_controller.py
│   ├── repositories/
│   │   ├── asiento_repository.py
│   │   ├── compra_repository.py
│   │   ├── db_connection.py
│   │   ├── estadisticas_repository.py
│   │   ├── funcion_repository.py
│   │   ├── incidencia_repository.py
│   │   ├── pelicula_repository.py
│   │   ├── perfil_repository.py
│   │   ├── producto_repository.py
│   │   ├── servicio_repository.py
│   │   ├── sucursal_repository.py
│   │   └── usuario_repository.py
│   ├── routes/
│   │   ├── admin_routes.py
│   │   ├── auth_routes.py
│   │   ├── candybar_routes.py
│   │   ├── compras_routes.py
│   │   ├── control_acceso_routes.py
│   │   ├── estadisticas_routes.py
│   │   ├── funciones_routes.py
│   │   ├── peliculas_routes.py
│   │   ├── perfil_routes.py
│   │   ├── servicios_routes.py
│   │   └── sucursales_routes.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── candybar_service.py
│   │   ├── compras_service.py
│   │   ├── control_acceso_service.py
│   │   ├── email_service.py
│   │   ├── estadisticas_service.py
│   │   ├── funciones_service.py
│   │   ├── peliculas_service.py
│   │   ├── perfil_service.py
│   │   ├── servicio_service.py
│   │   ├── sucursal_service.py
│   │   └── tmdb_service.py
│   ├── utils/
│   │   └── auth.py
│   └── validators/
│       ├── compra_validator.py
│       ├── funcion_validator.py
│       ├── pelicula_validator.py
│       ├── servicio_validator.py
│       └── sucursal_validator.py
├── database/
├── .env.example
├── .gitignore
├── app.py
├── Enunciado.md
├── init.sh
├── README.md
├── requirements.txt
└── swagger.yaml
```
