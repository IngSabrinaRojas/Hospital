"""
Verificar estructura de la tabla profesion y relación con persona
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Ver columnas de profesion
    print("📋 COLUMNAS DE LA TABLA 'profesion':")
    print("-" * 60)
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'profesion'
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]:25s} | {col[1]}")

    # Ver todos los registros de profesion
    print("\n📋 REGISTROS DE LA TABLA 'profesion':")
    print("-" * 60)
    cursor.execute("SELECT * FROM profesion")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # Contar personas por cargo
    print("\n📊 CONTEO POR CARGO:")
    print("-" * 60)
    cursor.execute("""
        SELECT p.cargo_per, COUNT(*) as cantidad
        FROM persona pe
        JOIN profesion p ON pe.id_pro = p.id_pro
        GROUP BY p.cargo_per
        ORDER BY cantidad DESC
    """)
    counts = cursor.fetchall()
    for row in counts:
        print(f"  {row[0]}: {row[1]} personas")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()