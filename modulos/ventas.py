from modulos.config.conexion import obtener_conexion, obtener_fecha_hora_el_salvador
import streamlit as st


def mostrar_ventas():

    st.title("💰 Registro de Ventas")
    st.caption(
        "Registra ventas, descuenta stock automáticamente y muestra el historial con hora de El Salvador."
    )

    st.divider()

    # ==============================
    # REGISTRO DE VENTA
    # ==============================

    st.subheader("🛒 Nueva venta")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT Id_Producto, Nombre, Stock
            FROM Producto
            ORDER BY Nombre ASC
        """)

        productos = cursor.fetchall()

        if not productos:
            st.warning("⚠️ No hay productos registrados.")
            cursor.close()
            con.close()
            return

        opciones = {}

        for producto in productos:
            id_producto = producto[0]
            nombre = producto[1]
            stock = producto[2]

            opciones[f"{nombre} | Stock disponible: {stock}"] = id_producto

        with st.form("form_registro_venta"):

            producto_seleccionado = st.selectbox(
                "Seleccione el producto",
                list(opciones.keys())
            )

            cantidad = st.number_input(
                "Cantidad a vender",
                min_value=1,
                step=1
            )

            registrar = st.form_submit_button("💾 Registrar venta")

            if registrar:

                id_producto = opciones[producto_seleccionado]

                cursor.execute("""
                    SELECT Stock
                    FROM Producto
                    WHERE Id_Producto = %s
                """, (id_producto,))

                resultado_stock = cursor.fetchone()

                if resultado_stock is None:
                    st.error("❌ El producto seleccionado no existe.")

                else:
                    stock_actual = resultado_stock[0]

                    if cantidad > stock_actual:

                        st.error(
                            f"❌ No hay suficiente stock. Disponible: {stock_actual}"
                        )

                    else:

                        nuevo_stock = stock_actual - cantidad

                        # Hora correcta de El Salvador
                        fecha_venta = obtener_fecha_hora_el_salvador()

                        cursor.execute("""
                            UPDATE Producto
                            SET Stock = %s
                            WHERE Id_Producto = %s
                        """, (nuevo_stock, id_producto))

                        cursor.execute("""
                            INSERT INTO Venta
                            (Id_Producto, Cantidad, Fecha)
                            VALUES (%s, %s, %s)
                        """, (id_producto, cantidad, fecha_venta))

                        con.commit()

                        st.success(
                            f"✅ Venta registrada correctamente. Nuevo stock: {nuevo_stock}"
                        )

                        st.rerun()

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"❌ Error al registrar venta: {e}")

    st.divider()

    # ==============================
    # HISTORIAL DE VENTAS
    # ==============================

    st.subheader("📋 Historial de Ventas")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT
                v.Id_Venta,
                p.Nombre,
                v.Cantidad,
                v.Fecha
            FROM Venta v
            INNER JOIN Producto p
                ON v.Id_Producto = p.Id_Producto
            ORDER BY v.Id_Venta DESC
        """)

        ventas = cursor.fetchall()

        if ventas:

            for venta in ventas:

                id_venta = venta[0]
                producto = venta[1]
                cantidad = venta[2]
                fecha = venta[3]

                with st.container():

                    col1, col2, col3, col4, col5 = st.columns([1.2, 3, 1.5, 3, 2])

                    with col1:
                        st.write(f"**Venta #{id_venta}**")

                    with col2:
                        st.write(f"**Producto:** {producto}")

                    with col3:
                        st.write(f"**Cantidad:** {cantidad}")

                    with col4:
                        st.write(f"**Fecha:** {fecha}")

                    with col5:
                        confirmar = st.checkbox(
                            "Confirmar",
                            key=f"confirmar_eliminar_venta_{id_venta}"
                        )

                        eliminar = st.button(
                            "🗑️ Eliminar",
                            key=f"eliminar_venta_{id_venta}",
                            disabled=not confirmar
                        )

                    if eliminar:

                        try:
                            # Buscar la venta antes de eliminarla
                            cursor.execute("""
                                SELECT Id_Producto, Cantidad
                                FROM Venta
                                WHERE Id_Venta = %s
                            """, (id_venta,))

                            venta_eliminar = cursor.fetchone()

                            if venta_eliminar is None:

                                st.error("❌ La venta ya no existe.")

                            else:

                                id_producto = venta_eliminar[0]
                                cantidad_vendida = venta_eliminar[1]

                                # Devolver la cantidad al stock
                                cursor.execute("""
                                    UPDATE Producto
                                    SET Stock = Stock + %s
                                    WHERE Id_Producto = %s
                                """, (cantidad_vendida, id_producto))

                                # Eliminar el registro de venta
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

                    st.divider()

        else:
            st.info("No hay ventas registradas.")

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"❌ Error al cargar ventas: {e}")
