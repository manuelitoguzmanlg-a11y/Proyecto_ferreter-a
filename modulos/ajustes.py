from modulos.config.conexion import obtener_conexion, obtener_fecha_hora_el_salvador
import streamlit as st
import pandas as pd
import hashlib


# =========================================================
# SEGURIDAD Y ROLES
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def es_marvin():
    usuario = st.session_state.get("usuario", "").lower()
    return usuario == "marvin"


# =========================================================
# ESTILO VISUAL PREMIUM
# =========================================================

def aplicar_estilo_premium():
    st.markdown("""
        <style>
            .premium-card {
                background: linear-gradient(135deg, #070b14 0%, #111827 55%, #1f2937 100%);
                border: 1px solid #d4af37;
                border-radius: 22px;
                padding: 30px;
                margin-bottom: 26px;
                box-shadow: 0 14px 34px rgba(0,0,0,0.45);
            }

            .premium-title {
                color: #f8fafc;
                font-size: 38px;
                font-weight: 900;
                margin-bottom: 8px;
            }

            .premium-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                margin-bottom: 14px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #8b6f1d, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 18px 0 24px 0;
            }

            .premium-box {
                background-color: #0f172a;
                border-left: 5px solid #d4af37;
                padding: 16px 20px;
                border-radius: 12px;
                color: #e5e7eb;
                margin-bottom: 18px;
            }

            .section-label {
                color: #f5d76e;
                font-size: 23px;
                font-weight: 800;
                margin-bottom: 14px;
            }
        </style>
    """, unsafe_allow_html=True)


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
    usuarios_base = [
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

    fecha = obtener_fecha_hora_el_salvador()

    for usuario in usuarios_base:
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


def preparar_usuarios():
    con = obtener_conexion()
    cursor = con.cursor()

    asegurar_tabla_usuarios(cursor)
    sembrar_usuarios_iniciales(cursor, con)

    cursor.close()
    con.close()


# =========================================================
# MÓDULO PRINCIPAL
# =========================================================

def mostrar_ajustes():

    aplicar_estilo_premium()

    if not es_marvin():
        st.error("❌ Solo Marvin Ramos puede acceder a los ajustes del sistema.")
        return

    st.markdown("""
        <div class="premium-card">
            <div class="premium-title">⚙️ Ajustes del Sistema</div>
            <div class="premium-subtitle">
                Administración de usuarios, contraseñas, roles y accesos del sistema.
            </div>
            <div class="gold-line"></div>
            <div class="premium-box">
                Este módulo es exclusivo para Marvin Ramos. Desde aquí puede crear usuarios,
                modificar contraseñas, cambiar roles y activar o desactivar accesos.
            </div>
        </div>
    """, unsafe_allow_html=True)

    try:
        preparar_usuarios()
    except Exception as e:
        st.error(f"❌ Error al preparar usuarios: {e}")
        return

    # =====================================================
    # USUARIOS REGISTRADOS
    # =====================================================

    with st.expander("👥 Usuarios registrados", expanded=True):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                SELECT
                    Id_Usuario,
                    Usuario,
                    Nombre,
                    Rol,
                    Activo,
                    Fecha_Registro,
                    Fecha_Modificacion
                FROM Usuario_Sistema
                ORDER BY Rol ASC, Nombre ASC
            """)

            usuarios = cursor.fetchall()

            if usuarios:
                datos = []

                for u in usuarios:
                    datos.append({
                        "ID": u[0],
                        "Usuario": u[1],
                        "Nombre": u[2],
                        "Rol": u[3],
                        "Estado": "Activo" if u[4] == 1 else "Inactivo",
                        "Fecha registro": u[5],
                        "Última modificación": u[6]
                    })

                df = pd.DataFrame(datos)

                st.dataframe(
                    df[
                        [
                            "Usuario",
                            "Nombre",
                            "Rol",
                            "Estado",
                            "Fecha registro",
                            "Última modificación"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No hay usuarios registrados.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar usuarios: {e}")

    st.divider()

    # =====================================================
    # CREAR NUEVO USUARIO
    # =====================================================

    with st.expander("➕ Crear nuevo usuario", expanded=False):

        st.markdown(
            '<div class="section-label">Datos del nuevo usuario</div>',
            unsafe_allow_html=True
        )

        with st.form("form_crear_usuario"):

            col1, col2 = st.columns(2)

            with col1:
                nuevo_usuario = st.text_input(
                    "Usuario",
                    placeholder="Ejemplo: empleado1"
                )

                nuevo_nombre = st.text_input(
                    "Nombre completo",
                    placeholder="Ejemplo: Carlos Pérez"
                )

            with col2:
                nuevo_rol = st.selectbox(
                    "Rol",
                    ["Administrador", "Vendedor"]
                )

                nueva_password = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="Ingrese una contraseña"
                )

            crear = st.form_submit_button("💾 Crear usuario")

            if crear:

                if nuevo_usuario.strip() == "" or nuevo_nombre.strip() == "" or nueva_password.strip() == "":
                    st.warning("⚠️ Debés completar usuario, nombre y contraseña.")

                else:
                    try:
                        con = obtener_conexion()
                        cursor = con.cursor()

                        asegurar_tabla_usuarios(cursor)

                        usuario_limpio = nuevo_usuario.strip().lower()

                        cursor.execute("""
                            SELECT COUNT(*)
                            FROM Usuario_Sistema
                            WHERE Usuario = %s
                        """, (usuario_limpio,))

                        existe = cursor.fetchone()[0]

                        if existe > 0:
                            st.error("❌ Ese usuario ya existe.")

                        else:
                            fecha = obtener_fecha_hora_el_salvador()

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
                                usuario_limpio,
                                nuevo_nombre.strip(),
                                nuevo_rol,
                                hash_password(nueva_password.strip()),
                                1,
                                fecha,
                                fecha
                            ))

                            con.commit()

                            st.success("✅ Usuario creado correctamente.")
                            st.rerun()

                        cursor.close()
                        con.close()

                    except Exception as e:
                        st.error(f"❌ Error al crear usuario: {e}")

    st.divider()

    # =====================================================
    # EDITAR USUARIO
    # =====================================================

    with st.expander("✏️ Editar usuario, rol o contraseña", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_usuarios(cursor)

            cursor.execute("""
                SELECT
                    Id_Usuario,
                    Usuario,
                    Nombre,
                    Rol,
                    Activo
                FROM Usuario_Sistema
                ORDER BY Nombre ASC
            """)

            usuarios = cursor.fetchall()

            if usuarios:

                opciones = {}

                for u in usuarios:
                    texto = f"{u[2]} | Usuario: {u[1]} | Rol: {u[3]} | {'Activo' if u[4] == 1 else 'Inactivo'}"
                    opciones[texto] = u

                usuario_seleccionado = st.selectbox(
                    "Seleccione el usuario a modificar",
                    list(opciones.keys())
                )

                usuario_actual = opciones[usuario_seleccionado]

                id_usuario = usuario_actual[0]
                usuario_original = usuario_actual[1]
                nombre_original = usuario_actual[2]
                rol_original = usuario_actual[3]
                activo_original = usuario_actual[4]

                with st.form("form_editar_usuario"):

                    col1, col2 = st.columns(2)

                    with col1:
                        usuario_editado = st.text_input(
                            "Usuario",
                            value=usuario_original,
                            disabled=(usuario_original == "marvin")
                        )

                        nombre_editado = st.text_input(
                            "Nombre completo",
                            value=nombre_original
                        )

                    with col2:
                        roles = ["Administrador", "Vendedor"]

                        rol_editado = st.selectbox(
                            "Rol",
                            roles,
                            index=roles.index(rol_original) if rol_original in roles else 1,
                            disabled=(usuario_original == "marvin")
                        )

                        estados = ["Activo", "Inactivo"]

                        estado_editado = st.selectbox(
                            "Estado",
                            estados,
                            index=0 if activo_original == 1 else 1,
                            disabled=(usuario_original == "marvin")
                        )

                    nueva_password = st.text_input(
                        "Nueva contraseña",
                        type="password",
                        placeholder="Dejar vacío si no desea cambiarla"
                    )

                    guardar = st.form_submit_button("💾 Guardar cambios")

                    if guardar:

                        if nombre_editado.strip() == "":
                            st.warning("⚠️ El nombre no puede quedar vacío.")

                        else:
                            try:
                                usuario_final = usuario_original if usuario_original == "marvin" else usuario_editado.strip().lower()
                                rol_final = "Administrador" if usuario_original == "marvin" else rol_editado
                                activo_final = 1 if usuario_original == "marvin" else (1 if estado_editado == "Activo" else 0)

                                cursor.execute("""
                                    SELECT COUNT(*)
                                    FROM Usuario_Sistema
                                    WHERE Usuario = %s
                                    AND Id_Usuario <> %s
                                """, (usuario_final, id_usuario))

                                duplicado = cursor.fetchone()[0]

                                if duplicado > 0:
                                    st.error("❌ Ese nombre de usuario ya está en uso.")

                                else:
                                    fecha = obtener_fecha_hora_el_salvador()

                                    if nueva_password.strip() != "":
                                        cursor.execute("""
                                            UPDATE Usuario_Sistema
                                            SET
                                                Usuario = %s,
                                                Nombre = %s,
                                                Rol = %s,
                                                Activo = %s,
                                                Password_Hash = %s,
                                                Fecha_Modificacion = %s
                                            WHERE Id_Usuario = %s
                                        """, (
                                            usuario_final,
                                            nombre_editado.strip(),
                                            rol_final,
                                            activo_final,
                                            hash_password(nueva_password.strip()),
                                            fecha,
                                            id_usuario
                                        ))
                                    else:
                                        cursor.execute("""
                                            UPDATE Usuario_Sistema
                                            SET
                                                Usuario = %s,
                                                Nombre = %s,
                                                Rol = %s,
                                                Activo = %s,
                                                Fecha_Modificacion = %s
                                            WHERE Id_Usuario = %s
                                        """, (
                                            usuario_final,
                                            nombre_editado.strip(),
                                            rol_final,
                                            activo_final,
                                            fecha,
                                            id_usuario
                                        ))

                                    con.commit()

                                    st.success("✅ Usuario actualizado correctamente.")

                                    if usuario_original == st.session_state.get("usuario", ""):
                                        st.session_state["nombre_usuario"] = nombre_editado.strip()
                                        st.session_state["rol"] = rol_final

                                    st.rerun()

                            except Exception as e:
                                con.rollback()
                                st.error(f"❌ Error al actualizar usuario: {e}")

            else:
                st.info("No hay usuarios disponibles para editar.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar editor de usuarios: {e}")

    st.divider()

    # =====================================================
    # INFORMACIÓN DE USO
    # =====================================================

    with st.expander("ℹ️ Información importante", expanded=False):

        st.info(
            "Las contraseñas se guardan protegidas mediante hash SHA-256. "
            "Marvin no puede desactivarse ni cambiar su propio rol para evitar perder el acceso principal."
        )

        st.write("Usuarios iniciales del sistema:")

        st.code("""
marvin / 1234    → Administrador
dayana / 1234    → Administrador
juanita / 1234   → Vendedor
bryan / 1234     → Vendedor
        """)
