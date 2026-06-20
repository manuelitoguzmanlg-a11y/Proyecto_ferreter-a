from modulos.config.conexion import obtener_conexion, obtener_fecha_hora_el_salvador
import streamlit as st
import pandas as pd
from datetime import datetime, date


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
                font-size: 36px;
                font-weight: 900;
                margin-bottom: 8px;
            }

            .luxury-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                margin-bottom: 10px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 18px 0 24px 0;
            }

            .section-label {
                color: #f5d76e;
                font-size: 23px;
                font-weight: 800;
                margin-bottom: 12px;
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
# FUNCIONES DE BASE DE DATOS
# =========================================================

def agregar_columna_si_no_existe(cursor, tabla, columna, definicion):
    cursor.execute("""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = %s
        AND COLUMN_NAME = %s
    """, (tabla, columna))

    existe = cursor.fetchone()[0]

    if existe == 0:
        cursor.execute(f"""
            ALTER TABLE {tabla}
            ADD COLUMN {columna} {definicion}
        """)


def asegurar_tabla_ventas(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Venta (
            Id_Venta INT AUTO_INCREMENT PRIMARY KEY,
            Id_Producto INT NOT NULL,
            Cantidad INT NOT NULL,
            Fecha DATETIME,
            Precio_Unitario DECIMAL(10,2) DEFAULT 0,
            Total DECIMAL(10,2) DEFAULT 0,
            Metodo_Pago VARCHAR(50) DEFAULT 'No especificado'
        )
    """)

    agregar_columna_si_no_existe(
        cursor,
        "Venta",
        "Precio_Unitario",
        "DECIMAL(10,2) DEFAULT 0"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Venta",
        "Total",
        "DECIMAL(10,2) DEFAULT 0"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Venta",
        "Metodo_Pago",
        "VARCHAR(50) DEFAULT 'No especificado'"
    )


def asegurar_tabla_cierre_caja(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cierre_Caja (
            Id_Cierre INT AUTO_INCREMENT PRIMARY KEY,
            Fecha_Cierre DATE NOT NULL,
            Total_Efectivo_Sistema DECIMAL(10,2) DEFAULT 0,
            Total_Transferencia_Sistema DECIMAL(10,2) DEFAULT 0,
            Total_General_Sistema DECIMAL(10,2) DEFAULT 0,
            Efectivo_Contado DECIMAL(10,2) DEFAULT 0,
            Diferencia DECIMAL(10,2) DEFAULT 0,
            Observaciones VARCHAR(255),
            Fecha_Registro DATETIME
        )
    """)


def obtener_fecha_actual_sv():
    fecha_hora = obtener_fecha_hora_el_salvador()

    if isinstance(fecha_hora, datetime):
        return fecha_hora.date()

    try:
        return datetime.strptime(str(fecha_hora)[:10], "%Y-%m-%d").date()
    except Exception:
        return date.today()


# =========================================================
# MÓDULO PRINCIPAL DE CAJA
# =========================================================

def mostrar_caja():

    aplicar_estilo_luxury()

    if not es_administrador():
        st.error("❌ No tenés permiso para acceder al módulo de caja.")
        return

    st.markdown("""
        <div class="luxury-card">
            <div class="luxury-title">💵 Caja y Arqueo Diario</div>
            <div class="luxury-subtitle">
                Control diario de ventas, efectivo, transferencias, cierre de caja y diferencias.
            </div>
            <div class="gold-line"></div>
            <div class="info-box">
                Este módulo permite revisar el dinero generado por ventas del día, separar efectivo y transferencias,
                y registrar un cierre de caja para control administrativo.
            </div>
        </div>
    """, unsafe_allow_html=True)

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        asegurar_tabla_ventas(cursor)
        asegurar_tabla_cierre_caja(cursor)
        con.commit()

        fecha_default = obtener_fecha_actual_sv()

        fecha_consulta = st.date_input(
            "Seleccione la fecha de caja",
            value=fecha_default
        )

        fecha_sql = fecha_consulta.strftime("%Y-%m-%d")

        st.divider()

        # =================================================
        # RESUMEN DE CAJA DEL DÍA
        # =================================================

        st.markdown(
            '<div class="section-label">Resumen de caja del día</div>',
            unsafe_allow_html=True
        )

        cursor.execute("""
            SELECT
                COUNT(v.Id_Venta) AS Registros,
                COALESCE(SUM(v.Cantidad), 0) AS Unidades,
                COALESCE(SUM(
                    CASE
                        WHEN v.Metodo_Pago = 'Efectivo'
                        THEN
                            CASE
                                WHEN v.Total IS NULL OR v.Total = 0
                                THEN v.Cantidad * p.Precio
                                ELSE v.Total
                            END
                        ELSE 0
                    END
                ), 0) AS Total_Efectivo,
                COALESCE(SUM(
                    CASE
                        WHEN v.Metodo_Pago = 'Transferencia bancaria'
                        THEN
                            CASE
                                WHEN v.Total IS NULL OR v.Total = 0
                                THEN v.Cantidad * p.Precio
                                ELSE v.Total
                            END
                        ELSE 0
                    END
                ), 0) AS Total_Transferencia,
                COALESCE(SUM(
                    CASE
                        WHEN v.Metodo_Pago IS NULL
                        OR v.Metodo_Pago = 'No especificado'
                        THEN
                            CASE
                                WHEN v.Total IS NULL OR v.Total = 0
                                THEN v.Cantidad * p.Precio
                                ELSE v.Total
                            END
                        ELSE 0
                    END
                ), 0) AS Total_No_Especificado,
                COALESCE(SUM(
                    CASE
                        WHEN v.Total IS NULL OR v.Total = 0
                        THEN v.Cantidad * p.Precio
                        ELSE v.Total
                    END
                ), 0) AS Total_General
            FROM Venta v
            INNER JOIN Producto p
                ON v.Id_Producto = p.Id_Producto
            WHERE DATE(v.Fecha) = %s
        """, (fecha_sql,))

        resumen = cursor.fetchone()

        registros = resumen[0]
        unidades = resumen[1]
        total_efectivo = float(resumen[2])
        total_transferencia = float(resumen[3])
        total_no_especificado = float(resumen[4])
        total_general = float(resumen[5])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Ventas registradas", registros)

        with col2:
            st.metric("Unidades vendidas", unidades)

        with col3:
            st.metric("Efectivo", f"${total_efectivo:.2f}")

        with col4:
            st.metric("Transferencias", f"${total_transferencia:.2f}")

        col5, col6 = st.columns(2)

        with col5:
            st.metric("No especificado", f"${total_no_especificado:.2f}")

        with col6:
            st.metric("Total general del día", f"${total_general:.2f}")

        if total_no_especificado > 0:
            st.warning(
                "⚠️ Hay ventas con método de pago no especificado. "
                "Esto corresponde a registros antiguos o ventas sin método definido."
            )

        st.divider()

        # =================================================
        # DETALLE POR MÉTODO DE PAGO
        # =================================================

        with st.expander("💳 Detalle por método de pago", expanded=True):

            cursor.execute("""
                SELECT
                    COALESCE(v.Metodo_Pago, 'No especificado') AS Metodo,
                    COUNT(v.Id_Venta) AS Registros,
                    COALESCE(SUM(v.Cantidad), 0) AS Unidades,
                    COALESCE(SUM(
                        CASE
                            WHEN v.Total IS NULL OR v.Total = 0
                            THEN v.Cantidad * p.Precio
                            ELSE v.Total
                        END
                    ), 0) AS Total
                FROM Venta v
                INNER JOIN Producto p
                    ON v.Id_Producto = p.Id_Producto
                WHERE DATE(v.Fecha) = %s
                GROUP BY v.Metodo_Pago
                ORDER BY Total DESC
            """, (fecha_sql,))

            metodos = cursor.fetchall()

            if metodos:

                datos_metodos = []

                for metodo in metodos:
                    datos_metodos.append({
                        "Método de pago": metodo[0],
                        "Registros": metodo[1],
                        "Unidades": metodo[2],
                        "Total": f"${float(metodo[3]):.2f}"
                    })

                df_metodos = pd.DataFrame(datos_metodos)

                st.dataframe(
                    df_metodos,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No hay ventas registradas para esta fecha.")

        st.divider()

        # =================================================
        # DETALLE DE VENTAS DEL DÍA
        # =================================================

        with st.expander("🧾 Detalle de ventas del día", expanded=False):

            cursor.execute("""
                SELECT
                    v.Id_Venta,
                    p.Nombre,
                    p.Codigo,
                    v.Cantidad,
                    COALESCE(v.Precio_Unitario, p.Precio) AS Precio_Unitario,
                    COALESCE(
                        CASE
                            WHEN v.Total IS NULL OR v.Total = 0
                            THEN v.Cantidad * p.Precio
                            ELSE v.Total
                        END,
                        0
                    ) AS Total,
                    COALESCE(v.Metodo_Pago, 'No especificado') AS Metodo_Pago,
                    v.Fecha
                FROM Venta v
                INNER JOIN Producto p
                    ON v.Id_Producto = p.Id_Producto
                WHERE DATE(v.Fecha) = %s
                ORDER BY v.Id_Venta DESC
            """, (fecha_sql,))

            ventas = cursor.fetchall()

            if ventas:

                datos_ventas = []

                for venta in ventas:
                    datos_ventas.append({
                        "Venta": f"Venta #{venta[0]}",
                        "Producto": venta[1],
                        "Código": venta[2],
                        "Cantidad": venta[3],
                        "Precio unitario": f"${float(venta[4]):.2f}",
                        "Total": f"${float(venta[5]):.2f}",
                        "Método de pago": venta[6],
                        "Fecha": venta[7]
                    })

                df_ventas = pd.DataFrame(datos_ventas)

                st.dataframe(
                    df_ventas,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No hay ventas registradas para esta fecha.")

        st.divider()

        # =================================================
        # ARQUEO / CIERRE DE CAJA
        # =================================================

        with st.expander("📌 Registrar cierre de caja", expanded=False):

            st.markdown(
                '<div class="section-label">Arqueo de efectivo</div>',
                unsafe_allow_html=True
            )

            st.info(
                "Ingrese el efectivo contado físicamente. El sistema calculará la diferencia contra el efectivo registrado."
            )

            efectivo_contado = st.number_input(
                "Efectivo contado físicamente",
                min_value=0.0,
                step=0.01,
                value=float(total_efectivo)
            )

            diferencia = efectivo_contado - total_efectivo

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric("Efectivo según sistema", f"${total_efectivo:.2f}")

            with col_b:
                st.metric("Efectivo contado", f"${efectivo_contado:.2f}")

            with col_c:
                st.metric("Diferencia", f"${diferencia:.2f}")

            observaciones = st.text_area(
                "Observaciones del cierre",
                placeholder="Ejemplo: cierre correcto, diferencia por cambio, venta pendiente de confirmar, etc."
            )

            confirmar_cierre = st.checkbox(
                "Confirmo que deseo registrar el cierre de caja",
                key="confirmar_cierre_caja"
            )

            guardar_cierre = st.button(
                "💾 Guardar cierre de caja",
                disabled=not confirmar_cierre
            )

            if guardar_cierre:

                try:
                    fecha_registro = obtener_fecha_hora_el_salvador()

                    cursor.execute("""
                        INSERT INTO Cierre_Caja
                        (
                            Fecha_Cierre,
                            Total_Efectivo_Sistema,
                            Total_Transferencia_Sistema,
                            Total_General_Sistema,
                            Efectivo_Contado,
                            Diferencia,
                            Observaciones,
                            Fecha_Registro
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        fecha_sql,
                        total_efectivo,
                        total_transferencia,
                        total_general,
                        efectivo_contado,
                        diferencia,
                        observaciones,
                        fecha_registro
                    ))

                    con.commit()

                    st.success("✅ Cierre de caja registrado correctamente.")
                    st.rerun()

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al guardar cierre de caja: {e}")

        st.divider()

        # =================================================
        # HISTORIAL DE CIERRES
        # =================================================

        with st.expander("📋 Historial de cierres de caja", expanded=False):

            cursor.execute("""
                SELECT
                    Id_Cierre,
                    Fecha_Cierre,
                    Total_Efectivo_Sistema,
                    Total_Transferencia_Sistema,
                    Total_General_Sistema,
                    Efectivo_Contado,
                    Diferencia,
                    Observaciones,
                    Fecha_Registro
                FROM Cierre_Caja
                ORDER BY Id_Cierre DESC
            """)

            cierres = cursor.fetchall()

            if cierres:

                datos_cierres = []

                for cierre in cierres:
                    datos_cierres.append({
                        "Cierre": f"Cierre #{cierre[0]}",
                        "Fecha cierre": cierre[1],
                        "Efectivo sistema": f"${float(cierre[2]):.2f}",
                        "Transferencias": f"${float(cierre[3]):.2f}",
                        "Total general": f"${float(cierre[4]):.2f}",
                        "Efectivo contado": f"${float(cierre[5]):.2f}",
                        "Diferencia": f"${float(cierre[6]):.2f}",
                        "Observaciones": cierre[7],
                        "Fecha registro": cierre[8]
                    })

                df_cierres = pd.DataFrame(datos_cierres)

                st.dataframe(
                    df_cierres,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("Todavía no hay cierres de caja registrados.")

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"❌ Error al cargar el módulo de caja: {e}")
