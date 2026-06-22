# Repositorio-Grupo-1


# TP-FinalBDA

Sistema base de seguimiento de hábitos bajo paradigma FARM:

- **Backend**: FastAPI + MongoDB (driver nativo `motor`/`pymongo`, sin ODM).
- **Frontend**: React (componente dashboard en `frontend/src/Dashboard.jsx`).
- **Resiliencia**: backup/restore con `mongodump` y `mongorestore` vía `subprocess`.

---

## 1) Requisitos previos

Instala en tu máquina:

- **Python 3.11+**
- **Node.js 20+** y **npm** (para frontend React/Vite)
- **MongoDB** (local o Atlas)
- **MongoDB Database Tools** (`mongodump`, `mongorestore`)
- **Git**

Verificación rápida:

```bash
python --version
node --version
npm --version
mongodump --version
mongorestore --version
```

---

## 2) Clonar y entrar al proyecto

```bash
git clone https://github.com/Juanpa1911/TP-FinalBDA.git
cd TP-FinalBDA
```

---

## 3) Levantar MongoDB con Docker (recomendado para local)

1. Copia el archivo de ejemplo:

```bash
copy .env.example .env  # Windows PowerShell
# cp .env.example .env  # Linux/macOS
```

2. Levanta MongoDB y el panel web:

```bash
docker compose up -d
```

- MongoDB queda en `mongodb://localhost:27017`
- Mongo Express queda en `http://localhost:8081`
- La primera vez se crean colecciones, índices y seeds desde `mongo-init/01-init.js`

Para detener:

```bash
docker compose down
```

---

## 4) Crear entorno virtual e instalar paquetería backend

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt
```

Paquetes Python usados:

- `fastapi`
- `uvicorn`
- `motor`
- `pymongo`
- `python-dotenv`

---

## 5) Configurar variables de entorno

Copia `.env.example` a `.env` y ajusta según el entorno:

```env
DB_USER=habits_app
DB_PASS=habits_app
DB_HOST=localhost:27017
DB_NAME=habits_db
DB_PROTOCOL=mongodb
DB_DIRECT_CONNECTION=true
MONGODB_URI=mongodb://habits_app:habits_app@localhost:27017/habits_db?retryWrites=true&w=majority
CORS_ORIGINS=http://localhost:5173

MONGO_ROOT_USER=mongo_root
MONGO_ROOT_PASS=mongo_root
MONGO_EXPRESS_USER=admin
MONGO_EXPRESS_PASS=admin
```

> `.env` está ignorado por Git para proteger credenciales.
> Para Atlas, ajusta `DB_PROTOCOL=mongodb+srv`, `DB_HOST=tu_cluster.mongodb.net` y `MONGODB_URI` con tu usuario real.
> Usa `DB_DIRECT_CONNECTION=true` si tu instancia local expone un replica set con hostnames internos.

---

## 6) Levantar backend FastAPI

```bash
uvicorn main:app --reload
```

Prueba de salud:

```bash
curl http://127.0.0.1:8000/health
```

Endpoint principal de hábitos:

- `GET  /api/habits`
- `POST /api/habits`

Ejemplo POST:

```bash
curl -X POST http://127.0.0.1:8000/api/habits \
  -H "Content-Type: application/json" \
  -d '{"name":"Leer 10 páginas","frequency":"daily","status":"active"}'
```

---

## 7) Frontend (React + Vite)

Este repositorio incluye el componente dashboard en:

- `frontend/src/Dashboard.jsx`

Si aún no tienes un proyecto Vite creado en `frontend/`, puedes inicializarlo:

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm run dev
```

Luego integra/reemplaza el componente `src/Dashboard.jsx` con el de este repositorio.

---

## 8) Backup y restore de base de datos

Script disponible:

- `scripts/backup_manager.py`

Comandos:

```bash
python scripts/backup_manager.py backup --archive dump.agz
python scripts/backup_manager.py restore --archive dump.agz
```

`restore` usa `--drop` para restauración limpia.

---

## 9) Tests automáticos

Se agregó una batería inicial con `unittest` en `tests/`:

- validación de modelos Pydantic (`extra='forbid'`, alias `_id`, estado)
- construcción de URI de conexión MongoDB
- backup/restore (verificación de argumentos de `subprocess.run`)
- endpoint `/health`

