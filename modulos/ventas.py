from modulos.config.conexion import obtener_conexion, obtener_fecha_hora_el_salvador
import streamlit as st
import pandas as pd


def mostrar_ventas():

    st.title("💰 Registro de Ventas")
    st.caption(
        "Registra ventas, descuenta stock automáticamente y muestra el historial con hora de El Salvador."
    )

    st.divider()

    # ==============================
    # REGISTRO DE VENTA
    # ==============================

    with st.expander("🛒 Nueva venta", expanded=True):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                SELECT Id_Producto, Nombre, Codigo, Stock
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
                codigo = producto[2]
                stock = producto[3]

                opciones[f"{nombre} | Código: {codigo} | Stock disponible: {stock}"] = id_producto

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

    with st.expander("📋 Ver historial de ventas", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                SELECT
                    v.Id_Venta,
                    v.Id_Producto,
                    p.Nombre,
                    p.Codigo,
                    v.Cantidad,
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
                    fecha = venta[5]

                    datos.append({
                        "Venta": f"Venta #{id_venta}",
                        "Producto": producto,
                        "Código": codigo,
                        "Cantidad": cantidad,
                        "Fecha": fecha,
                        "ID venta": id_venta,
                        "ID producto": id_producto
                    })

                df = pd.DataFrame(datos)

                st.dataframe(
                    df[["Venta", "Producto", "Código", "Cantidad", "Fecha"]],
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                st.subheader("🗑️ Eliminar registro de venta")

                opciones_eliminar = {}

                for fila in datos:
                    texto = (
                        f"{fila['Venta']} | {fila['Producto']} | "
                        f"Cantidad: {fila['Cantidad']} | Fecha: {fila['Fecha']}"
                    )

                    opciones_eliminar[texto] = {
                        "id_venta": fila["ID venta"],
                        "id_producto": fila["ID producto"],
                        "cantidad": fila["Cantidad"]
                    }

                venta_eliminar = st.selectbox(
                    "Seleccione la venta que desea eliminar",
                    list(opciones_eliminar.keys())
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo eliminar esta venta y restaurar el stock"
                )

                if st.button("🗑️ Eliminar venta seleccionada", disabled=not confirmar):

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

                        st.success("✅ Venta eliminada correctamente y stock restaurado.")
                        st.rerun()

                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al eliminar venta: {e}")

            else:
                st.info("No hay ventas registradas.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar ventas: {e}")
