from modulos.config.conexion import obtener_conexion
import streamlit as st
import pandas as pd


def es_administrador():

    usuario = st.session_state.get("usuario", "").lower()
    rol = st.session_state.get("rol", "").lower()

    return usuario in ["marvin", "marvin2"] or rol in ["administrador", "admin"]


def leer_codigo_desde_imagen(imagen):

    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
    except Exception:
        return None, "Para usar la cámara necesitás tener instalado pillow y pyzbar."

    try:
        imagen_pil = Image.open(imagen)
        codigos = decode(imagen_pil)

        if codigos:
            codigo = codigos[0].data.decode("utf-8")
            return codigo, None

        return None, "No se detectó ningún código. Probá acercar mejor la cámara."

    except Exception as e:
        return None, f"Error al leer el código: {e}"


def mostrar_venta():

    st.title("📦 Gestión de Productos")
    st.caption("Registro, búsqueda, consulta y control de stock de productos.")

    st.divider()

    with st.expander("➕ Registrar nuevo producto", expanded=True):

        with st.form("form_producto"):

            col1, col2 = st.columns(2)

            with col1:
                nombre = st.text_input("Nombre del producto")
                codigo = st.text_input("Código del producto")

            with col2:
                precio = st.number_input("Precio", min_value=0.0, step=0.01)
                stock = st.number_input("Stock inicial", min_value=0, step=1)

            stock_minimo = st.number_input(
                "Stock mínimo",
                min_value=0,
                value=5,
                step=1
            )

            guardar = st.form_submit_button("💾 Guardar producto")

            if guardar:

                if nombre.strip() == "" or codigo.strip() == "":
                    st.warning("⚠️ Debés completar el nombre y el código del producto.")

                else:

                    try:
                        con = obtener_conexion()
                        cursor = con.cursor()

                        cursor.execute("""
                            INSERT INTO Producto
                            (Nombre, Codigo, Precio, Stock, Stock_Minimo)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (nombre, codigo, precio, stock, stock_minimo))

                        con.commit()

                        cursor.close()
                        con.close()

                        st.success("✅ Producto guardado correctamente.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error al guardar producto: {e}")

    st.divider()

    with st.expander("🔎 Buscar producto por código o escáner", expanded=False):

        st.info(
            "Podés escribir el código manualmente o usar la cámara para leer un código de barras o QR."
        )

        metodo = st.radio(
            "Método de búsqueda",
            ["Escribir código", "Usar cámara"],
            horizontal=True
        )

        codigo_buscar = ""

        if metodo == "Escribir código":

            codigo_buscar = st.text_input(
                "Ingresá el código del producto",
                key="codigo_buscar_manual"
            )

        else:

            foto = st.camera_input("📷 Tomar foto del código")

            if foto is not None:

                codigo_leido, error = leer_codigo_desde_imagen(foto)

                if codigo_leido:
                    st.success(f"✅ Código detectado: {codigo_leido}")

                    codigo_buscar = st.text_input(
                        "Código detectado",
                        value=codigo_leido,
                        key="codigo_detectado"
                    )

                else:
                    st.warning(error)

        buscar = st.button("🔍 Buscar producto")

        if buscar:

            if codigo_buscar.strip() == "":
                st.warning("⚠️ Ingresá o escaneá un código primero.")

            else:

                try:
                    con = obtener_conexion()
                    cursor = con.cursor()

                    cursor.execute("""
                        SELECT
                            Nombre,
                            Codigo,
                            Precio,
                            Stock,
                            Stock_Minimo
                        FROM Producto
                        WHERE Codigo = %s
                    """, (codigo_buscar.strip(),))

                    producto = cursor.fetchone()

                    cursor.close()
                    con.close()

                    if producto:

                        nombre = producto[0]
                        codigo = producto[1]
                        precio = producto[2]
                        stock = producto[3]
                        stock_minimo = producto[4]

                        st.success("✅ Producto encontrado.")

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Producto", nombre)

                        with col2:
                            st.metric("Código", codigo)

                        with col3:
                            st.metric("Precio", f"${precio}")

                        with col4:
                            st.metric("Stock", stock)

                        if stock == 0:
                            st.error("🚨 Producto agotado.")
                        elif stock <= stock_minimo:
                            st.warning("⚠️ Producto próximo a agotarse.")
                        else:
                            st.success("✅ Producto disponible.")

                    else:
                        st.error("❌ Este producto no está registrado en el sistema.")

                except Exception as e:
                    st.error(f"❌ Error al buscar producto: {e}")

    st.divider()

    with st.expander("📋 Ver productos registrados", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                SELECT
                    Id_Producto,
                    Nombre,
                    Codigo,
                    Precio,
                    Stock,
                    Stock_Minimo
                FROM Producto
                ORDER BY Nombre ASC
            """)

            productos = cursor.fetchall()

            if productos:

                datos = []

                for producto in productos:

                    id_producto = producto[0]
                    nombre = producto[1]
                    codigo = producto[2]
                    precio = producto[3]
                    stock = producto[4]
                    stock_minimo = producto[5]

                    if stock == 0:
                        estado = "Agotado"
                    elif stock <= stock_minimo:
                        estado = "Stock bajo"
                    else:
                        estado = "Disponible"

                    datos.append({
                        "Producto": nombre,
                        "Código": codigo,
                        "Precio": f"${precio}",
                        "Stock": stock,
                        "Stock mínimo": stock_minimo,
                        "Estado": estado,
                        "ID interno": id_producto
                    })

                df = pd.DataFrame(datos)

                st.dataframe(
                    df[["Producto", "Código", "Precio", "Stock", "Stock mínimo", "Estado"]],
                    use_container_width=True,
                    hide_index=True
                )

                if es_administrador():

                    st.divider()
                    st.subheader("🗑️ Eliminar producto")

                    opciones_eliminar = {}

                    for fila in datos:
                        texto = (
                            f"{fila['Producto']} | Código: {fila['Código']} | "
                            f"Stock: {fila['Stock']}"
                        )

                        opciones_eliminar[texto] = fila["ID interno"]

                    producto_eliminar = st.selectbox(
                        "Seleccione el producto que desea eliminar",
                        list(opciones_eliminar.keys())
                    )

                    confirmar = st.checkbox("Confirmo que deseo eliminar este producto")

                    eliminar = st.button(
                        "🗑️ Eliminar producto seleccionado",
                        disabled=not confirmar
                    )

                    if eliminar:

                        try:
                            id_eliminar = opciones_eliminar[producto_eliminar]

                            cursor.execute("""
                                DELETE FROM Producto
                                WHERE Id_Producto = %s
                            """, (id_eliminar,))

                            con.commit()

                            st.success("✅ Producto eliminado correctamente.")
                            st.rerun()

                        except Exception as e:
                            st.error(
                                "❌ No se pudo eliminar el producto. "
                                "Puede que ya tenga ventas registradas."
                            )
                            st.error(f"Detalle: {e}")

            else:
                st.info("No hay productos registrados.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar productos: {e}")
