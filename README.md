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
