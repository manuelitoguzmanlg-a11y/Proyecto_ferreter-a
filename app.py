import streamlit as st

from modulos.venta import mostrar_venta
from modulos.ventas import mostrar_ventas
from modulos.login import login


if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False


if st.session_state["sesion_iniciada"]:

    st.title("🏪 Sistema Ferretería Elohim")

    st.success(
        f"Bienvenido {st.session_state['usuario']} "
        f"({st.session_state['tipo_usuario']})"
    )

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    tab1, tab2 = st.tabs(["📦 Productos", "💰 Ventas"])

    with tab1:
        mostrar_venta()

    with tab2:
        mostrar_ventas()

else:
    login()
