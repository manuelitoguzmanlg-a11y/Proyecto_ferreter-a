from modulos.config.conexion import obtener_conexion, obtener_fecha_hora_el_salvador
import streamlit as st
import pandas as pd


def es_administrador():
    usuario = st.session_state.get("usuario", "").lower()
    rol = st.session_state.get("rol", "").lower()

    return usuario in ["marvin", "marvin2"] or rol in ["administrador", "admin"]


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


def asegurar_tabla_compras(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Compra (
            Id_Compra INT AUTO_INCREMENT PRIMARY KEY,
            Id_Producto INT NOT NULL,
            Cantidad INT NOT NULL,
            Precio_Compra DECIMAL(10,2) DEFAULT 0,
            Fecha DATETIME NOT NULL
        )
    """)

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


def mostrar_compras():

    if not es_administrador():
        st.error("❌ No tenés permiso para acceder al proceso de compras.")
        return

    st.title("🛒 Proceso de Compras")
    st.caption(
        "Registro de compras, aumento automático de stock y recomendaciones para reabastecimiento."
    )

    st.divider()

    # ==============================
    # RECOMENDACIONES DE COMPRA
    # ==============================

    with st.expander("⚠️ Recomendaciones de compra", expanded=True):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

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
                    id_producto = producto[0]
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
                        "Compra sugerida": cantidad_sugerida,
                        "ID interno": id_producto
                    })

                df_recomendados = pd.DataFrame(datos_recomendados)

                st.dataframe(
                    df_recomendados[
                        [
                            "Producto",
                            "Código",
                            "Stock actual",
                            "Stock mínimo",
                            "Unidades vendidas",
                            "Compra sugerida"
                        ]
                    ],
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

    # ==============================
    # REGISTRAR COMPRA
    # ==============================

    with st.expander("➕ Registrar nueva compra", expanded=True):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_compras(cursor)
            con.commit()

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

            if not productos:
                st.warning("⚠️ No hay productos registrados. Primero registrá productos.")
                cursor.close()
                con.close()
                return

            opciones = {}

            for producto in productos:
                id_producto = producto[0]
                nombre = producto[1]
                codigo = producto[2]
                stock = producto[3]

                opciones[
                    f"{nombre} | Código: {codigo} | Stock actual: {stock}"
                ] = id_producto

            with st.form("form_registro_compra"):

                producto_seleccionado = st.selectbox(
                    "Seleccione el producto comprado",
                    list(opciones.keys())
                )

                cantidad = st.number_input(
                    "Cantidad comprada",
                    min_value=1,
                    step=1
                )

                precio_compra = st.number_input(
                    "Precio de compra por unidad",
                    min_value=0.0,
                    step=0.01
                )

                registrar = st.form_submit_button("💾 Registrar compra")

                if registrar:

                    id_producto = opciones[producto_seleccionado]
                    fecha_compra = obtener_fecha_hora_el_salvador()

                    cursor.execute("""
                        INSERT INTO Compra
                        (Id_Producto, Cantidad, Precio_Compra, Fecha)
                        VALUES (%s, %s, %s, %s)
                    """, (id_producto, cantidad, precio_compra, fecha_compra))

                    cursor.execute("""
                        UPDATE Producto
                        SET Stock = Stock + %s
                        WHERE Id_Producto = %s
                    """, (cantidad, id_producto))

                    con.commit()

                    st.success("✅ Compra registrada correctamente y stock actualizado.")
                    st.rerun()

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al registrar compra: {e}")

    st.divider()

    # ==============================
    # ESTADÍSTICAS DE COMPRAS
    # ==============================

    with st.expander("📊 Estadísticas de compras", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

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
                st.metric("Monto total comprado", f"${resumen[2]}")

            st.divider()

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

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar estadísticas de compras: {e}")

    st.divider()

    # ==============================
    # HISTORIAL DE COMPRAS
    # ==============================

    with st.expander("📋 Ver historial de compras", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_tabla_compras(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    c.Id_Compra,
                    c.Id_Producto,
                    p.Nombre,
                    p.Codigo,
                    c.Cantidad,
                    c.Precio_Compra,
                    c.Fecha
                FROM Compra c
                INNER JOIN Producto p
                    ON c.Id_Producto = p.Id_Producto
                ORDER BY c.Id_Compra DESC
            """)

            compras = cursor.fetchall()

            if compras:

                datos = []

                for compra in compras:
                    id_compra = compra[0]
                    id_producto = compra[1]
                    producto = compra[2]
                    codigo = compra[3]
                    cantidad = compra[4]
                    precio_compra = compra[5]
                    fecha = compra[6]

                    total = cantidad * precio_compra

                    datos.append({
                        "Compra": f"Compra #{id_compra}",
                        "Producto": producto,
                        "Código": codigo,
                        "Cantidad": cantidad,
                        "Precio unidad": f"${precio_compra}",
                        "Total": f"${total}",
                        "Fecha": fecha,
                        "ID compra": id_compra,
                        "ID producto": id_producto,
                        "Cantidad interna": cantidad
                    })

                df = pd.DataFrame(datos)

                st.dataframe(
                    df[
                        [
                            "Compra",
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

                st.subheader("🗑️ Eliminar registro de compra")

                opciones_eliminar = {}

                for fila in datos:
                    texto = (
                        f"{fila['Compra']} | {fila['Producto']} | "
                        f"Cantidad: {fila['Cantidad']} | Fecha: {fila['Fecha']}"
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

                        stock_actual = cursor.fetchone()[0]

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
