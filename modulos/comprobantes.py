from modulos.config.conexion import obtener_conexion
import streamlit as st
import pandas as pd


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

            .info-box {
                background-color: #0f172a;
                border-left: 5px solid #d4af37;
                padding: 14px 18px;
                border-radius: 10px;
                color: #e5e7eb;
                margin-bottom: 18px;
            }

            .section-label {
                color: #f5d76e;
                font-size: 23px;
                font-weight: 800;
                margin-bottom: 12px;
            }

            .receipt-box {
                background: #ffffff;
                color: #111827;
                border: 2px solid #d4af37;
                border-radius: 16px;
                padding: 28px;
                margin-top: 20px;
                font-family: Arial, sans-serif;
                box-shadow: 0 8px 24px rgba(0,0,0,0.25);
            }

            .receipt-title {
                text-align: center;
                font-size: 30px;
                font-weight: 900;
                color: #111827;
                margin-bottom: 2px;
            }

            .receipt-subtitle {
                text-align: center;
                font-size: 15px;
                color: #374151;
                margin-bottom: 18px;
            }

            .receipt-line {
                border-top: 2px solid #d4af37;
                margin: 16px 0;
            }

            .receipt-row {
                display: flex;
                justify-content: space-between;
                margin: 8px 0;
                font-size: 16px;
            }

            .receipt-label {
                font-weight: 700;
                color: #111827;
            }

            .receipt-total {
                font-size: 24px;
                font-weight: 900;
                color: #111827;
                text-align: right;
                margin-top: 16px;
            }

            .receipt-footer {
                text-align: center;
                font-size: 13px;
                color: #4b5563;
                margin-top: 18px;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# BASE DE DATOS
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


def generar_texto_comprobante(venta):
    texto = f"""
FERRETERÍA HELOIM
COMPROBANTE INTERNO DE VENTA

----------------------------------------
Venta: {venta["Venta"]}
Fecha: {venta["Fecha"]}
Método de pago: {venta["Método de pago"]}
----------------------------------------

Producto: {venta["Producto"]}
Código: {venta["Código"]}
Cantidad: {venta["Cantidad"]}
Precio unitario: {venta["Precio unitario"]}
Total: {venta["Total"]}

----------------------------------------
Documento interno de control.
Gracias por su compra.
----------------------------------------
"""
    return texto


# =========================================================
# MÓDULO PRINCIPAL
# =========================================================

def mostrar_comprobantes():

    aplicar_estilo_luxury()

    st.markdown("""
        <div class="luxury-card">
            <div class="luxury-title">🧾 Comprobantes de Venta</div>
            <div class="luxury-subtitle">
                Consulta y generación de comprobantes internos de venta para control comercial.
            </div>
            <div class="gold-line"></div>
            <div class="info-box">
                Este módulo permite seleccionar una venta registrada y generar un comprobante interno
                con producto, cantidad, precio, total, método de pago y fecha.
            </div>
        </div>
    """, unsafe_allow_html=True)

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        asegurar_tabla_ventas(cursor)
        con.commit()

        cursor.execute("""
            SELECT
                v.Id_Venta,
                p.Nombre,
                p.Codigo,
                v.Cantidad,
                CASE
                    WHEN v.Precio_Unitario IS NULL OR v.Precio_Unitario = 0
                    THEN p.Precio
                    ELSE v.Precio_Unitario
                END AS Precio_Unitario,
                CASE
                    WHEN v.Total IS NULL OR v.Total = 0
                    THEN v.Cantidad * p.Precio
                    ELSE v.Total
                END AS Total,
                COALESCE(v.Metodo_Pago, 'No especificado') AS Metodo_Pago,
                v.Fecha
            FROM Venta v
            INNER JOIN Producto p
                ON v.Id_Producto = p.Id_Producto
            ORDER BY v.Id_Venta DESC
        """)

        ventas = cursor.fetchall()

        if not ventas:
            st.info("Todavía no hay ventas registradas para generar comprobantes.")
            cursor.close()
            con.close()
            return

        datos = []

        for venta in ventas:
            id_venta = venta[0]
            producto = venta[1]
            codigo = venta[2]
            cantidad = venta[3]
            precio_unitario = venta[4]
            total = venta[5]
            metodo_pago = venta[6]
            fecha = venta[7]

            datos.append({
                "Venta": f"Venta #{id_venta}",
                "Producto": producto,
                "Código": codigo,
                "Cantidad": cantidad,
                "Precio unitario": f"${float(precio_unitario):.2f}",
                "Total": f"${float(total):.2f}",
                "Método de pago": metodo_pago,
                "Fecha": fecha,
                "ID": id_venta
            })

        df = pd.DataFrame(datos)

        with st.expander("📋 Ventas disponibles", expanded=False):

            st.markdown(
                '<div class="section-label">Historial de ventas para comprobante</div>',
                unsafe_allow_html=True
            )

            st.dataframe(
                df[
                    [
                        "Venta",
                        "Producto",
                        "Código",
                        "Cantidad",
                        "Precio unitario",
                        "Total",
                        "Método de pago",
                        "Fecha"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.markdown(
            '<div class="section-label">Seleccionar venta</div>',
            unsafe_allow_html=True
        )

        opciones = {}

        for fila in datos:
            texto = (
                f"{fila['Venta']} | {fila['Producto']} | "
                f"Cantidad: {fila['Cantidad']} | Total: {fila['Total']} | "
                f"Fecha: {fila['Fecha']}"
            )

            opciones[texto] = fila

        venta_seleccionada = st.selectbox(
            "Seleccione la venta para generar comprobante",
            list(opciones.keys())
        )

        venta = opciones[venta_seleccionada]

        st.markdown(f"""
            <div class="receipt-box">
                <div class="receipt-title">FERRETERÍA HELOIM</div>
                <div class="receipt-subtitle">Comprobante interno de venta</div>

                <div class="receipt-line"></div>

                <div class="receipt-row">
                    <span class="receipt-label">Venta:</span>
                    <span>{venta["Venta"]}</span>
                </div>

                <div class="receipt-row">
                    <span class="receipt-label">Fecha:</span>
                    <span>{venta["Fecha"]}</span>
                </div>

                <div class="receipt-row">
                    <span class="receipt-label">Método de pago:</span>
                    <span>{venta["Método de pago"]}</span>
                </div>

                <div class="receipt-line"></div>

                <div class="receipt-row">
                    <span class="receipt-label">Producto:</span>
                    <span>{venta["Producto"]}</span>
                </div>

                <div class="receipt-row">
                    <span class="receipt-label">Código:</span>
                    <span>{venta["Código"]}</span>
                </div>

                <div class="receipt-row">
                    <span class="receipt-label">Cantidad:</span>
                    <span>{venta["Cantidad"]}</span>
                </div>

                <div class="receipt-row">
                    <span class="receipt-label">Precio unitario:</span>
                    <span>{venta["Precio unitario"]}</span>
                </div>

                <div class="receipt-line"></div>

                <div class="receipt-total">
                    TOTAL: {venta["Total"]}
                </div>

                <div class="receipt-footer">
                    Documento interno de control. Gracias por su compra.
                </div>
            </div>
        """, unsafe_allow_html=True)

        texto_comprobante = generar_texto_comprobante(venta)

        st.download_button(
            label="⬇️ Descargar comprobante en TXT",
            data=texto_comprobante,
            file_name=f"comprobante_venta_{venta['ID']}.txt",
            mime="text/plain"
        )

        st.info(
            "Para imprimir el comprobante, podés usar la opción de impresión del navegador: Ctrl + P."
        )

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"❌ Error al cargar comprobantes: {e}")
