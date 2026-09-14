"""
Backend FastAPI - Dashboard Hospital
Conexión a PostgreSQL (Neon) y API REST para el frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Cargar variables de entorno
load_dotenv()

# Configuración de la app
app = FastAPI(
    title="Dashboard Hospital API",
    description="API para gestionar datos del personal hospitalario",
    version="1.0.0"
)

# Configuración CORS - Permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo Pydantic para el Personal
class Personal(BaseModel):
    id: Optional[int] = None
    nombre: str
    cedula: str
    ci_carnet: str
    telefono: str
    area: str

# Función para obtener conexión a la base de datos
def get_db_connection():
    """
    Crea una conexión a la base de datos PostgreSQL en Neon.
    La URL de conexión se obtiene de la variable de entorno DATABASE_URL.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise HTTPException(
            status_code=500, 
            detail="DATABASE_URL no está configurada en las variables de entorno"
        )
    
    try:
        connection = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        # Configurar encoding UTF-8
        connection.set_client_encoding('UTF8')
        return connection
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al conectar con la base de datos: {str(e)}"
        )

# Endpoint raíz para mostrar el dashboard visual (index.html)
@app.get("/", response_class=HTMLResponse)
def root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <head><title>Dashboard Hospital</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                <h1>¡API de Hospital Funcionando!</h1>
                <p>Pero no se encontró el archivo <b>index.html</b> en el servidor de Render.</p>
                <p>Asegúrate de subir el archivo index.html junto con main.py a tu repositorio de GitHub.</p>
                <p><a href="/docs" style="color: blue; text-decoration: underline;">Ir a la documentación (Swagger /docs)</a></p>
            </body>
        </html>
        """, 404

# Endpoint de información alternativa por si se requiere en JSON
@app.get("/api/info")
def api_info():
    return {
        "mensaje": "API Dashboard Hospital funcionando correctamente",
        "version": "1.0.0",
        "endpoints": {
            "personal": "/api/personal",
            "personal_por_id": "/api/personal/{id}",
            "crear_personal": "/api/personal (POST)",
            "actualizar_personal": "/api/personal/{id} (PUT)",
            "eliminar_personal": "/api/personal/{id} (DELETE)"
        }
    }

# GET - Obtener todo el personal (desde tabla persona)
@app.get("/api/personal")
def get_personal():
    """
    Obtiene todos los registros de la tabla persona.
    Retorna una lista con todos los empleados incluyendo su cargo.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consultar la tabla REAL 'persona' con 80 registros y hacer JOIN con profesion
        cursor.execute("""
            SELECT 
                pe.id_per as id,
                pe.prinombre_per || ' ' || pe.segnombre_per || ' ' || pe.priapellido_per || ' ' || pe.segapellido_per as nombre,
                pe.cedula_per as cedula,
                pe.correo_per as correo,
                pe.telefono_per as telefono,
                p.cargo_per as cargo
            FROM persona pe
            JOIN profesion p ON pe.id_pro = p.id_pro
            ORDER BY pe.id_per ASC
        """)
        
        personal = cursor.fetchall()
        
        # Convertir a lista de diccionarios
        result = [dict(row) for row in personal]
        
        return {
            "success": True,
            "count": len(result),
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la consulta: {str(e)}")
    finally:
        if conn:
            conn.close()

# GET - Obtener personal por ID
@app.get("/api/personal/{personal_id}")
def get_personal_by_id(personal_id: int):
    """
    Obtiene un registro de personal por su ID.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nombre, cedula, ci_carnet, telefono, area 
            FROM personal 
            WHERE id = %s
        """, (personal_id,))
        
        personal = cursor.fetchone()
        
        if not personal:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        
        return {
            "success": True,
            "data": dict(personal)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la consulta: {str(e)}")
    finally:
        if conn:
            conn.close()

# POST - Crear nuevo personal
@app.post("/api/personal")
def create_personal(personal: Personal):
    """
    Crea un nuevo registro de personal en la base de datos.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO personal (nombre, cedula, ci_carnet, telefono, area)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nombre, cedula, ci_carnet, telefono, area
        """, (
            personal.nombre,
            personal.cedula,
            personal.ci_carnet,
            personal.telefono,
            personal.area
        ))
        
        new_personal = cursor.fetchone()
        conn.commit()
        
        return {
            "success": True,
            "message": "Personal creado exitosamente",
            "data": dict(new_personal)
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear personal: {str(e)}")
    finally:
        if conn:
            conn.close()

# PUT - Actualizar personal
@app.put("/api/personal/{personal_id}")
def update_personal(personal_id: int, personal: Personal):
    """
    Actualiza un registro de personal existente.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si existe
        cursor.execute("SELECT id FROM personal WHERE id = %s", (personal_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        
        # Actualizar
        cursor.execute("""
            UPDATE personal 
            SET nombre = %s, cedula = %s, ci_carnet = %s, telefono = %s, area = %s
            WHERE id = %s
            RETURNING id, nombre, cedula, ci_carnet, telefono, area
        """, (
            personal.nombre,
            personal.cedula,
            personal.ci_carnet,
            personal.telefono,
            personal.area,
            personal_id
        ))
        
        updated_personal = cursor.fetchone()
        conn.commit()
        
        return {
            "success": True,
            "message": "Personal actualizado exitosamente",
            "data": dict(updated_personal)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar personal: {str(e)}")
    finally:
        if conn:
            conn.close()

# DELETE - Eliminar personal
@app.delete("/api/personal/{personal_id}")
def delete_personal(personal_id: int):
    """
    Elimina un registro de personal por su ID.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si existe
        cursor.execute("SELECT id FROM personal WHERE id = %s", (personal_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        
        # Eliminar
        cursor.execute("DELETE FROM personal WHERE id = %s", (personal_id,))
        conn.commit()
        
        return {
            "success": True,
            "message": "Personal eliminado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar personal: {str(e)}")
    finally:
        if conn:
            conn.close()

# Endpoint para obtener estadísticas (útil para las métricas del dashboard)
@app.get("/api/stats")
def get_stats():
    """
    Obtiene estadísticas generales para el dashboard.
    Usa la tabla profesion para contar por cargo y especialidad.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total de personal (tabla persona)
        cursor.execute("SELECT COUNT(*) as total FROM persona")
        total_personal = cursor.fetchone()["total"]
        
        # Conteo por cargo (Médico, Enfermero/a, Personal de Apoyo)
        cursor.execute("""
            SELECT p.cargo_per, COUNT(*) as cantidad
            FROM persona pe
            JOIN profesion p ON pe.id_pro = p.id_pro
            GROUP BY p.cargo_per
            ORDER BY p.cargo_per
        """)
        por_cargo = cursor.fetchall()
        
        # Conteo por especialidad (para gráfico de barras)
        cursor.execute("""
            SELECT p.especialidad_per, COUNT(*) as cantidad
            FROM persona pe
            JOIN profesion p ON pe.id_pro = p.id_pro
            GROUP BY p.especialidad_per
            ORDER BY cantidad DESC
        """)
        por_especialidad = cursor.fetchall()
        
        # Crear diccionario con los 3 cargos específicos
        stats_cargo = {
            "Medico": 0,
            "Enfermero/a": 0,
            "Personal de Apoyo": 0
        }
        
        for row in por_cargo:
            cargo = row["cargo_per"]
            if cargo in stats_cargo:
                stats_cargo[cargo] = row["cantidad"]
        
        return {
            "success": True,
            "data": {
                "total_personal": total_personal,
                "por_cargo": stats_cargo,
                "por_especialidad": [dict(row) for row in por_especialidad]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la consulta: {str(e)}")
    finally:
        if conn:
            conn.close()

# Endpoint para crear la tabla si no existe (útil para inicializar)
@app.post("/api/init-db")
def init_db():
    """
    Crea la tabla personal si no existe.
    Útil para inicializar la base de datos.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personal (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                cedula VARCHAR(20),
                ci_carnet VARCHAR(20),
                telefono VARCHAR(20),
                area VARCHAR(50)
            )
        """)
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Tabla 'personal' creada o ya existente"
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear tabla: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