Ejecutar todos:

```bash
python -m unittest discover -s tests -v
```

Ejecutar un archivo específico:

```bash
python -m unittest tests/test_models.py -v
```

---

## 10) Comandos útiles de desarrollo

```bash
# validar sintaxis Python
python -m compileall main.py app scripts tests

# ver estado de cambios
git status

# ver dependencias instaladas
pip list
```

---

## 11) Estructura de la Base de Datos MongoDB

### Visión General

La base de datos `habits_db` utiliza un modelo de documento flexible sin ODM, permitiendo iteración rápida sobre el esquema. Se compone de tres colecciones principales:

### Collection: `habits`

Almacena los hábitos creados por los usuarios.

**Estructura de documento:**

```json
{
  "_id": ObjectId("6a1c701d8e34f049139df8a5"),
  "name": "Leer 10 páginas",
  "frequency": "daily",
  "status": "active",
  "user_id": "demo_user",
  "date": ISODate("2026-05-31T17:30:05.068Z")
}
```

**Campos:**

| Campo       | Tipo     | Descripción                                                     | Requerido              |
| ----------- | -------- | --------------------------------------------------------------- | ---------------------- |
| `_id`       | ObjectId | Identificador único de MongoDB                                  | Sí (auto)              |
| `name`      | String   | Nombre del hábito (1-120 caracteres)                            | Sí                     |
| `frequency` | String   | Frecuencia del hábito (1-60 caracteres, ej: "daily", "3x/week") | Sí                     |
| `status`    | String   | Estado del hábito ("active" \| "archived")                      | Sí (default: "active") |
| `user_id`   | String   | ID del usuario que creó el hábito (opcional)                    | No                     |
| `date`      | Date     | Timestamp UTC de creación                                       | Sí (auto)              |

**Índices:**

1. **Índice compuesto en `user_id` y `date`:**

   ```javascript
   db.habits.createIndex({ user_id: 1, date: -1 });
   ```

   - **Propósito**: Optimizar consultas que filtran por usuario y ordenan por fecha
   - **Caso de uso**: Panel de dashboard de cada usuario
   - **Impacto**: Reduce tiempo de búsqueda O(n) a O(log n) para usuarios con muchos hábitos

2. **Índice parcial en `name` (solo hábitos activos):**
   ```javascript
   db.habits.createIndex(
     { name: 1 },
     { partialFilterExpression: { status: "active" } },
   );
   ```

   - **Propósito**: Búsqueda rápida de hábitos activos por nombre (case-sensitive)
   - **Caso de uso**: Autocompletar en formularios
   - **Ventaja**: Índice más pequeño que uno sin filtro; archivos archivados no consumen espacio de índice
   - **Impacto**: Reduce consumo de memoria en índices

### Collection: `users`

Almacena información de usuario (estructura predefinida para futuras expansiones).

**Estructura de documento:**

```json
{
  "_id": ObjectId("user_1"),
  "username": "demo_user",
  "created_at": ISODate("2026-05-31T17:30:05.068Z")
}
```

### Collection: `ephemeral_events`

Almacena eventos temporales (sesiones, notificaciones) con auto-expiración.

**Estructura de documento:**

```json
{
  "_id": ObjectId("event_1"),
  "event_type": "session_login",
  "user_id": "demo_user",
  "data": { "ip": "127.0.0.1" },
  "created_at": ISODate("2026-06-01T00:00:00.000Z")
}
```

**Índices:**

1. **Índice TTL (Time-To-Live) en `created_at`:**
   ```javascript
   db.ephemeral_events.createIndex(
     { created_at: 1 },
     { expireAfterSeconds: 86400 },
   );
   ```

   - **Propósito**: Eliminación automática de documentos después de 24 horas
   - **Caso de uso**: Limpiar eventos antiguos sin intervención manual
   - **Impacto**: MongoDB ejecuta un background thread que elimina documentos expirados cada 60 segundos

---

## 12) Pruebas y Demostración de Índices

Este proyecto fue diseñado para demostrar cómo los índices impactan el rendimiento y la seguridad en MongoDB. A continuación se incluyen consultas, casos de uso y análisis de impacto.

### 12.1) Conexión a la base de datos desde Mongo Express

