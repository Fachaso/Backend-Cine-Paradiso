import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Establece y retorna una conexión nativa a la base de datos MySQL.
    Asegura el uso de cursor de diccionario sin ORM según los requisitos.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "cine_paradiso"),
            charset="utf8mb4"
        )
        return connection
    except Error as e:
        print(f"Error de conexión a MySQL: {e}")
        raise e

def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Función auxiliar para ejecutar consultas SQL puras con cursor de diccionario.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        # Cursor de diccionario para mapear columnas a claves JSON automáticamente
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
            
        if commit:
            conn.commit()
            result = cursor.lastrowid or True
            
        return result
    except Error as e:
        if conn and commit:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
