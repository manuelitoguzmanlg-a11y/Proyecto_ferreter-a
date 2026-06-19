from modulos.config.conexion import obtener_conexion
import streamlit as st

def mostrar_venta():
    st.subheader("📦 Gestión de Productos")

    st.text_input("Nombre del producto")
    st.text_input("Código")
    st.number_input("Precio", min_value=0.0)
    st.number_input("Stock", min_value=0)

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

    except Exception as e:
        st.error(f"Error: {e}")
