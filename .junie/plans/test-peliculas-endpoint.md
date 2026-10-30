---
sessionId: session-261030-002337-123c
---

# Testing Guide

### Overview
This plan provides a step-by-step guide for the user to test the `GET /api/peliculas` endpoint that was implemented during the session. The endpoint supports pagination (`pagina`, `limite`) and dynamic filters (`genero`, `estado`, `buscar`) using pure SQL queries.

### Prerequisites
- MySQL server running with the `cine_paradiso` database
- Python 3 with Flask and dependencies installed (`requirements.txt`)
- The `.env` file configured with database credentials

### Test Steps

#### Step 1: Load the database schema
```bash
mysql -u root -p < database/schema.sql
```

Then insert test data:
```sql
USE cine_paradiso;

INSERT INTO peliculas (titulo, sinopsis, poster_url, genero, duracion_min, clasificacion, estado) VALUES
('Gladiator', 'Un general romano busca venganza.', 'https://example.com/gladiator.jpg', 'Acción', 155, '+16', 'ACTIVO'),
('Inception', 'Sueños dentro de sueños.', 'https://example.com/inception.jpg', 'Ciencia Ficción', 148, '+13', 'ACTIVO'),
('The Shawshank Redemption', 'Dos prisioneros forjan una amistad.', 'https://example.com/shawshank.jpg', 'Drama', 142, '+18', 'ACTIVO'),
('Titanic', 'Un barco, un amor trágico.', 'https://example.com/titanic.jpg', 'Drama', 194, '+13', 'INACTIVO');
```

#### Step 2: Verify `.env` configuration
Ensure `app/repositories/db_connection.py` can connect to MySQL. Check `.env` contains:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=cine_paradiso
```

#### Step 3: Start the Flask application
```bash
python3 run.py
```

#### Step 4: Test with curl

**All active movies (page 1):**
```bash
curl http://localhost:5000/api/peliculas
```

**Filter by genre:**
```bash
curl "http://localhost:5000/api/peliculas?genero=Drama"
```

**Search by title:**
```bash
curl "http://localhost:5000/api/peliculas?buscar=Gladiator"
```

**Page 2, 1 per page:**
```bash
curl "http://localhost:5000/api/peliculas?pagina=2&limite=1"
```

**Include inactive movies:**
```bash
curl "http://localhost:5000/api/peliculas?estado=INACTIVO"
```

**Combine filters:**
```bash
curl "http://localhost:5000/api/peliculas?genero=Drama&buscar=love&pagina=1&limite=5"
```

#### Step 5: Verify response format
Each response should include:
- `status`: "success"
- `data`: array of movie objects
- `pagination`: object with `pagina`, `limite`, `total`, `total_paginas`

### Troubleshooting
- **MySQL connection error**: Verify MySQL is running and `.env` credentials are correct
- **500 error**: Check Flask terminal for traceback
- **Empty results**: Ensure test data was inserted

# Delivery Steps

###   Step 1: Setup database and test data
Load the database schema and insert test movie data for testing the endpoint.

### * Step 2: Start Flask app and test endpoint
Start the Flask application and test the GET /api/peliculas endpoint with various curl commands to verify pagination and filtering work correctly.