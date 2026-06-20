from modulos.config.conexion import obtener_conexion, obtener_fecha_hora_el_salvador
import streamlit as st
import hashlib


# =========================================================
# SEGURIDAD
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# =========================================================
# USUARIOS BASE
# =========================================================

USUARIOS_BASE = [
    {
        "usuario": "marvin",
        "nombre": "Marvin Ramos",
        "rol": "Administrador",
        "password": "1234"
    },
    {
        "usuario": "dayana",
        "nombre": "Dayana",
        "rol": "Administrador",
        "password": "1234"
    },
    {
        "usuario": "juanita",
        "nombre": "Juanita de Ramos",
        "rol": "Vendedor",
        "password": "1234"
    },
    {
        "usuario": "bryan",
        "nombre": "Bryan Ramos",
        "rol": "Vendedor",
        "password": "1234"
    }
]


# =========================================================
# BASE DE DATOS
# =========================================================

def asegurar_tabla_usuarios(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario_Sistema (
            Id_Usuario INT AUTO_INCREMENT PRIMARY KEY,
            Usuario VARCHAR(50) NOT NULL UNIQUE,
            Nombre VARCHAR(150) NOT NULL,
            Rol VARCHAR(50) NOT NULL,
            Password_Hash VARCHAR(255) NOT NULL,
            Activo TINYINT DEFAULT 1,
            Fecha_Registro DATETIME,
            Fecha_Modificacion DATETIME
        )
    """)


def sembrar_usuarios_iniciales(cursor, con):
    fecha = obtener_fecha_hora_el_salvador()

    for usuario in USUARIOS_BASE:
        cursor.execute("""
            SELECT COUNT(*)
            FROM Usuario_Sistema
            WHERE Usuario = %s
        """, (usuario["usuario"],))

        existe = cursor.fetchone()[0]

        if existe == 0:
            cursor.execute("""
                INSERT INTO Usuario_Sistema
                (
                    Usuario,
                    Nombre,
                    Rol,
                    Password_Hash,
                    Activo,
                    Fecha_Registro,
                    Fecha_Modificacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                usuario["usuario"],
                usuario["nombre"],
                usuario["rol"],
                hash_password(usuario["password"]),
                1,
                fecha,
                fecha
            ))

    con.commit()


def preparar_login():
    con = obtener_conexion()
    cursor = con.cursor()

    asegurar_tabla_usuarios(cursor)
    sembrar_usuarios_iniciales(cursor, con)

    cursor.close()
    con.close()


# =========================================================
# ESTILO VISUAL PREMIUM
# =========================================================

def aplicar_estilo_login():
    st.markdown("""
        <style>
            .login-wrapper {
                min-height: 70vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .login-card {
                background: linear-gradient(135deg, #070b14 0%, #111827 55%, #1f2937 100%);
                border: 1px solid #d4af37;
                border-radius: 26px;
                padding: 38px;
                margin: 30px auto 20px auto;
                max-width: 680px;
                box-shadow: 0 16px 42px rgba(0,0,0,0.55);
            }

            .login-title {
                color: #f8fafc;
                font-size: 42px;
                font-weight: 900;
                text-align: center;
                margin-bottom: 8px;
                letter-spacing: 0.4px;
            }

            .login-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                text-align: center;
                margin-bottom: 18px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #8b6f1d, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 22px 0 24px 0;
            }

            .login-info {
                background-color: #0f172a;
                border-left: 5px solid #d4af37;
                padding: 15px 20px;
                border-radius: 12px;
                color: #e5e7eb;
                margin-top: 18px;
                font-size: 15px;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# LOGIN
# =========================================================

def mostrar_login():

    aplicar_estilo_login()

    try:
        preparar_login()
    except Exception as e:
        st.error(f"❌ Error al preparar el login: {e}")
        return

    st.markdown("""
        <div class="login-card">
            <div class="login-title">🛠️ Ferretería HELOIM</div>
            <div class="login-subtitle">
                Sistema de Gestión de Información
            </div>
            <div class="gold-line"></div>
            <div class="login-info">
                Acceda con sus credenciales para ingresar al sistema según el rol asignado.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        usuario = st.text_input(
            "Usuario",
            placeholder="Ejemplo: marvin"
        )

        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Ingrese su contraseña"
        )

        ingresar = st.button(
            "🔐 Iniciar sesión",
            use_container_width=True
        )

        if ingresar:

            usuario_limpio = usuario.strip().lower()
            password_limpio = password.strip()

            if usuario_limpio == "" or password_limpio == "":
                st.warning("⚠️ Ingrese usuario y contraseña.")

            else:
                try:
                    con = obtener_conexion()
                    cursor = con.cursor()

                    cursor.execute("""
                        SELECT
                            Usuario,
                            Nombre,
                            Rol,
                            Password_Hash,
                            Activo
                        FROM Usuario_Sistema
                        WHERE Usuario = %s
                    """, (usuario_limpio,))

                    resultado = cursor.fetchone()

                    cursor.close()
                    con.close()

                    if resultado is None:
                        st.error("❌ Usuario no registrado.")

                    else:
                        usuario_db = resultado[0]
                        nombre_db = resultado[1]
                        rol_db = resultado[2]
                        password_hash_db = resultado[3]
                        activo_db = resultado[4]

                        if activo_db != 1:
                            st.error("❌ Este usuario está inactivo.")

                        elif hash_password(password_limpio) != password_hash_db:
                            st.error("❌ Contraseña incorrecta.")

                        else:
                            st.session_state["logueado"] = True
                            st.session_state["usuario"] = usuario_db
                            st.session_state["nombre_usuario"] = nombre_db
                            st.session_state["rol"] = rol_db

                            st.success(f"✅ Bienvenido, {nombre_db}.")
                            st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al iniciar sesión: {e}")
