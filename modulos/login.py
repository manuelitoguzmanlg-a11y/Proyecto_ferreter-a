import streamlit as st


USUARIOS = {
    "marvin": {
        "password": "1234",
        "rol": "Administrador",
        "nombre": "Marvin"
    },
    "marvin2": {
        "password": "1234",
        "rol": "Administrador",
        "nombre": "Marvin2"
    },
    "vendedor": {
        "password": "1234",
        "rol": "Vendedor",
        "nombre": "Vendedor"
    },
    "vendedor2": {
        "password": "1234",
        "rol": "Vendedor",
        "nombre": "Vendedor2"
    }
}


def mostrar_login():

    st.title("🔐 Sistema Ferretería HELOIM")
    st.caption("Inicio de sesión por roles de usuario")

    st.divider()

    with st.form("form_login"):

        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        ingresar = st.form_submit_button("Ingresar")

        if ingresar:

            usuario_limpio = usuario.lower().strip()

            if usuario_limpio in USUARIOS and password == USUARIOS[usuario_limpio]["password"]:

                st.session_state["logueado"] = True
                st.session_state["usuario"] = usuario_limpio
                st.session_state["nombre_usuario"] = USUARIOS[usuario_limpio]["nombre"]
                st.session_state["rol"] = USUARIOS[usuario_limpio]["rol"]

                st.success("✅ Inicio de sesión correcto")
                st.rerun()

            else:
                st.error("❌ Usuario o contraseña incorrectos")
