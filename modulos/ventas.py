from modulos.config.conexion import obtener_conexion
import streamlit as st


def mostrar_ventas():

    st.subheader("💰 Registro de Ventas")

    try:

        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT Id_Producto, Nombre, Stock
            FROM Producto
        """)

        productos = cursor.fetchall()

        if not productos:
            st.warning("No hay productos registrados.")
            return

        opciones = {}

        for producto in productos:
            opciones[f"{producto[1]} (Stock: {producto[2]})"] = producto[0]

        producto_seleccionado = st.selectbox(
            "Seleccione producto",
            list(opciones.keys())
        )

        cantidad = st.number_input(
            "Cantidad a vender",
            min_value=1,
            step=1
        )

        if st.button("Registrar Venta"):

            id_producto = opciones[producto_seleccionado]

            cursor.execute("""
                SELECT Stock
                FROM Producto
                WHERE Id_Producto = %s
            """, (id_producto,))

            stock_actual = cursor.fetchone()[0]

            if cantidad > stock_actual:

                st.error(
                    f"No hay suficiente stock. Disponible: {stock_actual}"
                )

            else:

                nuevo_stock = stock_actual - cantidad

                cursor.execute("""
                    UPDATE Producto
                    SET Stock = %s
                    WHERE Id_Producto = %s
                """, (nuevo_stock, id_producto))

                cursor.execute("""
                    INSERT INTO Venta
                    (Id_Producto, Cantidad)
                    VALUES (%s, %s)
                """, (id_producto, cantidad))

                con.commit()

                st.success(
                    f"Venta registrada. Nuevo stock: {nuevo_stock}"
                )

                st.rerun()

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"Error: {e}")

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

                st.write(
                    f"Venta #{venta[0]} | "
                    f"Producto: {venta[1]} | "
                    f"Cantidad: {venta[2]} | "
                    f"Fecha: {venta[3]}"
                )

        else:

            st.info("No hay ventas registradas.")

        cursor.close()
        con.close()

    except Exception as e:

        st.error(f"Error al cargar ventas: {e}")
