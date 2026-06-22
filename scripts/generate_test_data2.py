#!/usr/bin/env python3
"""
Script para generar datos de prueba en MongoDB.

Uso:
    python scripts/generate_test_data.py --habits 1000 --users 10
    python scripts/generate_test_data.py --habits 5000 --clear  # Borra datos previos
    python scripts/generate_test_data.py --help
"""

import argparse
import os
import random
from datetime import datetime, timedelta, UTC

import pymongo
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración - Usar credenciales ROOT de MongoDB (funciona en Docker)
MONGO_USER = os.getenv("MONGO_ROOT_USER", "mongo_root")
MONGO_PASS = os.getenv("MONGO_ROOT_PASS", "mongo_root")
MONGO_HOST = os.getenv("DB_HOST", "localhost:27017")
MONGO_DB = os.getenv("DB_NAME", "habits_db")

# Conectar como admin para acceder a cualquier base de datos
MONGODB_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}/admin?authSource=admin&retryWrites=true"


def get_db_connection():
    """Conecta a MongoDB y retorna la base de datos."""
    try:
        print(f"Conectando a MongoDB...")
        print(f"  Host: {MONGO_HOST}")
        print(f"  Usuario: {MONGO_USER}")

        client = pymongo.MongoClient(
            MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Verificar conexión
        client.admin.command("ping")
        print("✅ Conectado a MongoDB\n")
        return client[MONGO_DB]
    except pymongo.errors.ConnectionFailure as e:
        print(f"❌ Error de conexión: {e}")
        print(f"   Verifica que MongoDB está corriendo: docker compose up -d")
        exit(1)
    except pymongo.errors.OperationFailure as e:
        print(f"❌ Error de autenticación: {e}")
        print(f"   Verifica MONGO_ROOT_USER y MONGO_ROOT_PASS en .env")
        print(f"   Usuario actual: {MONGO_USER}")
        print(f"   Contraseña: {MONGO_PASS}")
        exit(1)


def generate_test_users(db, num_users):
    """Genera usuarios de prueba."""
    print(f"📝 Generando {num_users} usuarios de prueba...")

    users = []
    for i in range(1, num_users + 1):
        user = {
            "_id": f"test_user_{i}",
            "username": f"test_user_{i}",
            "email": f"user{i}@example.com",
            "created_at": datetime.now(UTC) - timedelta(days=random.randint(1, 365)),
        }
        users.append(user)

    # Insertar con replace para evitar duplicados
    for user in users:
        db.users.update_one({"_id": user["_id"]}, {"$set": user}, upsert=True)

    print(f"✅ {num_users} usuarios generados")
    return [user["_id"] for user in users]


def generate_test_habits(db, num_habits, user_ids):
    """Genera hábitos de prueba."""
    print(f"\n📚 Generando {num_habits} hábitos de prueba...")

    # Datos para generar hábitos realistas
    habit_templates = [
        ("Leer", "daily"),
        ("Hacer ejercicio", "3x/week"),
        ("Meditar", "daily"),
        ("Escribir en diario", "daily"),
        ("Aprender idioma", "daily"),
        ("Cocinar saludable", "3x/week"),
        ("Caminar", "daily"),
        ("Programar", "daily"),
        ("Estudiar", "5x/week"),
        ("Dormir 8 horas", "daily"),
        ("Beber agua", "daily"),
        ("Hacer yoga", "3x/week"),
        ("Limpiar casa", "weekly"),
        ("Llamar familia", "weekly"),
        ("Descansar", "weekly"),
        ("Revisar finanzas", "weekly"),
        ("Proyectos personales", "3x/week"),
        ("Networking", "2x/week"),
        ("Practicar música", "3x/week"),
        ("Fotografía", "weekly"),
    ]

    frequencies = [
        "daily", "2x/week", "3x/week", "4x/week", "5x/week", "weekly",
        "bi-weekly", "monthly"
    ]

    habits = []
    base_date = datetime.now(UTC) - timedelta(days=365)

    for i in range(num_habits):
        habit_name, _ = random.choice(habit_templates)
        habit = {
            "name": f"{habit_name} #{i+1}",
            "frequency": random.choice(frequencies),
            "status": random.choices(["active", "archived"], weights=[80, 20])[0],
            "user_id": random.choice(user_ids),
            "date": base_date + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            ),
        }
        habits.append(habit)

    # Insertar en lotes para mejor rendimiento
    batch_size = 1000
    for i in range(0, len(habits), batch_size):
        batch = habits[i: i + batch_size]
        db.habits.insert_many(batch, ordered=False)
        print(
            f"   ✓ Insertados {min(i + batch_size, len(habits))}/{num_habits} hábitos")

    print(f"✅ {num_habits} hábitos generados")


def show_statistics(db):
    """Muestra estadísticas de la base de datos."""
    print("\n📊 Estadísticas:")

    users_count = db.users.count_documents({})
    habits_count = db.habits.count_documents({})
    active_count = db.habits.count_documents({"status": "active"})
    archived_count = db.habits.count_documents({"status": "archived"})

    print(f"   • Usuarios: {users_count}")
    print(f"   • Hábitos totales: {habits_count}")
    print(f"   • Hábitos activos: {active_count}")
    print(f"   • Hábitos archivados: {archived_count}")

    # Hábitos por usuario
    pipeline = [
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
    ]
    top_users = list(db.habits.aggregate(pipeline))

    if top_users:
        print(f"\n   Top 5 usuarios con más hábitos:")
        for user_data in top_users:
            print(f"      - {user_data['_id']}: {user_data['count']} hábitos")


def clear_data(db):
    """Elimina todos los datos de prueba."""
    print("\n🗑️  Eliminando datos previos...")
    db.habits.drop()
    db.users.drop()
    print("✅ Datos eliminados")


def main():
    parser = argparse.ArgumentParser(
        description="Generador de datos de prueba para MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/generate_test_data.py --habits 1000 --users 10
  python scripts/generate_test_data.py --habits 5000 --clear
  python scripts/generate_test_data.py --show-stats
        """,
    )

    parser.add_argument(
        "--habits",
        type=int,
        default=0,
        help="Cantidad de hábitos a generar (default: 0)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=5,
        help="Cantidad de usuarios a generar (default: 5)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Borra todos los datos antes de generar nuevos",
    )
    parser.add_argument(
        "--show-stats",
        action="store_true",
        help="Muestra estadísticas de la base de datos sin generar datos",
    )

    args = parser.parse_args()

    # Conectar a BD
    db = get_db_connection()

    # Si solo quiere ver estadísticas
    if args.show_stats:
        show_statistics(db)
        return

    # Si no especifica hábitos ni usuarios
    if args.habits == 0 and not args.show_stats:
        parser.print_help()
        print("\n⚠️  Debes especificar --habits o --show-stats")
        return

    # Limpiar datos si se especifica
    if args.clear:
        clear_data(db)

    # Generar usuarios
    if args.users > 0:
        user_ids = generate_test_users(db, args.users)
    else:
        # Si no se especifican usuarios, usar los existentes
        user_ids = [doc["_id"] for doc in db.users.find({}, {"_id": 1})]
        if not user_ids:
            print("❌ No hay usuarios en la BD. Usa --users para crear algunos.")
            return

    # Generar hábitos
    if args.habits > 0:
        generate_test_habits(db, args.habits, user_ids)

    # Mostrar estadísticas finales
    show_statistics(db)

    print("\n✅ Generación completada")


if __name__ == "__main__":
    main()
