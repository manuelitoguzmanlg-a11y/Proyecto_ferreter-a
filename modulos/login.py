import streamlit as st


# =========================================================
# USUARIOS DEL SISTEMA SEGÚN DOCUMENTO DEL PROYECTO
# =========================================================

USUARIOS = {
    "marvin": {
        "password": "1234",
        "nombre": "Marvin Ramos",
        "rol": "Administrador"
    },
    "dayana": {
        "password": "1234",
        "nombre": "Dayana",
        "rol": "Administrador"
    },
    "juanita": {
        "password": "1234",
        "nombre": "Juanita de Ramos",
        "rol": "Vendedor"
    },
    "bryan": {
        "password": "1234",
        "nombre": "Bryan Ramos",
        "rol": "Vendedor"
    }
}


# =========================================================
# ESTILO VISUAL LUXURY
# =========================================================

def aplicar_estilo_login():
    st.markdown("""
        <style>
            .login-card {
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                border: 1px solid #d4af37;
                border-radius: 22px;
                padding: 34px;
                margin: 40px auto 20px auto;
                max-width: 620px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.40);
            }

            .login-title {
                color: #f8fafc;
                font-size: 40px;
                font-weight: 900;
                text-align: center;
                margin-bottom: 8px;
            }

            .login-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                text-align: center;
                margin-bottom: 18px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 20px 0 22px 0;
            }

            .login-info {
                background-color: #0f172a;
                border-left: 5px solid #d4af37;
                padding: 14px 18px;
                border-radius: 10px;
                color: #e5e7eb;
                margin-top: 18px;
                font-size: 15px;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# LOGIN
# =========================================================

def mostrar_login():

    aplicar_estilo_login()

    st.markdown("""
        <div class="login-card">
            <div class="login-title">🛠️ Ferretería HELOIM</div>
            <div class="login-subtitle">
                Sistema de Gestión de Información
            </div>
            <div class="gold-line"></div>
            <div class="login-info">
                Ingrese sus credenciales para acceder al sistema según el rol asignado.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        usuario = st.text_input(
            "Usuario",
            placeholder="Ejemplo: marvin"
        )

        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Ingrese su contraseña"
        )

        ingresar = st.button(
            "🔐 Iniciar sesión",
            use_container_width=True
        )

        if ingresar:

            usuario_limpio = usuario.strip().lower()
            password_limpio = password.strip()

            if usuario_limpio in USUARIOS:

                datos_usuario = USUARIOS[usuario_limpio]

                if password_limpio == datos_usuario["password"]:

                    st.session_state["logueado"] = True
                    st.session_state["usuario"] = usuario_limpio
                    st.session_state["nombre_usuario"] = datos_usuario["nombre"]
                    st.session_state["rol"] = datos_usuario["rol"]

                    st.success(
                        f"✅ Bienvenido, {datos_usuario['nombre']}."
                    )

                    st.rerun()

                else:
                    st.error("❌ Contraseña incorrecta.")

            else:
                st.error("❌ Usuario no registrado.")
