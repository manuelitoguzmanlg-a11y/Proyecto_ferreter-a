import mysql.connector
from mysql.connector import Error
from datetime import datetime, timezone, timedelta


# ==================================
# ZONA HORARIA DE EL SALVADOR
# ==================================

ZONA_EL_SALVADOR = timezone(timedelta(hours=-6))


def obtener_fecha_hora_el_salvador():
    """
    Devuelve la fecha y hora actual de El Salvador
    en formato compatible con MySQL.
    """
    return datetime.now(ZONA_EL_SALVADOR).strftime("%Y-%m-%d %H:%M:%S")


def obtener_fecha_el_salvador():
    """
    Devuelve solo la fecha actual de El Salvador.
    """
    return datetime.now(ZONA_EL_SALVADOR).strftime("%Y-%m-%d")


def obtener_hora_el_salvador():
    """
    Devuelve solo la hora actual de El Salvador.
    """
    return datetime.now(ZONA_EL_SALVADOR).strftime("%H:%M:%S")


# ==================================
# CONEXIÓN A MYSQL CLEVER CLOUD
# ==================================

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="bemxvjgccuq9ohhqqoon-mysql.services.clever-cloud.com",
            user="uqgwgiv9dbanrjai",
            password="Ji6Id6MlpELTj1Tl9auU",
            database="bemxvjgccuq9ohhqqoon",
            port=3306
        )

        if conexion.is_connected():
            print("✅ Conexión establecida")

            # Configura la zona horaria de la sesión MySQL a El Salvador
            cursor = conexion.cursor()
            cursor.execute("SET time_zone = '-06:00'")
            cursor.close()

            return conexion

        else:
            print("❌ Conexión fallida")
            return None

    except Error as e:
        print(f"❌ Error al conectar: {e}")
        return None


# ==================================
# ALIAS POR SI OTROS ARCHIVOS LO USAN
# ==================================

def conectar():
    return obtener_conexion()


def crear_conexion():
    return obtener_conexion()


def cerrar_conexion(conexion):
    if conexion is not None and conexion.is_connected():
        conexion.close()
