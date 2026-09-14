"""
Verificar especialidades y cargos para las gráficas
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Conteo por cargo (para gráfico de torta)
    print("📊 POR CARGO (Gráfico de Torta):")
    print("-" * 50)
    cursor.execute("""
        SELECT p.cargo_per, COUNT(*) as cantidad
        FROM persona pe
        JOIN profesion p ON pe.id_pro = p.id_pro
        GROUP BY p.cargo_per
        ORDER BY cantidad DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Conteo por especialidad (para gráfico de barras)
    print("\n📊 POR ESPECIALIDAD (Gráfico de Barras):")
    print("-" * 50)
    cursor.execute("""
        SELECT p.especialidad_per, COUNT(*) as cantidad
        FROM persona pe
        JOIN profesion p ON pe.id_pro = p.id_pro
        GROUP BY p.especialidad_per
        ORDER BY cantidad DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()