1. Accede a `http://localhost:8081` (credenciales por defecto: `admin/admin`)
2. Selecciona la base de datos `habits_db`
3. Explora las collections y datos

### 12.2) Consultas de demostración (Mongo Shell)

Accede al shell:

```bash
docker exec -it habits_mongo mongosh -u mongo_root -p mongo_root --authenticationDatabase admin
```

Luego dentro del shell:

```javascript
// Seleccionar la base de datos
use habits_db

// ============ CONSULTAS BÁSICAS ============

// 1. Listar todos los hábitos
db.habits.find()

// 2. Listar hábitos activos de un usuario
db.habits.find({ user_id: "demo_user", status: "active" })

// 3. Listar hábitos archivados
db.habits.find({ status: "archived" })

// 4. Búsqueda por nombre (case-sensitive, sin índice es lento con muchos datos)
db.habits.find({ name: "Leer 10 páginas" })

// 5. Búsqueda por nombre (case-insensitive con regex)
db.habits.find({ name: { $regex: "leer", $options: "i" } })

// 6. Contar hábitos activos
db.habits.countDocuments({ status: "active" })

// 7. Listar hábitos ordenados por fecha descendente
db.habits.find().sort({ date: -1 }).limit(5)
```

### 12.3) Análisis de rendimiento con `explain()`

Para ver si una consulta usa índice:

```javascript
// Sin índice (recolección completa)
db.habits.find({ name: "Leer 10 páginas" }).explain("executionStats");

// Con índice compuesto
db.habits
  .find({ user_id: "demo_user", status: "active" })
  .sort({ date: -1 })
  .explain("executionStats");
```

Busca en el resultado:

- **`executionStages.stage: "COLLSCAN"`** = sin índice (malo)
- **`executionStages.stage: "IXSCAN"`** = con índice (bueno)
- **`executionStats.totalDocsExamined`** vs **`executionStats.nReturned`**: si son diferentes, el índice no es selectivo

### 12.4) Casos de uso de índices: Beneficioso vs Perjudicial

#### ✅ BENEFICIOSO: Índice compuesto en `user_id, date DESC`

**Escenario:**

- 1 millón de hábitos
- Muchos usuarios consultando sus datos regularmente

**Consulta:**

```javascript
db.habits.find({ user_id: "user_123" }).sort({ date: -1 });
```

**Sin índice:**

- Recorre todos los 1M de documentos
- Ordena en memoria
- ~500ms en hardware moderno

**Con índice:**

- Accede directo a ~500 documentos del usuario
- Ya está ordenado
- ~10ms

**Beneficio:** 50x más rápido ✅

---

#### ⚠️ PERJUDICIAL: Índice en campo con baja cardinalidad

**Escenario:**

- Colección `habits` con 1 millón de documentos
- Campo `status` solo tiene 2 valores: "active" (80%) y "archived" (20%)

**Índice malo:**

```javascript
db.habits.createIndex({ status: 1 });
```

**Problema:**

- MongoDB necesita examinar 800k documentos "active" de todas formas
- El índice consume memoria pero no reduce búsqueda significativamente
- Ralentiza inserciones (overhead de mantener índice)

**Solución:** Usar índice parcial:

```javascript
db.habits.createIndex(
  { status: 1 },
  { partialFilterExpression: { status: "active" } },
);
```

Resultado: índice 80% más pequeño, misma velocidad ✅

---

#### ⚠️ PERJUDICIAL: Índice en columna frecuentemente actualizada

**Escenario:**

```javascript
db.metrics.createIndex({ counter: 1 });
```

Cada actualización:

```javascript
db.metrics.updateOne({ _id: 1 }, { $inc: { counter: 1 } });
```

**Problema:**

- Cada incremento requiere actualizar el índice
- Con 10k inserciones/seg, índice se convierte en cuello de botella
- CPU dedicado a mantener estructura de árbol B

**Solución:** Para contadores muy frecuentes, usar colección separada o `$inc` sin índice ✅

---

### 12.5) Comandos para crear/eliminar índices en demostración

