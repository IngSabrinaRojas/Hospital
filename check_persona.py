"""
Verificar estructura de la tabla persona
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Ver columnas de la tabla persona
    print("📋 COLUMNAS DE LA TABLA 'persona':")
    print("-" * 60)
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'persona'
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]:25s} | {col[1]}")

    # Mostrar primeros 5 registros
    print("\n📋 PRIMEROS 5 REGISTROS:")
    print("-" * 60)
    cursor.execute("SELECT * FROM persona LIMIT 5")
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    print(f"Columnas: {col_names}")
    for row in rows:
        print(row)

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()
