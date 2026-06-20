from modulos.config.conexion import obtener_conexion
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


def asegurar_estructura_reportes(cursor):

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Venta (
            Id_Venta INT AUTO_INCREMENT PRIMARY KEY,
            Id_Producto INT NOT NULL,
            Cantidad INT NOT NULL,
            Fecha DATETIME,
            Precio_Unitario DECIMAL(10,2) DEFAULT 0,
            Total DECIMAL(10,2) DEFAULT 0,
            Metodo_Pago VARCHAR(50) DEFAULT 'No especificado'
        )
    """)

    agregar_columna_si_no_existe(
        cursor,
        "Venta",
        "Precio_Unitario",
        "DECIMAL(10,2) DEFAULT 0"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Venta",
        "Total",
        "DECIMAL(10,2) DEFAULT 0"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Venta",
        "Metodo_Pago",
        "VARCHAR(50) DEFAULT 'No especificado'"
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Compra (
            Id_Compra INT AUTO_INCREMENT PRIMARY KEY,
            Id_Proveedor INT NULL,
            Id_Producto INT NOT NULL,
            Cantidad INT NOT NULL,
            Precio_Compra DECIMAL(10,2) DEFAULT 0,
            Fecha DATETIME
        )
    """)

    agregar_columna_si_no_existe(
        cursor,
        "Compra",
        "Id_Proveedor",
        "INT NULL"
    )

    agregar_columna_si_no_existe(
        cursor,
        "Compra",
        "Precio_Compra",
        "DECIMAL(10,2) DEFAULT 0"
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Proveedor (
            Id_Proveedor INT AUTO_INCREMENT PRIMARY KEY,
            Nombre VARCHAR(150) NOT NULL,
            Direccion VARCHAR(255),
            Telefono VARCHAR(30),
            Vendedor_Asignado VARCHAR(150),
            NIT_NRC VARCHAR(50),
            Fecha_Registro DATETIME
        )
    """)

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


def convertir_dataframe(datos, columnas):
    return pd.DataFrame(datos, columns=columnas)


# =========================================================
# MÓDULO PRINCIPAL DE REPORTES
# =========================================================

def mostrar_reportes():

    aplicar_estilo_luxury()

    if not es_administrador():
        st.error("❌ No tenés permiso para acceder al módulo de reportes.")
        return

    st.markdown("""
        <div class="luxury-card">
            <div class="luxury-title">📊 Reportes e Inteligencia de Negocio</div>
            <div class="luxury-subtitle">
                Panel ejecutivo para analizar ventas, compras, inventario, proveedores, rotación de productos
                y comportamiento mensual del negocio.
            </div>
            <div class="gold-line"></div>
            <div class="info-box">
                Este módulo consolida la información clave del sistema para apoyar la toma de decisiones
                administrativas de Ferretería HELOIM.
            </div>
        </div>
    """, unsafe_allow_html=True)

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        asegurar_estructura_reportes(cursor)
        con.commit()

        # =================================================
        # RESUMEN GENERAL
        # =================================================

        st.markdown(
            '<div class="section-label">Resumen ejecutivo</div>',
            unsafe_allow_html=True
        )

        cursor.execute("""
            SELECT COUNT(*)
            FROM Producto
        """)
        total_productos = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Proveedor
        """)
        total_proveedores = cursor.fetchone()[0]

        cursor.execute("""
            SELECT
                COUNT(v.Id_Venta) AS Registros,
                COALESCE(SUM(v.Cantidad), 0) AS Unidades,
                COALESCE(SUM(
                    CASE
                        WHEN v.Total IS NULL OR v.Total = 0
                        THEN v.Cantidad * p.Precio
                        ELSE v.Total
                    END
                ), 0) AS Ingresos
            FROM Venta v
            INNER JOIN Producto p
                ON v.Id_Producto = p.Id_Producto
        """)
        resumen_ventas = cursor.fetchone()

        cursor.execute("""
            SELECT
                COUNT(*) AS Registros,
                COALESCE(SUM(Cantidad), 0) AS Unidades,
                COALESCE(SUM(Cantidad * Precio_Compra), 0) AS Total_Compras
            FROM Compra
        """)
        resumen_compras = cursor.fetchone()

        registros_ventas = resumen_ventas[0]
        unidades_vendidas = resumen_ventas[1]
        ingresos_ventas = float(resumen_ventas[2])

        registros_compras = resumen_compras[0]
        unidades_compradas = resumen_compras[1]
        monto_compras = float(resumen_compras[2])

        resultado_estimado = ingresos_ventas - monto_compras

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Productos registrados", total_productos)

        with col2:
            st.metric("Proveedores registrados", total_proveedores)

        with col3:
            st.metric("Ingresos por ventas", f"${ingresos_ventas:.2f}")

        with col4:
            st.metric("Compras registradas", f"${monto_compras:.2f}")

        col5, col6, col7, col8 = st.columns(4)

        with col5:
            st.metric("Registros de ventas", registros_ventas)

        with col6:
            st.metric("Unidades vendidas", unidades_vendidas)

        with col7:
            st.metric("Registros de compras", registros_compras)

        with col8:
            st.metric("Unidades compradas", unidades_compradas)

        st.info(
            f"📌 Resultado estimado simple: ${resultado_estimado:.2f}. "
            "Este dato compara ingresos por ventas contra compras registradas; no sustituye un cálculo contable formal."
        )

        st.divider()

        # =================================================
        # VENTAS MENSUALES
        # =================================================

        with st.expander("📅 Ventas mensuales", expanded=True):

            cursor.execute("""
                SELECT
                    DATE_FORMAT(v.Fecha, '%Y-%m') AS Mes,
                    COUNT(v.Id_Venta) AS Registros,
                    COALESCE(SUM(v.Cantidad), 0) AS Unidades_Vendidas,
                    COALESCE(SUM(
                        CASE
                            WHEN v.Total IS NULL OR v.Total = 0
                            THEN v.Cantidad * p.Precio
                            ELSE v.Total
                        END
                    ), 0) AS Ingresos
                FROM Venta v
                INNER JOIN Producto p
                    ON v.Id_Producto = p.Id_Producto
                WHERE v.Fecha IS NOT NULL
                GROUP BY DATE_FORMAT(v.Fecha, '%Y-%m')
                ORDER BY Mes DESC
            """)

            ventas_mensuales = cursor.fetchall()

            if ventas_mensuales:

                datos = []

                for fila in ventas_mensuales:
                    datos.append({
                        "Mes": fila[0],
                        "Registros de ventas": fila[1],
                        "Unidades vendidas": fila[2],
                        "Ingresos del mes": f"${float(fila[3]):.2f}"
                    })

                df_ventas_mensuales = pd.DataFrame(datos)

                st.dataframe(
                    df_ventas_mensuales,
                    use_container_width=True,
                    hide_index=True
                )

                cursor.execute("""
                    SELECT
                        DATE_FORMAT(v.Fecha, '%Y-%m') AS Mes,
                        COALESCE(SUM(
                            CASE
                                WHEN v.Total IS NULL OR v.Total = 0
                                THEN v.Cantidad * p.Precio
                                ELSE v.Total
                            END
                        ), 0) AS Ingresos
                    FROM Venta v
                    INNER JOIN Producto p
                        ON v.Id_Producto = p.Id_Producto
                    WHERE v.Fecha IS NOT NULL
                    GROUP BY DATE_FORMAT(v.Fecha, '%Y-%m')
                    ORDER BY Ingresos DESC
                    LIMIT 1
                """)

                mejor_mes = cursor.fetchone()

                if mejor_mes:
                    st.success(
                        f"🏆 Mes con mayores ingresos: **{mejor_mes[0]}** con **${float(mejor_mes[1]):.2f}**."
                    )

            else:
                st.info("Todavía no hay ventas con fecha registrada.")

        st.divider()

        # =================================================
        # COMPRAS MENSUALES
        # =================================================

        with st.expander("📅 Compras mensuales", expanded=False):

            cursor.execute("""
                SELECT
                    DATE_FORMAT(Fecha, '%Y-%m') AS Mes,
                    COUNT(Id_Compra) AS Registros,
                    COALESCE(SUM(Cantidad), 0) AS Unidades_Compradas,
                    COALESCE(SUM(Cantidad * Precio_Compra), 0) AS Monto_Comprado
                FROM Compra
                WHERE Fecha IS NOT NULL
                GROUP BY DATE_FORMAT(Fecha, '%Y-%m')
                ORDER BY Mes DESC
            """)

            compras_mensuales = cursor.fetchall()

            if compras_mensuales:

                datos = []

                for fila in compras_mensuales:
                    datos.append({
                        "Mes": fila[0],
                        "Registros de compras": fila[1],
                        "Unidades compradas": fila[2],
                        "Monto comprado": f"${float(fila[3]):.2f}"
                    })

                df_compras_mensuales = pd.DataFrame(datos)

                st.dataframe(
                    df_compras_mensuales,
                    use_container_width=True,
                    hide_index=True
                )

                cursor.execute("""
                    SELECT
                        DATE_FORMAT(Fecha, '%Y-%m') AS Mes,
                        COALESCE(SUM(Cantidad * Precio_Compra), 0) AS Monto_Comprado
                    FROM Compra
                    WHERE Fecha IS NOT NULL
                    GROUP BY DATE_FORMAT(Fecha, '%Y-%m')
                    ORDER BY Monto_Comprado DESC
                    LIMIT 1
                """)

                mes_mayor_compra = cursor.fetchone()

                if mes_mayor_compra:
                    st.warning(
                        f"📦 Mes con mayor monto de compras: **{mes_mayor_compra[0]}** con **${float(mes_mayor_compra[1]):.2f}**."
                    )

            else:
                st.info("Todavía no hay compras con fecha registrada.")

        st.divider()

        # =================================================
        # COMPARATIVO MENSUAL
        # =================================================

        with st.expander("📈 Comparativo mensual ventas vs compras", expanded=False):

            cursor.execute("""
                SELECT
                    meses.Mes,
                    COALESCE(v.Ingresos, 0) AS Ingresos_Ventas,
                    COALESCE(c.Monto_Compras, 0) AS Monto_Compras,
                    COALESCE(v.Ingresos, 0) - COALESCE(c.Monto_Compras, 0) AS Resultado_Estimado
                FROM
                (
                    SELECT DATE_FORMAT(Fecha, '%Y-%m') AS Mes
                    FROM Venta
                    WHERE Fecha IS NOT NULL

                    UNION

                    SELECT DATE_FORMAT(Fecha, '%Y-%m') AS Mes
                    FROM Compra
                    WHERE Fecha IS NOT NULL
                ) meses
                LEFT JOIN
                (
                    SELECT
                        DATE_FORMAT(v.Fecha, '%Y-%m') AS Mes,
                        COALESCE(SUM(
                            CASE
                                WHEN v.Total IS NULL OR v.Total = 0
                                THEN v.Cantidad * p.Precio
                                ELSE v.Total
                            END
                        ), 0) AS Ingresos
                    FROM Venta v
                    INNER JOIN Producto p
                        ON v.Id_Producto = p.Id_Producto
                    WHERE v.Fecha IS NOT NULL
                    GROUP BY DATE_FORMAT(v.Fecha, '%Y-%m')
                ) v
                    ON meses.Mes = v.Mes
                LEFT JOIN
                (
                    SELECT
                        DATE_FORMAT(Fecha, '%Y-%m') AS Mes,
                        COALESCE(SUM(Cantidad * Precio_Compra), 0) AS Monto_Compras
                    FROM Compra
                    WHERE Fecha IS NOT NULL
                    GROUP BY DATE_FORMAT(Fecha, '%Y-%m')
                ) c
                    ON meses.Mes = c.Mes
                ORDER BY meses.Mes DESC
            """)

            comparativo_mensual = cursor.fetchall()

            if comparativo_mensual:

                datos = []

                for fila in comparativo_mensual:
                    datos.append({
                        "Mes": fila[0],
                        "Ingresos por ventas": f"${float(fila[1]):.2f}",
                        "Monto en compras": f"${float(fila[2]):.2f}",
                        "Resultado estimado": f"${float(fila[3]):.2f}"
                    })

                df_comparativo = pd.DataFrame(datos)

                st.dataframe(
                    df_comparativo,
                    use_container_width=True,
                    hide_index=True
                )

                st.info(
                    "Este comparativo mensual permite observar el comportamiento entre ventas y compras registradas."
                )

            else:
                st.info("Todavía no hay información mensual para comparar.")

        st.divider()

        # =================================================
        # INVENTARIO CRÍTICO
        # =================================================

        with st.expander("⚠️ Productos con stock bajo o agotado", expanded=False):

            cursor.execute("""
                SELECT
                    Nombre,
                    Codigo,
                    Categoria,
                    Ubicacion,
                    Stock,
                    Stock_Minimo,
                    CASE
                        WHEN Stock = 0 THEN 'Agotado'
                        WHEN Stock <= Stock_Minimo THEN 'Stock bajo'
                        ELSE 'Disponible'
                    END AS Estado
                FROM Producto
                WHERE Stock <= Stock_Minimo
                ORDER BY Stock ASC, Nombre ASC
            """)

            stock_critico = cursor.fetchall()

            if stock_critico:

                df_stock = convertir_dataframe(
                    stock_critico,
                    [
                        "Producto",
                        "Código",
                        "Categoría",
                        "Ubicación",
                        "Stock",
                        "Stock mínimo",
                        "Estado"
                    ]
                )

                st.warning("Estos productos requieren atención para evitar quiebres de inventario.")

                st.dataframe(
                    df_stock,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.success("✅ No hay productos con stock bajo o agotado.")

        st.divider()

        # =================================================
        # TOP PRODUCTOS POR VENTAS
        # =================================================

        with st.expander("🔥 Top productos más vendidos", expanded=False):

            cursor.execute("""
                SELECT
                    p.Nombre,
                    p.Codigo,
                    COALESCE(p.Categoria, 'Sin categoría') AS Categoria,
                    SUM(v.Cantidad) AS Unidades_Vendidas,
                    COALESCE(SUM(
                        CASE
                            WHEN v.Total IS NULL OR v.Total = 0
                            THEN v.Cantidad * p.Precio
                            ELSE v.Total
                        END
                    ), 0) AS Ingresos
                FROM Venta v
                INNER JOIN Producto p
                    ON v.Id_Producto = p.Id_Producto
                GROUP BY p.Id_Producto, p.Nombre, p.Codigo, p.Categoria
                ORDER BY Unidades_Vendidas DESC
                LIMIT 10
            """)

            top_vendidos = cursor.fetchall()

            if top_vendidos:

                datos = []

                for fila in top_vendidos:
                    datos.append({
                        "Producto": fila[0],
                        "Código": fila[1],
                        "Categoría": fila[2],
                        "Unidades vendidas": fila[3],
                        "Ingresos": f"${float(fila[4]):.2f}"
                    })

                df_top = pd.DataFrame(datos)

                st.dataframe(
                    df_top,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("Todavía no hay ventas registradas.")

        st.divider()

        # =================================================
        # PRODUCTOS DE BAJA ROTACIÓN
        # =================================================

        with st.expander("📉 Productos de baja rotación", expanded=False):

            cursor.execute("""
                SELECT
                    p.Nombre,
                    p.Codigo,
                    COALESCE(p.Categoria, 'Sin categoría') AS Categoria,
                    p.Stock,
                    COALESCE(SUM(v.Cantidad), 0) AS Unidades_Vendidas
                FROM Producto p
                LEFT JOIN Venta v
                    ON p.Id_Producto = v.Id_Producto
                GROUP BY p.Id_Producto, p.Nombre, p.Codigo, p.Categoria, p.Stock
                ORDER BY Unidades_Vendidas ASC, p.Stock DESC
                LIMIT 10
            """)

            baja_rotacion = cursor.fetchall()

            if baja_rotacion:

                df_baja = convertir_dataframe(
                    baja_rotacion,
                    [
                        "Producto",
                        "Código",
                        "Categoría",
                        "Stock actual",
                        "Unidades vendidas"
                    ]
                )

                st.info(
                    "Estos productos presentan menor movimiento. Sirven para evaluar compras futuras."
                )

                st.dataframe(
                    df_baja,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No hay productos registrados para analizar.")

        st.divider()

        # =================================================
        # VENTAS POR MÉTODO DE PAGO
        # =================================================

        with st.expander("💳 Ventas por método de pago", expanded=False):

            cursor.execute("""
                SELECT
                    COALESCE(v.Metodo_Pago, 'No especificado') AS Metodo,
                    COUNT(v.Id_Venta) AS Registros,
                    COALESCE(SUM(v.Cantidad), 0) AS Unidades,
                    COALESCE(SUM(
                        CASE
                            WHEN v.Total IS NULL OR v.Total = 0
                            THEN v.Cantidad * p.Precio
                            ELSE v.Total
                        END
                    ), 0) AS Ingresos
                FROM Venta v
                INNER JOIN Producto p
                    ON v.Id_Producto = p.Id_Producto
                GROUP BY v.Metodo_Pago
                ORDER BY Ingresos DESC
            """)

            metodos_pago = cursor.fetchall()

            if metodos_pago:

                datos = []

                for fila in metodos_pago:
                    datos.append({
                        "Método de pago": fila[0],
                        "Registros": fila[1],
                        "Unidades": fila[2],
                        "Ingresos": f"${float(fila[3]):.2f}"
                    })

                df_metodos = pd.DataFrame(datos)

                st.dataframe(
                    df_metodos,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No hay ventas registradas.")

        st.divider()

        # =================================================
        # COMPRAS POR PROVEEDOR
        # =================================================

        with st.expander("🚚 Compras por proveedor", expanded=False):

            cursor.execute("""
                SELECT
                    COALESCE(pr.Nombre, 'Proveedor no especificado') AS Proveedor,
                    COUNT(c.Id_Compra) AS Registros,
                    COALESCE(SUM(c.Cantidad), 0) AS Unidades_Compradas,
                    COALESCE(SUM(c.Cantidad * c.Precio_Compra), 0) AS Monto_Comprado
                FROM Compra c
                LEFT JOIN Proveedor pr
                    ON c.Id_Proveedor = pr.Id_Proveedor
                GROUP BY pr.Nombre
                ORDER BY Monto_Comprado DESC
            """)

            compras_proveedor = cursor.fetchall()

            if compras_proveedor:

                datos = []

                for fila in compras_proveedor:
                    datos.append({
                        "Proveedor": fila[0],
                        "Registros": fila[1],
                        "Unidades compradas": fila[2],
                        "Monto comprado": f"${float(fila[3]):.2f}"
                    })

                df_proveedores = pd.DataFrame(datos)

                st.dataframe(
                    df_proveedores,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No hay compras registradas.")

        st.divider()

        # =================================================
        # INVENTARIO GENERAL POR CATEGORÍA
        # =================================================

        with st.expander("📦 Inventario por categoría", expanded=False):

            cursor.execute("""
                SELECT
                    COALESCE(Categoria, 'Sin categoría') AS Categoria,
                    COUNT(*) AS Productos,
                    COALESCE(SUM(Stock), 0) AS Stock_Total,
                    COALESCE(SUM(Stock * Precio), 0) AS Valor_Estimado
                FROM Producto
                GROUP BY Categoria
                ORDER BY Productos DESC
            """)

            inventario_categoria = cursor.fetchall()

            if inventario_categoria:

                datos = []

                for fila in inventario_categoria:
                    datos.append({
                        "Categoría": fila[0],
                        "Productos": fila[1],
                        "Stock total": fila[2],
                        "Valor estimado inventario": f"${float(fila[3]):.2f}"
                    })

                df_categoria = pd.DataFrame(datos)

                st.dataframe(
                    df_categoria,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No hay productos registrados.")

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"❌ Error al cargar reportes: {e}")
