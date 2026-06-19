from modulos.config.conexion import obtener_conexion
import streamlit as st


def mostrar_venta():

    st.subheader("📦 Gestión de Productos")

    nombre = st.text_input("Nombre del producto")
    codigo = st.text_input("Código")
    precio = st.number_input("Precio", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)

    if st.button("Guardar Producto"):

        try:

            con = obtener_conexion()
            cursor = con.cursor()

            sql = """
            INSERT INTO Producto
            (Nombre, Codigo, Precio, Stock, Stock_Minimo)
            VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                sql,
                (nombre, codigo, precio, stock, 5)
            )

            con.commit()

            st.success("✅ Producto guardado correctamente")

            cursor.close()
            con.close()

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.subheader("📋 Productos Registrados")

    try:

        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT
                Id_Producto,
                Nombre,
                Codigo,
                Precio,
                Stock,
                Stock_Minimo
            FROM Producto
        """)

        productos = cursor.fetchall()

        if productos:

            for producto in productos:

                id_producto = producto[0]
                nombre = producto[1]
                codigo = producto[2]
                precio = producto[3]
                stock = producto[4]
                stock_minimo = producto[5]

                st.write(
                    f"ID: {id_producto} | "
                    f"Producto: {nombre} | "
                    f"Código: {codigo} | "
                    f"Precio: ${precio} | "
                    f"Stock: {stock}"
                )

                if st.button(
                    f"🗑️ Eliminar {id_producto}",
                    key=f"eliminar_{id_producto}"
                ):

                    cursor.execute(
                        "DELETE FROM Producto WHERE Id_Producto = %s",
                        (id_producto,)
                    )

                    con.commit()

                    st.success("✅ Producto eliminado")

                    st.rerun()

                if stock == 0:

                    st.error(
                        f"🚨 {nombre} AGOTADO"
                    )

                elif stock <= stock_minimo:

                    st.warning(
                        f"⚠️ {nombre} está próximo a agotarse "
                        f"(Stock: {stock})"
                    )

                st.divider()

        else:

            st.info("No hay productos registrados.")

        cursor.close()
        con.close()

    except Exception as e:

        st.error(
            f"Error al cargar productos: {e}"
        )
