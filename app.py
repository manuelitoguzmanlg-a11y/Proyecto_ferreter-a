import streamlit as st

from modulos.login import mostrar_login
from modulos.venta import mostrar_venta
from modulos.ventas import mostrar_ventas
from modulos.compras import mostrar_compras
from modulos.proveedores import mostrar_proveedores
from modulos.reportes import mostrar_reportes
from modulos.caja import mostrar_caja
from modulos.comprobantes import mostrar_comprobantes
from modulos.ajustes import mostrar_ajustes


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Ferretería HELOIM",
    page_icon="🛠️",
    layout="wide"
)


# =========================================================
# ESTILO GLOBAL PREMIUM
# =========================================================

def aplicar_estilo_global():

    st.markdown("""
        <style>
            .stApp {
                background: radial-gradient(circle at top left, #1f2937 0%, #0f172a 45%, #020617 100%);
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #020617 0%, #0f172a 55%, #111827 100%);
                border-right: 1px solid rgba(212, 175, 55, 0.35);
            }

            .main-header {
                background: linear-gradient(135deg, #020617 0%, #111827 45%, #1f2937 100%);
                border: 1px solid #d4af37;
                border-radius: 26px;
                padding: 34px;
                margin-bottom: 30px;
                box-shadow: 0 16px 42px rgba(0,0,0,0.50);
            }

            .main-title {
                font-size: 46px;
                font-weight: 950;
                color: #f8fafc;
                margin-bottom: 8px;
                letter-spacing: 0.5px;
            }

            .main-subtitle {
                font-size: 16px;
                color: #cbd5e1;
                margin-bottom: 16px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #8b6f1d, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin-top: 18px;
            }

            .sidebar-card {
                background: linear-gradient(135deg, #111827, #1f2937);
                border: 1px solid rgba(212, 175, 55, 0.55);
                border-left: 5px solid #d4af37;
                padding: 20px;
                border-radius: 18px;
                color: #e5e7eb;
                margin-bottom: 20px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.35);
            }

            .sidebar-title {
                font-size: 24px;
                font-weight: 900;
                color: #f8fafc;
                margin-bottom: 8px;
            }

            .sidebar-subtitle {
                font-size: 14px;
                color: #cbd5e1;
                line-height: 1.6;
            }

            .admin-badge {
                background: linear-gradient(135deg, #064e3b, #166534);
                color: #bbf7d0;
                padding: 13px 15px;
                border-radius: 14px;
                font-weight: 800;
                margin-top: 12px;
                border: 1px solid rgba(187, 247, 208, 0.35);
            }

            .seller-badge {
                background: linear-gradient(135deg, #1e3a8a, #1d4ed8);
                color: #dbeafe;
                padding: 13px 15px;
                border-radius: 14px;
                font-weight: 800;
                margin-top: 12px;
                border: 1px solid rgba(219, 234, 254, 0.35);
            }

            .marvin-badge {
                background: linear-gradient(135deg, #713f12, #a16207);
                color: #fef3c7;
                padding: 13px 15px;
                border-radius: 14px;
                font-weight: 800;
                margin-top: 12px;
                border: 1px solid rgba(254, 243, 199, 0.35);
            }

            div[data-testid="stTabs"] button {
                font-weight: 800;
                font-size: 15px;
            }

            .stButton button {
                border-radius: 12px;
                font-weight: 800;
            }

            .stDownloadButton button {
                border-radius: 12px;
                font-weight: 800;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# SESIÓN Y ROLES
# =========================================================

def es_administrador():
    usuario = st.session_state.get("usuario", "").lower()
    rol = st.session_state.get("rol", "").lower()

    return usuario == "marvin" or rol in ["administrador", "admin"]


def es_marvin():
    usuario = st.session_state.get("usuario", "").lower()
    return usuario == "marvin"


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
# INICIO
# =========================================================

aplicar_estilo_global()
inicializar_sesion()


if not st.session_state["logueado"]:
    mostrar_login()
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
        <div class="sidebar-card">
            <div class="sidebar-title">🛠️ Ferretería HELOIM</div>
            <div class="sidebar-subtitle">
                Sistema de Gestión de Información<br>
                Inventario • Ventas • Compras • Caja
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write(f"**Usuario:** {st.session_state.get('nombre_usuario', '')}")
    st.write(f"**Rol:** {st.session_state.get('rol', '')}")

    if es_marvin():
        st.markdown(
            '<div class="marvin-badge">👑 Acceso principal de Marvin</div>',
            unsafe_allow_html=True
        )
    elif es_administrador():
        st.markdown(
            '<div class="admin-badge">✅ Acceso administrativo</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="seller-badge">🛒 Acceso operativo de vendedor</div>',
            unsafe_allow_html=True
        )

    st.divider()

    if st.button("🚪 Cerrar sesión", use_container_width=True):
        cerrar_sesion()


# =========================================================
# ENCABEZADO
# =========================================================

st.markdown("""
    <div class="main-header">
        <div class="main-title">Sistema de Gestión de Información</div>
        <div class="main-subtitle">
            Plataforma administrativa para productos, ventas, comprobantes, compras, proveedores, reportes, caja y control de accesos.
        </div>
        <div class="gold-line"></div>
    </div>
""", unsafe_allow_html=True)


# =========================================================
# MENÚ POR ROL
# =========================================================

if es_administrador():

    if es_marvin():

        (
            tab_productos,
            tab_ventas,
            tab_comprobantes,
            tab_compras,
            tab_proveedores,
            tab_reportes,
            tab_caja,
            tab_ajustes
        ) = st.tabs(
            [
                "📦 Productos",
                "💰 Ventas",
                "🧾 Comprobantes",
                "🛒 Compras",
                "🚚 Proveedores",
                "📊 Reportes",
                "💵 Caja",
                "⚙️ Ajustes"
            ]
        )

        with tab_productos:
            mostrar_venta()

        with tab_ventas:
            mostrar_ventas()

        with tab_comprobantes:
            mostrar_comprobantes()

        with tab_compras:
            mostrar_compras()

        with tab_proveedores:
            mostrar_proveedores()

        with tab_reportes:
            mostrar_reportes()

        with tab_caja:
            mostrar_caja()

        with tab_ajustes:
            mostrar_ajustes()

    else:

        (
            tab_productos,
            tab_ventas,
            tab_comprobantes,
            tab_compras,
            tab_proveedores,
            tab_reportes,
            tab_caja
        ) = st.tabs(
            [
                "📦 Productos",
                "💰 Ventas",
                "🧾 Comprobantes",
                "🛒 Compras",
                "🚚 Proveedores",
                "📊 Reportes",
                "💵 Caja"
            ]
        )

        with tab_productos:
            mostrar_venta()

        with tab_ventas:
            mostrar_ventas()

        with tab_comprobantes:
            mostrar_comprobantes()

        with tab_compras:
            mostrar_compras()

        with tab_proveedores:
            mostrar_proveedores()

        with tab_reportes:
            mostrar_reportes()

        with tab_caja:
            mostrar_caja()

else:

    tab_productos, tab_ventas, tab_comprobantes = st.tabs(
        [
            "📦 Productos",
            "💰 Ventas",
            "🧾 Comprobantes"
        ]
    )

    with tab_productos:
        mostrar_venta()

    with tab_ventas:
        mostrar_ventas()

    with tab_comprobantes:
        mostrar_comprobantes()
