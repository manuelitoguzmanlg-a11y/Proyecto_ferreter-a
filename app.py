import streamlit as st
from modulos.login import mostrar_login
from modulos.venta import mostrar_venta
from modulos.ventas import mostrar_ventas


try:
    from modulos.compras import mostrar_compras
    MODULO_COMPRAS_DISPONIBLE = True
except Exception:
    try:
        from modulos.compra import mostrar_compras
        MODULO_COMPRAS_DISPONIBLE = True
    except Exception:
        MODULO_COMPRAS_DISPONIBLE = False


st.set_page_config(
    page_title="Ferretería HELOIM",
    page_icon="🛠️",
    layout="wide"
)


def es_administrador():

    usuario = st.session_state.get("usuario", "").lower()
    rol = st.session_state.get("rol", "").lower()

    return usuario in ["marvin", "marvin2"] or rol in ["administrador", "admin"]


def cerrar_sesion():

    st.session_state["logueado"] = False
    st.session_state["usuario"] = ""
    st.session_state["nombre_usuario"] = ""
    st.session_state["rol"] = ""
    st.rerun()


if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""

if "nombre_usuario" not in st.session_state:
    st.session_state["nombre_usuario"] = ""

if "rol" not in st.session_state:
    st.session_state["rol"] = ""


if not st.session_state["logueado"]:
    mostrar_login()
    st.stop()


with st.sidebar:

    st.title("🛠️ Ferretería HELOIM")

    st.write(f"**Usuario:** {st.session_state.get('nombre_usuario', '')}")
    st.write(f"**Rol:** {st.session_state.get('rol', '')}")

    st.divider()

    if es_administrador():
        st.success("Acceso completo de administrador")
    else:
        st.info("Acceso de vendedor")

    st.divider()

    if st.button("🚪 Cerrar sesión"):
        cerrar_sesion()


st.title("Sistema de Gestión de Información")
st.caption("Control de productos, ventas, inventario y accesos por rol.")

st.divider()


if es_administrador():

    tab_productos, tab_ventas, tab_compras = st.tabs(
        ["📦 Productos", "💰 Ventas", "🛒 Compras"]
    )

    with tab_productos:
        mostrar_venta()

    with tab_ventas:
        mostrar_ventas()

    with tab_compras:

        st.title("🛒 Proceso de Compras")
        st.caption("Este módulo es exclusivo para administradores.")

        if MODULO_COMPRAS_DISPONIBLE:
            mostrar_compras()
        else:
            st.warning(
                "⚠️ Todavía no se encontró un archivo de compras. "
                "Cuando tengás compra.py o compras.py lo conectamos aquí."
            )

else:

    tab_productos, tab_ventas = st.tabs(
        ["📦 Productos", "💰 Ventas"]
    )

    with tab_productos:
        mostrar_venta()

    with tab_ventas:
        mostrar_ventas()
