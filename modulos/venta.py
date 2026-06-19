import streamlit as st

def mostrar_venta():
    st.subheader("📦 Gestión de Productos")

    st.text_input("Nombre del producto")
    st.text_input("Código")
    st.number_input("Precio", min_value=0.0)
    st.number_input("Stock", min_value=0)

    st.button("Guardar Producto")
