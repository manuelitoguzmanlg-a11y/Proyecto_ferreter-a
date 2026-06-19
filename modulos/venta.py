from modulos.config.conexion import obtener_conexion
import streamlit as st


def mostrar_venta():

    st.title("📦 Gestión de Productos")
    st.caption("Registro, consulta, eliminación y control de stock de productos.")

    st.divider()

    # ==============================
    # FORMULARIO DE PRODUCTOS
    # ==============================

    st.subheader("➕ Registrar nuevo producto")

    with st.form("form_producto"):

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre del producto")
            codigo = st.text_input("Código del producto")

        with col2:
            precio = st.number_input("Precio", min_value=0.0, step=0.01)
            stock = st.number_input("Stock inicial", min_value=0, step=1)

        stock_minimo = st.number_input(
            "Stock mínimo",
            min_value=0,
            value=5,
            step=1
        )

        guardar = st.form_submit_button("💾 Guardar producto")

        if guardar:

            if nombre.strip() == "" or codigo.strip() == "":
                st.warning("⚠️ Debes completar el nombre y el código del producto.")

            else:
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
                        (nombre, codigo, precio, stock, stock_minimo)
                    )

                    con.commit()

                    cursor.close()
                    con.close()

                    st.success("✅ Producto guardado correctamente")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al guardar producto: {e}")

    st.divider()

    # ==============================
    # LISTADO DE PRODUCTOS
    # ==============================

    st.subheader("📋 Productos registrados")

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
            ORDER BY Nombre ASC
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

                with st.container():

                    col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])

                    with col1:
                        st.write(f"**ID:** {id_producto}")

                    with col2:
                        st.write(f"**Producto:** {nombre}")

                    with col3:
                        st.write(f"**Código:** {codigo}")

                    with col4:
                        st.write(f"**Precio:** ${precio}")

                    with col5:
                        st.write(f"**Stock:** {stock}")

                    if stock == 0:
                        st.error(f"🚨 {nombre} está AGOTADO")

                    elif stock <= stock_minimo:
                        st.warning(
                            f"⚠️ {nombre} está próximo a agotarse. "
                            f"Stock actual: {stock}"
                        )

                    else:
                        st.success("✅ Stock disponible")

                    eliminar = st.button(
                        f"🗑️ Eliminar producto ID {id_producto}",
                        key=f"eliminar_{id_producto}"
                    )

                    if eliminar:

                        try:
                            cursor.execute(
                                "DELETE FROM Producto WHERE Id_Producto = %s",
                                (id_producto,)
                            )

                            con.commit()

                            st.success("✅ Producto eliminado correctamente")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error al eliminar producto: {e}")

                    st.divider()

        else:
            st.info("No hay productos registrados.")

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"❌ Error al cargar productos: {e}")
