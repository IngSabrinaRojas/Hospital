"""
Script para verificar los datos REALES en la base de datos Neon
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print(f"🔍 Conectando a: {DATABASE_URL[:50]}...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Listar TODAS las tablas en la base de datos
    print("\n📋 TABLAS EN LA BASE DE DATOS:")
    print("-" * 60)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Tabla: {table_name} | Registros: {count}")

    # Detalles de la tabla personal
    print("\n" + "=" * 60)
    print("📊 DETALLE DE LA TABLA 'personal':")
    print("=" * 60)
    
    cursor.execute("SELECT COUNT(*) FROM personal")
    count = cursor.fetchone()[0]
    print(f"Total de registros: {count}")

    # Mostrar todos los registros
    cursor.execute("SELECT id, nombre, cedula, ci_carnet, telefono, area FROM personal ORDER BY id")
    rows = cursor.fetchall()

    print(f"\n📋 REGISTROS (mostrando {len(rows)} de {count}):")
    print("-" * 80)
    for row in rows:
        print(f"ID: {row[0]:3d} | {row[1]:25s} | {row[2]:15s} | {row[5]}")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()
