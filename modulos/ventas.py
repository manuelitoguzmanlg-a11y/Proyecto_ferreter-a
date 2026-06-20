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


# =========================================================
# MÓDULO PRINCIPAL DE VENTAS
# =========================================================

def mostrar_ventas():

    aplicar_estilo_luxury()

    st.markdown("""
        <div class="luxury-card">
            <div class="luxury-title">💰 Registro de Ventas</div>
            <div class="luxury-subtitle">
                Punto de venta rápido, control de stock, método de pago, totales e historial comercial.
            </div>
            <div class="gold-line"></div>
            <div class="info-box">
                Este módulo permite registrar ventas, descontar inventario automáticamente y generar
                información útil para control de caja, reportes mensuales y análisis de productos vendidos.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # NUEVA VENTA
    # =====================================================

    with st.expander("🛒 Registrar nueva venta", expanded=True):

        st.markdown(
            '<div class="section-label">Datos de la venta</div>',
            unsafe_allow_html=True
        )

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_ventas(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    Id_Producto,
                    Nombre,
                    Codigo,
                    Precio,
                    Stock
                FROM Producto
                ORDER BY Nombre ASC
            """)

            productos = cursor.fetchall()

            if not productos:
                st.warning("⚠️ No hay productos registrados.")
                cursor.close()
                con.close()
                return

            opciones_productos = {}

            for producto in productos:
                id_producto = producto[0]
                nombre = producto[1]
                codigo = producto[2]
                precio = producto[3]
                stock = producto[4]

                texto = (
                    f"{nombre} | Código: {codigo} | "
                    f"Precio: ${float(precio):.2f} | Stock: {stock}"
                )

                opciones_productos[texto] = {
                    "id_producto": id_producto,
                    "nombre": nombre,
                    "codigo": codigo,
                    "precio": float(precio),
                    "stock": int(stock)
                }

            producto_seleccionado = st.selectbox(
                "Seleccione el producto vendido",
                list(opciones_productos.keys())
            )

            datos_producto = opciones_productos[producto_seleccionado]

            id_producto = datos_producto["id_producto"]
            precio_unitario = datos_producto["precio"]
            stock_disponible = datos_producto["stock"]

            col1, col2 = st.columns(2)

            with col1:
                cantidad = st.number_input(
                    "Cantidad a vender",
                    min_value=1,
                    step=1
                )

            with col2:
                metodo_pago = st.selectbox(
                    "Método de pago",
                    [
                        "Efectivo",
                        "Transferencia bancaria"
                    ]
                )

            total_venta = cantidad * precio_unitario

            st.divider()

            col3, col4, col5 = st.columns(3)

            with col3:
                st.metric("Precio unitario", f"${precio_unitario:.2f}")

            with col4:
                st.metric("Stock disponible", stock_disponible)

            with col5:
                st.metric("Total de venta", f"${total_venta:.2f}")

            if stock_disponible == 0:
                st.error("🚨 Este producto está agotado.")

            elif cantidad > stock_disponible:
                st.error(
                    f"❌ No hay suficiente stock. Disponible: {stock_disponible}"
                )

            registrar = st.button("💾 Registrar venta")

            if registrar:

                try:
                    cursor.execute("""
                        SELECT
                            Precio,
                            Stock
                        FROM Producto
                        WHERE Id_Producto = %s
                    """, (id_producto,))

                    producto_actual = cursor.fetchone()

                    if producto_actual is None:
                        st.error("❌ El producto seleccionado no existe.")

                    else:
                        precio_actual = float(producto_actual[0])
                        stock_actual = int(producto_actual[1])

                        if cantidad > stock_actual:
                            st.error(
                                f"❌ No hay suficiente stock. Disponible: {stock_actual}"
                            )

                        else:
                            nuevo_stock = stock_actual - cantidad
                            total_final = cantidad * precio_actual
                            fecha_venta = obtener_fecha_hora_el_salvador()

                            cursor.execute("""
                                INSERT INTO Venta
                                (
                                    Id_Producto,
                                    Cantidad,
                                    Fecha,
                                    Precio_Unitario,
                                    Total,
                                    Metodo_Pago
                                )
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (
                                id_producto,
                                cantidad,
                                fecha_venta,
                                precio_actual,
                                total_final,
                                metodo_pago
                            ))

                            cursor.execute("""
                                UPDATE Producto
                                SET Stock = %s
                                WHERE Id_Producto = %s
                            """, (nuevo_stock, id_producto))

                            con.commit()

                            st.success(
                                f"✅ Venta registrada correctamente. Total: ${total_final:.2f}. Nuevo stock: {nuevo_stock}"
                            )

                            st.rerun()

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al registrar venta: {e}")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar productos para venta: {e}")

    # =====================================================
    # ESTADÍSTICAS DE VENTAS SOLO ADMIN
    # =====================================================

    if es_administrador():

        st.divider()

        with st.expander("📊 Estadísticas de ventas", expanded=False):

            st.markdown(
                '<div class="section-label">Indicadores comerciales</div>',
                unsafe_allow_html=True
            )

            try:
                con = obtener_conexion()
                cursor = con.cursor()

                asegurar_tabla_ventas(cursor)
                con.commit()

                cursor.execute("""
                    SELECT
                        COUNT(v.Id_Venta) AS Total_Registros,
                        COALESCE(SUM(v.Cantidad), 0) AS Total_Unidades,
                        COALESCE(SUM(
                            CASE
                                WHEN v.Total IS NULL OR v.Total = 0
                                THEN v.Cantidad * p.Precio
                                ELSE v.Total
                            END
                        ), 0) AS Ingresos_Totales
                    FROM Venta v
                    INNER JOIN Producto p
                        ON v.Id_Producto = p.Id_Producto
                """)

                resumen = cursor.fetchone()

                registros = resumen[0]
                unidades = resumen[1]
                ingresos = float(resumen[2])

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Registros de ventas", registros)

                with col2:
                    st.metric("Unidades vendidas", unidades)

                with col3:
                    st.metric("Ingresos por ventas", f"${ingresos:.2f}")

                st.divider()

                col4, col5 = st.columns(2)

                with col4:

                    cursor.execute("""
                        SELECT
                            p.Nombre,
                            p.Codigo,
                            SUM(v.Cantidad) AS Total_Vendido
                        FROM Venta v
                        INNER JOIN Producto p
                            ON v.Id_Producto = p.Id_Producto
                        GROUP BY p.Id_Producto, p.Nombre, p.Codigo
                        ORDER BY Total_Vendido DESC
                        LIMIT 1
                    """)

                    mas_vendido = cursor.fetchone()

                    if mas_vendido:
                        st.success("🔥 Producto más vendido")
                        st.write(f"**Producto:** {mas_vendido[0]}")
                        st.write(f"**Código:** {mas_vendido[1]}")
                        st.write(f"**Unidades vendidas:** {mas_vendido[2]}")
                    else:
                        st.info("Todavía no hay ventas registradas.")

                with col5:

                    cursor.execute("""
                        SELECT
                            p.Nombre,
                            p.Codigo,
                            SUM(v.Cantidad) AS Total_Vendido
                        FROM Venta v
                        INNER JOIN Producto p
                            ON v.Id_Producto = p.Id_Producto
                        GROUP BY p.Id_Producto, p.Nombre, p.Codigo
                        ORDER BY Total_Vendido ASC
                        LIMIT 1
                    """)

                    menos_vendido = cursor.fetchone()

                    if menos_vendido:
                        st.warning("📉 Producto menos vendido")
                        st.write(f"**Producto:** {menos_vendido[0]}")
                        st.write(f"**Código:** {menos_vendido[1]}")
                        st.write(f"**Unidades vendidas:** {menos_vendido[2]}")
                    else:
                        st.info("Todavía no hay ventas registradas.")

                st.divider()

                cursor.execute("""
                    SELECT
                        COALESCE(v.Metodo_Pago, 'No especificado') AS Metodo,
                        COUNT(v.Id_Venta) AS Registros,
                        COALESCE(SUM(
                            CASE
                                WHEN v.Total IS NULL OR v.Total = 0
                                THEN v.Cantidad * p.Precio
                                ELSE v.Total
                            END
                        ), 0) AS Ingresos
                    FROM Venta v
                    INNER JOIN Producto p
                        ON v.Id_Producto = p.Id_Producto
                    GROUP BY v.Metodo_Pago
                    ORDER BY Ingresos DESC
                """)

                metodos = cursor.fetchall()

                if metodos:

                    datos_metodos = []

                    for metodo in metodos:
                        datos_metodos.append({
                            "Método de pago": metodo[0],
                            "Registros": metodo[1],
                            "Ingresos": f"${float(metodo[2]):.2f}"
                        })

                    df_metodos = pd.DataFrame(datos_metodos)

                    st.markdown(
                        '<div class="section-label">Ingresos por método de pago</div>',
                        unsafe_allow_html=True
                    )

                    st.dataframe(
                        df_metodos,
                        use_container_width=True,
                        hide_index=True
                    )

                st.divider()

                cursor.execute("""
                    SELECT
                        p.Nombre,
                        p.Codigo,
                        SUM(v.Cantidad) AS Unidades,
                        COALESCE(SUM(
                            CASE
                                WHEN v.Total IS NULL OR v.Total = 0
                                THEN v.Cantidad * p.Precio
                                ELSE v.Total
                            END
                        ), 0) AS Ingresos
                    FROM Venta v
                    INNER JOIN Producto p
                        ON v.Id_Producto = p.Id_Producto
                    GROUP BY p.Id_Producto, p.Nombre, p.Codigo
                    ORDER BY Ingresos DESC
                    LIMIT 10
                """)

                top_productos = cursor.fetchall()

                if top_productos:

                    datos_top = []

                    for producto in top_productos:
                        datos_top.append({
                            "Producto": producto[0],
                            "Código": producto[1],
                            "Unidades vendidas": producto[2],
                            "Ingresos": f"${float(producto[3]):.2f}"
                        })

                    df_top = pd.DataFrame(datos_top)

                    st.markdown(
                        '<div class="section-label">Top productos por ingresos</div>',
                        unsafe_allow_html=True
                    )

                    st.dataframe(
                        df_top,
                        use_container_width=True,
                        hide_index=True
                    )

                cursor.close()
                con.close()

            except Exception as e:
                st.error(f"❌ Error al cargar estadísticas de ventas: {e}")

    # =====================================================
    # EDITAR MÉTODO DE PAGO SOLO ADMIN
    # =====================================================

    if es_administrador():

        st.divider()

        with st.expander("✏️ Editar método de pago de ventas", expanded=False):

            st.markdown(
                '<div class="section-label">Corregir ventas antiguas o sin método de pago</div>',
                unsafe_allow_html=True
            )

            st.info(
                "Use esta sección para corregir ventas registradas antes de agregar el método de pago."
            )

            try:
                con = obtener_conexion()
                cursor = con.cursor()

                asegurar_tabla_ventas(cursor)
                con.commit()

                cursor.execute("""
                    SELECT
                        v.Id_Venta,
                        v.Id_Producto,
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

                ventas_editar = cursor.fetchall()

                if ventas_editar:

                    opciones_editar = {}

                    for venta in ventas_editar:
                        id_venta = venta[0]
                        producto = venta[2]
                        cantidad = venta[4]
                        total = float(venta[6])
                        metodo_actual = venta[7]
                        fecha = venta[8]

                        texto = (
                            f"Venta #{id_venta} | {producto} | "
                            f"Cantidad: {cantidad} | Total: ${total:.2f} | "
                            f"Método actual: {metodo_actual} | Fecha: {fecha}"
                        )

                        opciones_editar[texto] = venta

                    venta_seleccionada = st.selectbox(
                        "Seleccione la venta que desea corregir",
                        list(opciones_editar.keys()),
                        key="venta_editar_pago_select"
                    )

                    venta_actual = opciones_editar[venta_seleccionada]

                    id_venta_actual = venta_actual[0]
                    cantidad_actual = int(venta_actual[4])
                    precio_unitario_actual = float(venta_actual[5])
                    total_actual = float(venta_actual[6])
                    metodo_actual = venta_actual[7]

                    metodos_pago = [
                        "Efectivo",
                        "Transferencia bancaria",
                        "No especificado"
                    ]

                    if metodo_actual in metodos_pago:
                        indice_metodo = metodos_pago.index(metodo_actual)
                    else:
                        indice_metodo = 2

                    with st.form("form_editar_metodo_pago"):

                        nuevo_metodo = st.selectbox(
                            "Nuevo método de pago",
                            metodos_pago,
                            index=indice_metodo
                        )

                        st.write(f"**Cantidad:** {cantidad_actual}")
                        st.write(f"**Precio unitario aplicado:** ${precio_unitario_actual:.2f}")
                        st.write(f"**Total de la venta:** ${total_actual:.2f}")

                        actualizar = st.form_submit_button("💾 Guardar corrección")

                        if actualizar:

                            try:
                                total_corregido = cantidad_actual * precio_unitario_actual

                                cursor.execute("""
                                    UPDATE Venta
                                    SET
                                        Metodo_Pago = %s,
                                        Precio_Unitario = %s,
                                        Total = %s
                                    WHERE Id_Venta = %s
                                """, (
                                    nuevo_metodo,
                                    precio_unitario_actual,
                                    total_corregido,
                                    id_venta_actual
                                ))

                                con.commit()

                                st.success("✅ Método de pago actualizado correctamente.")
                                st.rerun()

                            except Exception as e:
                                con.rollback()
                                st.error(f"❌ Error al actualizar método de pago: {e}")

                else:
                    st.info("No hay ventas registradas para editar.")

                cursor.close()
                con.close()

            except Exception as e:
                st.error(f"❌ Error al cargar editor de métodos de pago: {e}")

    # =====================================================
    # HISTORIAL DE VENTAS
    # =====================================================

    st.divider()

    with st.expander("📋 Ver historial de ventas", expanded=False):

        st.markdown(
            '<div class="section-label">Historial consolidado de ventas</div>',
            unsafe_allow_html=True
        )

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_ventas(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    v.Id_Venta,
                    v.Id_Producto,
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

            if ventas:

                datos = []

                for venta in ventas:
                    id_venta = venta[0]
                    id_producto = venta[1]
                    producto = venta[2]
                    codigo = venta[3]
                    cantidad = venta[4]
                    precio_unitario = venta[5]
                    total = venta[6]
                    metodo_pago = venta[7]
                    fecha = venta[8]

                    datos.append({
                        "Venta": f"Venta #{id_venta}",
                        "Producto": producto,
                        "Código": codigo,
                        "Cantidad": cantidad,
                        "Precio unitario": f"${float(precio_unitario):.2f}",
                        "Total": f"${float(total):.2f}",
                        "Método de pago": metodo_pago,
                        "Fecha": fecha,
                        "ID venta": id_venta,
                        "ID producto": id_producto,
                        "Cantidad interna": cantidad
                    })

                df = pd.DataFrame(datos)

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

                # =========================================
                # ELIMINAR VENTA SOLO ADMIN
                # =========================================

                if es_administrador():

                    st.divider()

                    st.markdown(
                        '<div class="section-label">🗑️ Eliminar registro de venta</div>',
                        unsafe_allow_html=True
                    )

                    st.warning(
                        "Al eliminar una venta, el sistema restaurará al inventario la cantidad vendida."
                    )

                    opciones_eliminar = {}

                    for fila in datos:
                        texto = (
                            f"{fila['Venta']} | {fila['Producto']} | "
                            f"Cantidad: {fila['Cantidad']} | Total: {fila['Total']} | "
                            f"Fecha: {fila['Fecha']}"
                        )

                        opciones_eliminar[texto] = {
                            "id_venta": fila["ID venta"],
                            "id_producto": fila["ID producto"],
                            "cantidad": fila["Cantidad interna"]
                        }

                    venta_eliminar = st.selectbox(
                        "Seleccione la venta que desea eliminar",
                        list(opciones_eliminar.keys()),
                        key="venta_eliminar_select"
                    )

                    confirmar = st.checkbox(
                        "Confirmo que deseo eliminar esta venta y restaurar el stock",
                        key="confirmar_eliminar_venta"
                    )

                    eliminar = st.button(
                        "🗑️ Eliminar venta seleccionada",
                        disabled=not confirmar,
                        key="boton_eliminar_venta"
                    )

                    if eliminar:

                        try:
                            datos_venta = opciones_eliminar[venta_eliminar]

                            id_venta = datos_venta["id_venta"]
                            id_producto = datos_venta["id_producto"]
                            cantidad = datos_venta["cantidad"]

                            cursor.execute("""
                                UPDATE Producto
                                SET Stock = Stock + %s
                                WHERE Id_Producto = %s
                            """, (cantidad, id_producto))

                            cursor.execute("""
                                DELETE FROM Venta
                                WHERE Id_Venta = %s
                            """, (id_venta,))

                            con.commit()

                            st.success(
                                "✅ Venta eliminada correctamente y stock restaurado."
                            )

                            st.rerun()

                        except Exception as e:
                            con.rollback()
                            st.error(f"❌ Error al eliminar venta: {e}")

                else:
                    st.info("ℹ️ Solo los administradores pueden eliminar ventas.")

            else:
                st.info("No hay ventas registradas.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar ventas: {e}")
