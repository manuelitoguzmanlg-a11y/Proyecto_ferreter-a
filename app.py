import streamlit as st

from modulos.login import mostrar_login
from modulos.venta import mostrar_venta
from modulos.ventas import mostrar_ventas
from modulos.compras import mostrar_compras
from modulos.proveedores import mostrar_proveedores
from modulos.reportes import mostrar_reportes


# =========================================================
# CONFIGURACIÓN GENERAL DE LA APP
# =========================================================

st.set_page_config(
    page_title="Ferretería HELOIM",
    page_icon="🛠️",
    layout="wide"
)


# =========================================================
# ESTILO VISUAL LUXURY
# =========================================================

def aplicar_estilo_luxury():

    st.markdown("""
        <style>
            .main-title {
                font-size: 48px;
                font-weight: 900;
                color: #f8fafc;
                margin-bottom: 6px;
            }

            .main-subtitle {
                font-size: 17px;
                color: #cbd5e1;
                margin-bottom: 20px;
            }

            .luxury-header {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #111827 100%);
                border: 1px solid #d4af37;
                border-radius: 22px;
                padding: 30px;
                margin-bottom: 28px;
                box-shadow: 0 10px 28px rgba(0,0,0,0.35);
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin-top: 18px;
            }

            .luxury-sidebar-box {
                background: linear-gradient(135deg, #111827, #1f2937);
                border-left: 5px solid #d4af37;
                padding: 18px;
                border-radius: 14px;
                color: #e5e7eb;
                margin-bottom: 20px;
            }

            .sidebar-title {
                font-size: 24px;
                font-weight: 800;
                color: #f8fafc;
                margin-bottom: 10px;
            }

            .sidebar-text {
                font-size: 15px;
                color: #e5e7eb;
                line-height: 1.7;
            }

            .role-admin {
                background-color: #14532d;
                color: #bbf7d0;
                padding: 14px 16px;
                border-radius: 12px;
                font-weight: 700;
                margin-top: 12px;
            }

            .role-vendedor {
                background-color: #1e3a8a;
                color: #bfdbfe;
                padding: 14px 16px;
                border-radius: 12px;
                font-weight: 700;
                margin-top: 12px;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# FUNCIONES DE SESIÓN Y ROLES
# =========================================================

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


def inicializar_sesion():

    if "logueado" not in st.session_state:
        st.session_state["logueado"] = False

    if "usuario" not in st.session_state:
        st.session_state["usuario"] = ""

    if "nombre_usuario" not in st.session_state:
        st.session_state["nombre_usuario"] = ""

    if "rol" not in st.session_state:
        st.session_state["rol"] = ""


# =========================================================
# INICIO DE LA APP
# =========================================================

aplicar_estilo_luxury()
inicializar_sesion()


# =========================================================
# LOGIN
# =========================================================

if not st.session_state["logueado"]:
    mostrar_login()
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
        <div class="luxury-sidebar-box">
            <div class="sidebar-title">🛠️ Ferretería HELOIM</div>
            <div class="sidebar-text">
                Sistema de Gestión de Información<br>
                Control operativo y administrativo.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write(f"**Usuario:** {st.session_state.get('nombre_usuario', '')}")
    st.write(f"**Rol:** {st.session_state.get('rol', '')}")

    if es_administrador():
        st.markdown(
            '<div class="role-admin">✅ Acceso completo de administrador</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="role-vendedor">🛒 Acceso operativo de vendedor</div>',
            unsafe_allow_html=True
        )

    st.divider()

    if st.button("🚪 Cerrar sesión"):
        cerrar_sesion()


# =========================================================
# ENCABEZADO PRINCIPAL
# =========================================================

st.markdown("""
    <div class="luxury-header">
        <div class="main-title">Sistema de Gestión de Información</div>
        <div class="main-subtitle">
            Control de productos, ventas, compras, proveedores, reportes, inventario y accesos por rol.
        </div>
        <div class="gold-line"></div>
    </div>
""", unsafe_allow_html=True)


# =========================================================
# MENÚ POR ROL
# =========================================================

if es_administrador():

    tab_productos, tab_ventas, tab_compras, tab_proveedores, tab_reportes = st.tabs(
        [
            "📦 Productos",
            "💰 Ventas",
            "🛒 Compras",
            "🚚 Proveedores",
            "📊 Reportes"
        ]
    )

    with tab_productos:
        mostrar_venta()

    with tab_ventas:
        mostrar_ventas()

    with tab_compras:
        mostrar_compras()

    with tab_proveedores:
        mostrar_proveedores()

    with tab_reportes:
        mostrar_reportes()

else:

    tab_productos, tab_ventas = st.tabs(
        [
            "📦 Productos",
            "💰 Ventas"
        ]
    )

    with tab_productos:
        mostrar_venta()

    with tab_ventas:
        mostrar_ventas()
