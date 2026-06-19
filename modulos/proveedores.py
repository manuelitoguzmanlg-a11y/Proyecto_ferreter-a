from modulos.config.conexion import obtener_conexion, obtener_fecha_hora_el_salvador
import streamlit as st
import pandas as pd


# =========================================================
# VALIDACIÓN DE ROL
# =========================================================

def es_administrador():
    usuario = st.session_state.get("usuario", "").lower()
    rol = st.session_state.get("rol", "").lower()

    return usuario in ["marvin", "marvin2"] or rol in ["administrador", "admin"]


# =========================================================
# ESTILO VISUAL LUXURY
# =========================================================

def aplicar_estilo_luxury():
    st.markdown("""
        <style>
            .luxury-card {
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                border: 1px solid #d4af37;
                border-radius: 18px;
                padding: 24px;
                margin-bottom: 22px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.35);
            }

            .luxury-title {
                color: #f8fafc;
                font-size: 34px;
                font-weight: 800;
                margin-bottom: 6px;
            }

            .luxury-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                margin-bottom: 8px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #d4af37, #f5d76e, #d4af37);
                border-radius: 10px;
                margin: 18px 0 28px 0;
            }

            .section-label {
                color: #f5d76e;
                font-size: 22px;
                font-weight: 700;
                margin-bottom: 10px;
            }

            .info-box {
                background-color: #0f172a;
                border-left: 5px solid #d4af37;
                padding: 14px 18px;
                border-radius: 10px;
                color: #e5e7eb;
                margin-bottom: 18px;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# BASE DE DATOS
# =========================================================

def asegurar_tabla_proveedores(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Proveedor (
            Id_Proveedor INT AUTO_INCREMENT PRIMARY KEY,
            Nombre VARCHAR(150) NOT NULL,
            Direccion VARCHAR(255),
            Telefono VARCHAR(30),
            Vendedor_Asignado VARCHAR(150),
            NIT_NRC VARCHAR(50),
            Fecha_Registro DATETIME
        )
    """)


# =========================================================
# MÓDULO PRINCIPAL
# =========================================================

def mostrar_proveedores():

    aplicar_estilo_luxury()

    if not es_administrador():
        st.error("❌ No tenés permiso para acceder al módulo de proveedores.")
        return

    st.markdown("""
        <div class="luxury-card">
            <div class="luxury-title">🚚 Gestión de Proveedores</div>
            <div class="luxury-subtitle">
                Registro, consulta y control de proveedores principales de Ferretería HELOIM.
            </div>
            <div class="gold-line"></div>
            <div class="info-box">
                Este módulo permite administrar la cartera de proveedores, asociando datos de contacto,
                vendedor asignado y documentación fiscal como NIT o NRC.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # REGISTRAR PROVEEDOR
    # =====================================================

    with st.expander("➕ Registrar nuevo proveedor", expanded=True):

        st.markdown(
            '<div class="section-label">Datos generales del proveedor</div>',
            unsafe_allow_html=True
        )

        with st.form("form_proveedor"):

            nombre = st.text_input("Nombre de la empresa / Razón social")

            col1, col2 = st.columns(2)

            with col1:
                telefono = st.text_input("Teléfono de contacto")
                vendedor_asignado = st.text_input("Vendedor o asesor asignado")

            with col2:
                nit_nrc = st.text_input("NIT / NRC")
                direccion = st.text_area("Dirección física comercial")

            guardar = st.form_submit_button("💾 Guardar proveedor")

            if guardar:

                if nombre.strip() == "":
                    st.warning("⚠️ Debés ingresar el nombre del proveedor.")

                else:
                    try:
                        con = obtener_conexion()
                        cursor = con.cursor()

                        asegurar_tabla_proveedores(cursor)

                        fecha_registro = obtener_fecha_hora_el_salvador()

                        cursor.execute("""
                            INSERT INTO Proveedor
                            (
                                Nombre,
                                Direccion,
                                Telefono,
                                Vendedor_Asignado,
                                NIT_NRC,
                                Fecha_Registro
                            )
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            nombre,
                            direccion,
                            telefono,
                            vendedor_asignado,
                            nit_nrc,
                            fecha_registro
                        ))

                        con.commit()

                        cursor.close()
                        con.close()

                        st.success("✅ Proveedor registrado correctamente.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error al registrar proveedor: {e}")

    st.divider()

    # =====================================================
    # LISTADO DE PROVEEDORES
    # =====================================================

    with st.expander("📋 Ver proveedores registrados", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_proveedores(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    Id_Proveedor,
                    Nombre,
                    Direccion,
                    Telefono,
                    Vendedor_Asignado,
                    NIT_NRC,
                    Fecha_Registro
                FROM Proveedor
                ORDER BY Nombre ASC
            """)

            proveedores = cursor.fetchall()

            if proveedores:

                datos = []

                for proveedor in proveedores:

                    id_proveedor = proveedor[0]
                    nombre = proveedor[1]
                    direccion = proveedor[2]
                    telefono = proveedor[3]
                    vendedor_asignado = proveedor[4]
                    nit_nrc = proveedor[5]
                    fecha_registro = proveedor[6]

                    datos.append({
                        "Proveedor": nombre,
                        "Teléfono": telefono,
                        "Vendedor asignado": vendedor_asignado,
                        "NIT / NRC": nit_nrc,
                        "Dirección": direccion,
                        "Fecha de registro": fecha_registro,
                        "ID interno": id_proveedor
                    })

                df = pd.DataFrame(datos)

                st.markdown(
                    '<div class="section-label">Cartera actual de proveedores</div>',
                    unsafe_allow_html=True
                )

                st.dataframe(
                    df[
                        [
                            "Proveedor",
                            "Teléfono",
                            "Vendedor asignado",
                            "NIT / NRC",
                            "Dirección",
                            "Fecha de registro"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                # =========================================
                # ELIMINAR PROVEEDOR
                # =========================================

                st.markdown(
                    '<div class="section-label">🗑️ Eliminar proveedor</div>',
                    unsafe_allow_html=True
                )

                st.warning(
                    "Esta acción solo debe usarse si el proveedor fue registrado por error."
                )

                opciones_eliminar = {}

                for fila in datos:

                    texto = (
                        f"{fila['Proveedor']} | "
                        f"Teléfono: {fila['Teléfono']} | "
                        f"NIT/NRC: {fila['NIT / NRC']}"
                    )

                    opciones_eliminar[texto] = fila["ID interno"]

                proveedor_eliminar = st.selectbox(
                    "Seleccione el proveedor que desea eliminar",
                    list(opciones_eliminar.keys()),
                    key="proveedor_eliminar_select"
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo eliminar este proveedor",
                    key="confirmar_eliminar_proveedor"
                )

                eliminar = st.button(
                    "🗑️ Eliminar proveedor seleccionado",
                    disabled=not confirmar,
                    key="boton_eliminar_proveedor"
                )

                if eliminar:

                    try:
                        id_eliminar = opciones_eliminar[proveedor_eliminar]

                        cursor.execute("""
                            DELETE FROM Proveedor
                            WHERE Id_Proveedor = %s
                        """, (id_eliminar,))

                        con.commit()

                        st.success("✅ Proveedor eliminado correctamente.")
                        st.rerun()

                    except Exception as e:
                        st.error(
                            "❌ No se pudo eliminar el proveedor. "
                            "Puede que esté relacionado con una compra."
                        )
                        st.error(f"Detalle: {e}")

            else:
                st.info("No hay proveedores registrados todavía.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar proveedores: {e}")
