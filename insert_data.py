"""
Script para insertar datos de ejemplo en la base de datos
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Datos de ejemplo
personal_data = [
    ("María García López", "V-12.345.678", "CI-001", "+58 414 123 4567", "Cardiología"),
    ("Carlos Rodríguez Pérez", "V-23.456.789", "CI-002", "+58 424 234 5678", "Emergencias"),
    ("Ana Martínez Blanco", "V-34.567.890", "CI-003", "+58 412 345 6789", "Pediatría"),
    ("José Fernández Ruiz", "V-45.678.901", "CI-004", "+58 426 456 7890", "Traumatología"),
    ("Laura Sánchez Morales", "V-56.789.012", "CI-005", "+58 414 567 8901", "Laboratorio"),
    ("Pedro Díaz Castro", "V-67.890.123", "CI-006", "+58 424 678 9012", "Radiología"),
    ("Carmen López Herrera", "V-78.901.234", "CI-007", "+58 412 789 0123", "Cardiología"),
    ("Miguel Torres Vega", "V-89.012.345", "CI-008", "+58 426 890 1234", "Emergencias"),
]

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    for person in personal_data:
        cursor.execute("""
            INSERT INTO personal (nombre, cedula, ci_carnet, telefono, area)
            VALUES (%s, %s, %s, %s, %s)
        """, person)
    
    conn.commit()
    print(f"✅ Se insertaron {len(personal_data)} registros exitosamente")

    # Verificar
    cursor.execute("SELECT COUNT(*) FROM personal")
    count = cursor.fetchone()[0]
    print(f"📊 Total de registros en la tabla: {count}")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()
