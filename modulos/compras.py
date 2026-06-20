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


def asegurar_tabla_compras(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Compra (
            Id_Compra INT AUTO_INCREMENT PRIMARY KEY,
            Id_Proveedor INT NULL,
            Id_Producto INT NOT NULL,
            Cantidad INT NOT NULL,
            Precio_Compra DECIMAL(10,2) DEFAULT 0,
            Fecha DATETIME NOT NULL
        )
    """)

    agregar_columna_si_no_existe(
        cursor,
        "Compra",
        "Id_Proveedor",
        "INT NULL"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Compra",
        "Id_Producto",
        "INT NOT NULL"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Compra",
        "Cantidad",
        "INT NOT NULL DEFAULT 0"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Compra",
        "Precio_Compra",
        "DECIMAL(10,2) DEFAULT 0"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Compra",
        "Fecha",
        "DATETIME NULL"
    )


# =========================================================
# MÓDULO PRINCIPAL DE COMPRAS
# =========================================================

def mostrar_compras():

    aplicar_estilo_luxury()

    if not es_administrador():
        st.error("❌ No tenés permiso para acceder al proceso de compras.")
        return

    st.markdown("""
        <div class="luxury-card">
            <div class="luxury-title">🛒 Proceso de Compras</div>
            <div class="luxury-subtitle">
                Registro de adquisiciones, control de proveedores, aumento automático de stock
                y recomendaciones inteligentes de reabastecimiento.
            </div>
            <div class="gold-line"></div>
            <div class="info-box">
                Este módulo es exclusivo para administradores. Cada compra se vincula con un proveedor
                y actualiza automáticamente el inventario disponible.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # RECOMENDACIONES DE COMPRA
    # =====================================================

    with st.expander("⚠️ Recomendaciones de compra", expanded=True):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_proveedores(cursor)
            asegurar_tabla_compras(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    p.Id_Producto,
                    p.Nombre,
                    p.Codigo,
                    p.Stock,
                    p.Stock_Minimo,
                    COALESCE(SUM(v.Cantidad), 0) AS Total_Vendido
                FROM Producto p
                LEFT JOIN Venta v
                    ON p.Id_Producto = v.Id_Producto
                GROUP BY
                    p.Id_Producto,
                    p.Nombre,
                    p.Codigo,
                    p.Stock,
                    p.Stock_Minimo
                HAVING p.Stock <= p.Stock_Minimo
                ORDER BY Total_Vendido DESC, p.Stock ASC
            """)

            recomendaciones = cursor.fetchall()

            if recomendaciones:

                st.warning(
                    "Estos productos tienen poco stock. El sistema prioriza los que más se han vendido."
                )

                datos_recomendados = []

                for producto in recomendaciones:
                    nombre = producto[1]
                    codigo = producto[2]
                    stock = producto[3]
                    stock_minimo = producto[4]
                    total_vendido = producto[5]

                    cantidad_sugerida = max((stock_minimo * 2) - stock, 1)

                    datos_recomendados.append({
                        "Producto": nombre,
                        "Código": codigo,
                        "Stock actual": stock,
                        "Stock mínimo": stock_minimo,
                        "Unidades vendidas": total_vendido,
                        "Compra sugerida": cantidad_sugerida
                    })

                df_recomendados = pd.DataFrame(datos_recomendados)

                st.dataframe(
                    df_recomendados,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.success("✅ No hay productos críticos para comprar en este momento.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar recomendaciones: {e}")

    st.divider()

    # =====================================================
    # REGISTRAR COMPRA CON PROVEEDOR
    # =====================================================

    with st.expander("➕ Registrar nueva compra", expanded=True):

        st.markdown(
            '<div class="section-label">Datos de la adquisición</div>',
            unsafe_allow_html=True
        )

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_proveedores(cursor)
            asegurar_tabla_compras(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    Id_Proveedor,
                    Nombre,
                    Telefono,
                    Vendedor_Asignado
                FROM Proveedor
                ORDER BY Nombre ASC
            """)

            proveedores = cursor.fetchall()

            cursor.execute("""
                SELECT
                    Id_Producto,
                    Nombre,
                    Codigo,
                    Stock
                FROM Producto
                ORDER BY Nombre ASC
            """)

            productos = cursor.fetchall()

            if not proveedores:
                st.warning(
                    "⚠️ No hay proveedores registrados. Primero registrá un proveedor en la pestaña Proveedores."
                )
                cursor.close()
                con.close()
                return

            if not productos:
                st.warning(
                    "⚠️ No hay productos registrados. Primero registrá productos."
                )
                cursor.close()
                con.close()
                return

            opciones_proveedores = {}

            for proveedor in proveedores:
                id_proveedor = proveedor[0]
                nombre_proveedor = proveedor[1]
                telefono = proveedor[2]
                vendedor_asignado = proveedor[3]

                opciones_proveedores[
                    f"{nombre_proveedor} | Tel: {telefono} | Asesor: {vendedor_asignado}"
                ] = id_proveedor

            opciones_productos = {}

            for producto in productos:
                id_producto = producto[0]
                nombre = producto[1]
                codigo = producto[2]
                stock = producto[3]

                opciones_productos[
                    f"{nombre} | Código: {codigo} | Stock actual: {stock}"
                ] = id_producto

            with st.form("form_registro_compra"):

                proveedor_seleccionado = st.selectbox(
                    "Seleccione el proveedor",
                    list(opciones_proveedores.keys())
                )

                producto_seleccionado = st.selectbox(
                    "Seleccione el producto comprado",
                    list(opciones_productos.keys())
                )

                col1, col2 = st.columns(2)

                with col1:
                    cantidad = st.number_input(
                        "Cantidad comprada",
                        min_value=1,
                        step=1
                    )

                with col2:
                    precio_compra = st.number_input(
                        "Precio de compra por unidad",
                        min_value=0.0,
                        step=0.01
                    )

                total_estimado = cantidad * precio_compra

                st.info(f"💵 Total estimado de la compra: ${total_estimado:.2f}")

                registrar = st.form_submit_button("💾 Registrar compra")

                if registrar:

                    id_proveedor = opciones_proveedores[proveedor_seleccionado]
                    id_producto = opciones_productos[producto_seleccionado]
                    fecha_compra = obtener_fecha_hora_el_salvador()

                    cursor.execute("""
                        INSERT INTO Compra
                        (
                            Id_Proveedor,
                            Id_Producto,
                            Cantidad,
                            Precio_Compra,
                            Fecha
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        id_proveedor,
                        id_producto,
                        cantidad,
                        precio_compra,
                        fecha_compra
                    ))

                    cursor.execute("""
                        UPDATE Producto
                        SET Stock = Stock + %s
                        WHERE Id_Producto = %s
                    """, (cantidad, id_producto))

                    con.commit()

                    st.success(
                        "✅ Compra registrada correctamente y stock actualizado."
                    )

                    st.rerun()

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al registrar compra: {e}")

    st.divider()

    # =====================================================
    # ESTADÍSTICAS DE COMPRAS
    # =====================================================

    with st.expander("📊 Estadísticas de compras", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_proveedores(cursor)
            asegurar_tabla_compras(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    COUNT(*) AS Total_Compras,
                    COALESCE(SUM(Cantidad), 0) AS Unidades_Compradas,
                    COALESCE(SUM(Cantidad * Precio_Compra), 0) AS Monto_Total
                FROM Compra
            """)

            resumen = cursor.fetchone()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Registros de compras", resumen[0])

            with col2:
                st.metric("Unidades compradas", resumen[1])

            with col3:
                st.metric("Monto total comprado", f"${float(resumen[2]):.2f}")

            st.divider()

            col4, col5 = st.columns(2)

            with col4:

                cursor.execute("""
                    SELECT
                        p.Nombre,
                        p.Codigo,
                        SUM(c.Cantidad) AS Total_Comprado
                    FROM Compra c
                    INNER JOIN Producto p
                        ON c.Id_Producto = p.Id_Producto
                    GROUP BY p.Id_Producto, p.Nombre, p.Codigo
                    ORDER BY Total_Comprado DESC
                    LIMIT 1
                """)

                producto_mas_comprado = cursor.fetchone()

                if producto_mas_comprado:
                    st.success("📦 Producto más comprado")
                    st.write(f"**Producto:** {producto_mas_comprado[0]}")
                    st.write(f"**Código:** {producto_mas_comprado[1]}")
                    st.write(f"**Unidades compradas:** {producto_mas_comprado[2]}")
                else:
                    st.info("Todavía no hay compras registradas.")

            with col5:

                cursor.execute("""
                    SELECT
                        COALESCE(pr.Nombre, 'Proveedor no especificado') AS Proveedor,
                        COUNT(c.Id_Compra) AS Total_Compras
                    FROM Compra c
                    LEFT JOIN Proveedor pr
                        ON c.Id_Proveedor = pr.Id_Proveedor
                    GROUP BY pr.Nombre
                    ORDER BY Total_Compras DESC
                    LIMIT 1
                """)

                proveedor_principal = cursor.fetchone()

                if proveedor_principal:
                    st.success("🚚 Proveedor con más compras")
                    st.write(f"**Proveedor:** {proveedor_principal[0]}")
                    st.write(f"**Registros de compra:** {proveedor_principal[1]}")
                else:
                    st.info("Todavía no hay proveedor principal.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar estadísticas de compras: {e}")

    st.divider()

    # =====================================================
    # HISTORIAL DE COMPRAS
    # =====================================================

    with st.expander("📋 Ver historial de compras", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_proveedores(cursor)
            asegurar_tabla_compras(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    c.Id_Compra,
                    c.Id_Producto,
                    c.Id_Proveedor,
                    COALESCE(pr.Nombre, 'Proveedor no especificado') AS Proveedor,
                    p.Nombre,
                    p.Codigo,
                    c.Cantidad,
                    c.Precio_Compra,
                    c.Fecha
                FROM Compra c
                INNER JOIN Producto p
                    ON c.Id_Producto = p.Id_Producto
                LEFT JOIN Proveedor pr
                    ON c.Id_Proveedor = pr.Id_Proveedor
                ORDER BY c.Id_Compra DESC
            """)

            compras = cursor.fetchall()

            if compras:

                datos = []

                for compra in compras:
                    id_compra = compra[0]
                    id_producto = compra[1]
                    id_proveedor = compra[2]
                    proveedor = compra[3]
                    producto = compra[4]
                    codigo = compra[5]
                    cantidad = compra[6]
                    precio_compra = compra[7]
                    fecha = compra[8]

                    total = float(cantidad) * float(precio_compra)

                    datos.append({
                        "Compra": f"Compra #{id_compra}",
                        "Proveedor": proveedor,
                        "Producto": producto,
                        "Código": codigo,
                        "Cantidad": cantidad,
                        "Precio unidad": f"${float(precio_compra):.2f}",
                        "Total": f"${total:.2f}",
                        "Fecha": fecha,
                        "ID compra": id_compra,
                        "ID producto": id_producto,
                        "ID proveedor": id_proveedor,
                        "Cantidad interna": cantidad
                    })

                df = pd.DataFrame(datos)

                st.markdown(
                    '<div class="section-label">Historial consolidado de adquisiciones</div>',
                    unsafe_allow_html=True
                )

                st.dataframe(
                    df[
                        [
                            "Compra",
                            "Proveedor",
                            "Producto",
                            "Código",
                            "Cantidad",
                            "Precio unidad",
                            "Total",
                            "Fecha"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                # =========================================
                # ELIMINAR COMPRA
                # =========================================

                st.markdown(
                    '<div class="section-label">🗑️ Eliminar registro de compra</div>',
                    unsafe_allow_html=True
                )

                st.warning(
                    "Al eliminar una compra, el sistema descontará del inventario la cantidad comprada."
                )

                opciones_eliminar = {}

                for fila in datos:
                    texto = (
                        f"{fila['Compra']} | {fila['Proveedor']} | "
                        f"{fila['Producto']} | Cantidad: {fila['Cantidad']} | "
                        f"Fecha: {fila['Fecha']}"
                    )

                    opciones_eliminar[texto] = {
                        "id_compra": fila["ID compra"],
                        "id_producto": fila["ID producto"],
                        "cantidad": fila["Cantidad interna"]
                    }

                compra_eliminar = st.selectbox(
                    "Seleccione la compra que desea eliminar",
                    list(opciones_eliminar.keys()),
                    key="compra_eliminar_select"
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo eliminar esta compra y descontar el stock",
                    key="confirmar_eliminar_compra"
                )

                eliminar = st.button(
                    "🗑️ Eliminar compra seleccionada",
                    disabled=not confirmar,
                    key="boton_eliminar_compra"
                )

                if eliminar:

                    try:
                        datos_compra = opciones_eliminar[compra_eliminar]

                        id_compra = datos_compra["id_compra"]
                        id_producto = datos_compra["id_producto"]
                        cantidad = datos_compra["cantidad"]

                        cursor.execute("""
                            SELECT Stock
                            FROM Producto
                            WHERE Id_Producto = %s
                        """, (id_producto,))

                        resultado_stock = cursor.fetchone()

                        if resultado_stock is None:
                            st.error(
                                "❌ No se encontró el producto relacionado con esta compra."
                            )

                        else:
                            stock_actual = resultado_stock[0]

                            if stock_actual < cantidad:
                                st.error(
                                    "❌ No se puede eliminar esta compra porque el stock quedaría negativo."
                                )

                            else:
                                cursor.execute("""
                                    UPDATE Producto
                                    SET Stock = Stock - %s
                                    WHERE Id_Producto = %s
                                """, (cantidad, id_producto))

                                cursor.execute("""
                                    DELETE FROM Compra
                                    WHERE Id_Compra = %s
                                """, (id_compra,))

                                con.commit()

                                st.success(
                                    "✅ Compra eliminada correctamente y stock descontado."
                                )

                                st.rerun()

                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al eliminar compra: {e}")

            else:
                st.info("No hay compras registradas.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar historial de compras: {e}")
