from modulos.config.conexion import obtener_conexion, obtener_fecha_hora_el_salvador
import streamlit as st
import pandas as pd


# =========================================================
# VALIDACIÓN DE ROL
# =========================================================

def es_administrador():
    usuario = st.session_state.get("usuario", "").lower()
    rol = st.session_state.get("rol", "").lower()

    return usuario in ["marvin", "marvin2"] or rol in ["administrador", "admin"]


# =========================================================
# ESTILO VISUAL LUXURY
# =========================================================

def aplicar_estilo_luxury():
    st.markdown("""
        <style>
            .luxury-card {
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                border: 1px solid #d4af37;
                border-radius: 18px;
                padding: 24px;
                margin-bottom: 22px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.35);
            }

            .luxury-title {
                color: #f8fafc;
                font-size: 36px;
                font-weight: 900;
                margin-bottom: 8px;
            }

            .luxury-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                margin-bottom: 10px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 18px 0 24px 0;
            }

            .section-label {
                color: #f5d76e;
                font-size: 23px;
                font-weight: 800;
                margin-bottom: 12px;
            }

            .info-box {
                background-color: #0f172a;
                border-left: 5px solid #d4af37;
                padding: 14px 18px;
                border-radius: 10px;
                color: #e5e7eb;
                margin-bottom: 18px;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# FUNCIONES DE BASE DE DATOS
# =========================================================

def agregar_columna_si_no_existe(cursor, tabla, columna, definicion):
    cursor.execute("""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = %s
        AND COLUMN_NAME = %s
    """, (tabla, columna))

    existe = cursor.fetchone()[0]

    if existe == 0:
        cursor.execute(f"""
            ALTER TABLE {tabla}
            ADD COLUMN {columna} {definicion}
        """)


def asegurar_columnas_producto(cursor):
    agregar_columna_si_no_existe(
        cursor,
        "Producto",
        "Categoria",
        "VARCHAR(100) DEFAULT 'Sin categoría'"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Producto",
        "Ubicacion",
        "VARCHAR(100) DEFAULT 'No asignada'"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Producto",
        "Tipo_Codigo",
        "VARCHAR(50) DEFAULT 'Con código de barras'"
    )


def generar_codigo_interno(cursor):
    numero = 1

    while True:
        codigo_generado = f"SIN-COD-{numero:03d}"

        cursor.execute("""
            SELECT COUNT(*)
            FROM Producto
            WHERE Codigo = %s
        """, (codigo_generado,))

        existe = cursor.fetchone()[0]

        if existe == 0:
            return codigo_generado

        numero += 1


# =========================================================
# LECTOR DE CÓDIGO CON CÁMARA
# =========================================================

def leer_codigo_desde_imagen(imagen):
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
    except Exception:
        return None, "Para usar la cámara necesitás tener instalado pillow, pyzbar y libzbar0."

    try:
        imagen_pil = Image.open(imagen)
        codigos = decode(imagen_pil)

        if codigos:
            codigo = codigos[0].data.decode("utf-8")
            return codigo, None

        return None, "No se detectó ningún código. Probá acercar mejor la cámara."

    except Exception as e:
        return None, f"Error al leer el código: {e}"


# =========================================================
# MÓDULO PRINCIPAL DE PRODUCTOS
# =========================================================

def mostrar_venta():

    aplicar_estilo_luxury()

    st.markdown("""
        <div class="luxury-card">
            <div class="luxury-title">📦 Gestión de Productos</div>
            <div class="luxury-subtitle">
                Registro, búsqueda, clasificación, ubicación física y control de stock del inventario.
            </div>
            <div class="gold-line"></div>
            <div class="info-box">
                Este módulo permite administrar productos con código de barras y productos sin código,
                asignándoles categoría, ubicación y niveles mínimos de stock.
            </div>
        </div>
    """, unsafe_allow_html=True)

    categorias = [
        "Construcción",
        "Fontanería",
        "Electricidad",
        "Pinturas",
        "Automotriz",
        "Herramientas",
        "Carpintería",
        "Otros"
    ]

    ubicaciones = [
        "Mostrador",
        "Bodega interna",
        "Patio de materiales",
        "Estantería principal",
        "Área de pinturas",
        "Área eléctrica",
        "Área de herramientas",
        "No asignada"
    ]

    # =====================================================
    # REGISTRAR PRODUCTO
    # =====================================================

    with st.expander("➕ Registrar nuevo producto", expanded=True):

        st.markdown(
            '<div class="section-label">Datos generales del producto</div>',
            unsafe_allow_html=True
        )

        with st.form("form_producto"):

            nombre = st.text_input("Nombre del producto")

            producto_sin_codigo = st.checkbox(
                "Este producto no posee código de barras"
            )

            if producto_sin_codigo:
                st.info(
                    "El sistema generará un código interno automático para este producto."
                )
                codigo = ""
            else:
                codigo = st.text_input("Código del producto")

            col1, col2 = st.columns(2)

            with col1:
                categoria = st.selectbox(
                    "Categoría del producto",
                    categorias
                )

                precio = st.number_input(
                    "Precio de venta",
                    min_value=0.0,
                    step=0.01
                )

                stock = st.number_input(
                    "Stock inicial",
                    min_value=0,
                    step=1
                )

            with col2:
                ubicacion = st.selectbox(
                    "Ubicación física",
                    ubicaciones
                )

                stock_minimo = st.number_input(
                    "Stock mínimo",
                    min_value=0,
                    value=5,
                    step=1
                )

            guardar = st.form_submit_button("💾 Guardar producto")

            if guardar:

                if nombre.strip() == "":
                    st.warning("⚠️ Debés completar el nombre del producto.")

                elif not producto_sin_codigo and codigo.strip() == "":
                    st.warning("⚠️ Debés ingresar el código del producto o marcar que no posee código.")

                else:

                    try:
                        con = obtener_conexion()
                        cursor = con.cursor()

                        asegurar_columnas_producto(cursor)
                        con.commit()

                        if producto_sin_codigo:
                            codigo_final = generar_codigo_interno(cursor)
                            tipo_codigo = "Sin código de barras"
                        else:
                            codigo_final = codigo.strip()
                            tipo_codigo = "Con código de barras"

                        cursor.execute("""
                            INSERT INTO Producto
                            (
                                Nombre,
                                Codigo,
                                Precio,
                                Stock,
                                Stock_Minimo,
                                Categoria,
                                Ubicacion,
                                Tipo_Codigo
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            nombre,
                            codigo_final,
                            precio,
                            stock,
                            stock_minimo,
                            categoria,
                            ubicacion,
                            tipo_codigo
                        ))

                        con.commit()

                        cursor.close()
                        con.close()

                        st.success(
                            f"✅ Producto guardado correctamente. Código asignado: {codigo_final}"
                        )

                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error al guardar producto: {e}")

    st.divider()

    # =====================================================
    # BUSCAR PRODUCTO
    # =====================================================

    with st.expander("🔎 Buscar producto por código, nombre o escáner", expanded=False):

        st.markdown(
            '<div class="section-label">Consulta rápida de inventario</div>',
            unsafe_allow_html=True
        )

        metodo = st.radio(
            "Método de búsqueda",
            ["Escribir código o nombre", "Usar cámara"],
            horizontal=True
        )

        texto_buscar = ""

        if metodo == "Escribir código o nombre":

            texto_buscar = st.text_input(
                "Ingresá el código o nombre del producto",
                key="codigo_nombre_buscar_manual"
            )

        else:

            foto = st.camera_input("📷 Tomar foto del código")

            if foto is not None:

                codigo_leido, error = leer_codigo_desde_imagen(foto)

                if codigo_leido:
                    st.success(f"✅ Código detectado: {codigo_leido}")

                    texto_buscar = st.text_input(
                        "Código detectado",
                        value=codigo_leido,
                        key="codigo_detectado"
                    )

                else:
                    st.warning(error)

        buscar = st.button("🔍 Buscar producto")

        if buscar:

            if texto_buscar.strip() == "":
                st.warning("⚠️ Ingresá, escribí o escaneá un código primero.")

            else:

                try:
                    con = obtener_conexion()
                    cursor = con.cursor()

                    asegurar_columnas_producto(cursor)
                    con.commit()

                    cursor.execute("""
                        SELECT
                            Nombre,
                            Codigo,
                            Precio,
                            Stock,
                            Stock_Minimo,
                            Categoria,
                            Ubicacion,
                            Tipo_Codigo
                        FROM Producto
                        WHERE Codigo = %s
                        OR Nombre LIKE %s
                    """, (
                        texto_buscar.strip(),
                        f"%{texto_buscar.strip()}%"
                    ))

                    producto = cursor.fetchone()

                    cursor.close()
                    con.close()

                    if producto:

                        nombre = producto[0]
                        codigo = producto[1]
                        precio = producto[2]
                        stock = producto[3]
                        stock_minimo = producto[4]
                        categoria = producto[5]
                        ubicacion = producto[6]
                        tipo_codigo = producto[7]

                        st.success("✅ Producto encontrado.")

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Producto", nombre)

                        with col2:
                            st.metric("Código", codigo)

                        with col3:
                            st.metric("Precio", f"${float(precio):.2f}")

                        with col4:
                            st.metric("Stock", stock)

                        col5, col6, col7 = st.columns(3)

                        with col5:
                            st.write(f"**Categoría:** {categoria}")

                        with col6:
                            st.write(f"**Ubicación:** {ubicacion}")

                        with col7:
                            st.write(f"**Tipo:** {tipo_codigo}")

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

    # =====================================================
    # PRODUCTOS REGISTRADOS
    # =====================================================

    with st.expander("📋 Ver productos registrados", expanded=False):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            asegurar_columnas_producto(cursor)
            con.commit()

            cursor.execute("""
                SELECT
                    Id_Producto,
                    Nombre,
                    Codigo,
                    Precio,
                    Stock,
                    Stock_Minimo,
                    Categoria,
                    Ubicacion,
                    Tipo_Codigo
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
                    categoria = producto[6]
                    ubicacion = producto[7]
                    tipo_codigo = producto[8]

                    if stock == 0:
                        estado = "Agotado"
                    elif stock <= stock_minimo:
                        estado = "Stock bajo"
                    else:
                        estado = "Disponible"

                    datos.append({
                        "Producto": nombre,
                        "Código": codigo,
                        "Tipo de código": tipo_codigo,
                        "Categoría": categoria,
                        "Ubicación": ubicacion,
                        "Precio": f"${float(precio):.2f}",
                        "Stock": stock,
                        "Stock mínimo": stock_minimo,
                        "Estado": estado,
                        "ID interno": id_producto
                    })

                df = pd.DataFrame(datos)

                st.markdown(
                    '<div class="section-label">Inventario registrado</div>',
                    unsafe_allow_html=True
                )

                st.dataframe(
                    df[
                        [
                            "Producto",
                            "Código",
                            "Tipo de código",
                            "Categoría",
                            "Ubicación",
                            "Precio",
                            "Stock",
                            "Stock mínimo",
                            "Estado"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                # =========================================
                # RESUMEN DE INVENTARIO
                # =========================================

                total_productos = len(datos)
                stock_bajo = len([x for x in datos if x["Estado"] == "Stock bajo"])
                agotados = len([x for x in datos if x["Estado"] == "Agotado"])

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Productos registrados", total_productos)

                with col2:
                    st.metric("Productos con stock bajo", stock_bajo)

                with col3:
                    st.metric("Productos agotados", agotados)

                # =========================================
                # ELIMINAR PRODUCTO SOLO ADMIN
                # =========================================

                if es_administrador():

                    st.divider()

                    st.markdown(
                        '<div class="section-label">🗑️ Eliminar producto</div>',
                        unsafe_allow_html=True
                    )

                    st.warning(
                        "Elimine productos únicamente si fueron registrados por error."
                    )

                    opciones_eliminar = {}

                    for fila in datos:
                        texto = (
                            f"{fila['Producto']} | Código: {fila['Código']} | "
                            f"Stock: {fila['Stock']}"
                        )

                        opciones_eliminar[texto] = fila["ID interno"]

                    producto_eliminar = st.selectbox(
                        "Seleccione el producto que desea eliminar",
                        list(opciones_eliminar.keys()),
                        key="producto_eliminar_select"
                    )

                    confirmar = st.checkbox(
                        "Confirmo que deseo eliminar este producto",
                        key="confirmar_eliminar_producto"
                    )

                    eliminar = st.button(
                        "🗑️ Eliminar producto seleccionado",
                        disabled=not confirmar,
                        key="boton_eliminar_producto"
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
                                "Puede que tenga ventas o compras registradas."
                            )
                            st.error(f"Detalle: {e}")

                else:
                    st.info("ℹ️ Solo los administradores pueden eliminar productos.")

            else:
                st.info("No hay productos registrados.")

            cursor.close()
            con.close()

        except Exception as e:
            st.error(f"❌ Error al cargar productos: {e}")
