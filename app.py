import streamlit as st

from modulos.venta import mostrar_venta
from modulos.ventas import mostrar_ventas
from modulos.login import login


# Inicializar sesión
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False


# Si ya inició sesión
if st.session_state["sesion_iniciada"]:

    st.title("🏪 Sistema Ferretería Elohim")

    st.success(
        f"Bienvenido {st.session_state['usuario']} "
        f"({st.session_state['tipo_usuario']})"
    )

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # ==========================
    # MÓDULO PRODUCTOS
    # ==========================
    mostrar_venta()

    st.divider()

    # ==========================
    # MÓDULO VENTAS
    # ==========================
    mostrar_ventas()


# Si NO ha iniciado sesión
else:
    login()