```javascript
// Ver todos los índices de la colección
db.habits.getIndexes();

// Crear índice compuesto (ya existe en init script, pero para demo)
db.habits.createIndex({ user_id: 1, date: -1 });

// Crear índice parcial
db.habits.createIndex(
  { name: 1 },
  { partialFilterExpression: { status: "active" } },
);

// Crear índice con opciones de background (no bloquea lecturas/escrituras)
db.habits.createIndex({ frequency: 1 }, { background: true });

// Eliminar un índice
db.habits.dropIndex("user_id_1_date_-1");

// Eliminar todos los índices (excepto _id)
db.habits.dropIndexes();

// Reconstruir índices (útil después de muchas deletes)
db.habits.reIndex();
```

### 12.6) Estadísticas de colección

```javascript
// Tamaño total de la colección
db.habits.stats();

// Tamaño de índices
db.habits.stats().indexSizes;

// Información de documentos
db.habits.countDocuments();
```

### 12.7) Testing desde la API

El panel de admin en la UI del frontend (`http://localhost:5173`) incluye:

1. **Búsqueda y filtros**: Prueba `GET /api/admin/habits?search=Leer&status=active`
2. **Paginación**: Prueba `GET /api/admin/habits?skip=0&limit=10`
3. **Filtro por usuario**: Prueba `GET /api/admin/habits?user_id=demo_user`

Todos estos endpoints usan índices para optimizar consultas.

### 12.8) Generación de datos para testing (opcional)

Para llenar la base de datos con datos de prueba:

```javascript
// Insertar 1000 hábitos ficticios
const users = ["user_1", "user_2", "user_3", "user_4", "user_5"];
const frequencies = ["daily", "3x/week", "weekly", "bi-weekly", "monthly"];

for (let i = 0; i < 1000; i++) {
  db.habits.insertOne({
    name: `Test Habit ${i}`,
    frequency: frequencies[Math.floor(Math.random() * frequencies.length)],
    status: Math.random() > 0.2 ? "active" : "archived",
    user_id: users[Math.floor(Math.random() * users.length)],
    date: new Date(),
  });
}
```

---

## 13) Seguridad

### Validación de entrada

- **Pydantic `ConfigDict(extra='forbid')`**: Rechaza campos desconocidos (protege contra inyección)
- **`StrictStr` con `min_length` y `max_length`**: Valida tipos y longitud
- **Regex en búsqueda**: `$regex` con `$options: "i"` es seguro contra injection

### Credenciales

- `.env` está en `.gitignore`
- Credenciales MongoDB: usuario con permisos limitados en la BD específica
- CORS habilitado solo para `http://localhost:5173` (cambiar en producción)

### Respaldos

- `mongodump` y `mongorestore` usan credenciales de `.env`
- Backups se guardan en `backups/` (agregar a `.gitignore` en producción)

---

## 14) Estructura de carpetas

```
TP-FinalBDA/
├── main.py                     # Punto de entrada FastAPI
├── requirements.txt            # Dependencias Python
├── docker-compose.yml          # Configuración Docker (MongoDB + Mongo Express)
├── .env.example                # Plantilla de variables de entorno
├── .gitignore                  # Archivos a ignorar en Git
│
├── app/
│   ├── __init__.py
│   ├── config.py               # Configuración de la app
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connector.py        # Conexión a MongoDB
│   │   └── init_db.py          # Inicialización de índices
│   ├── models/
│   │   ├── __init__.py
│   │   ├── habit.py            # Esquema Pydantic de Habit
│   │   └── user.py             # Esquema Pydantic de User
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── habits.py           # Endpoints CRUD de hábitos
│   │   ├── users.py            # Endpoints de usuarios
│   │   └── admin.py            # Endpoints de admin (filtros, backup)
│   └── services/
│       ├── __init__.py
│       └── habit_manager.py    # Lógica de negocio de hábitos
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.jsx            # Punto de entrada React
│   │   ├── App.jsx             # Componente Dashboard
│   │   ├── Admin.jsx           # Componente Admin (nuevo)
│   │   ├── App.css             # Estilos
│   │   └── index.css           # Estilos globales
│   ├── package.json
│   └── vite.config.js
│
├── scripts/
│   └── backup_manager.py       # Script para backup/restore manual
│
├── tests/
│   ├── test_models.py          # Tests de validación Pydantic
│   ├── test_connection.py      # Tests de conexión MongoDB
│   └── test_backup.py          # Tests de backup/restore
│
├── mongo-init/
│   └── 01-init.js              # Script de inicialización MongoDB
│
└── README.md                   # Este archivo
```