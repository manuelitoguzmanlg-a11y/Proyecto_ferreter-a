from modulos.config.conexion import obtener_conexion
import streamlit as st
import pandas as pd


# =========================================================
# ESTILO VISUAL
# =========================================================

def aplicar_estilo_reportes():
    st.markdown("""
        <style>
            .report-card {
                background: linear-gradient(135deg, #070b14 0%, #111827 55%, #1f2937 100%);
                border: 1px solid #d4af37;
                border-radius: 24px;
                padding: 30px;
                margin-bottom: 28px;
                box-shadow: 0 14px 34px rgba(0,0,0,0.45);
            }

            .report-title {
                color: #f8fafc;
                font-size: 40px;
                font-weight: 950;
                margin-bottom: 8px;
            }

            .report-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                margin-bottom: 12px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #8b6f1d, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 18px 0 24px 0;
            }

            .info-box {
                background-color: #0f172a;
                border-left: 5px solid #d4af37;
                padding: 16px 20px;
                border-radius: 12px;
                color: #e5e7eb;
                margin-bottom: 18px;
            }

            .section-label {
                color: #f5d76e;
                font-size: 24px;
                font-weight: 900;
                margin-bottom: 14px;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# FUNCIONES GENERALES DE BASE DE DATOS
# =========================================================

def obtener_columnas(tabla):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
        """, (tabla,))

        columnas = [fila[0] for fila in cursor.fetchall()]

        cursor.close()
        con.close()

        return columnas

    except Exception:
        return []


def tabla_existe(tabla):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
        """, (tabla,))

        existe = cursor.fetchone()[0]

        cursor.close()
        con.close()

        return existe > 0

    except Exception:
        return False


def ejecutar_dataframe(query):
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute(query)
    filas = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    cursor.close()
    con.close()

    return pd.DataFrame(filas, columns=columnas)


def obtener_valor(query):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute(query)
        valor = cursor.fetchone()[0]

        cursor.close()
        con.close()

        return valor if valor is not None else 0

    except Exception:
        return 0


def formatear_moneda(valor):
    try:
        return f"${float(valor):.2f}"
    except Exception:
        return "$0.00"


def formatear_columna_moneda(df, columna):
    if columna in df.columns:
        df[columna] = df[columna].apply(formatear_moneda)

    return df


def obtener_columna_fecha(tabla, opciones):
    columnas = obtener_columnas(tabla)

    for opcion in opciones:
        if opcion in columnas:
            return opcion

    return None


def obtener_expr_codigo_producto():
    columnas_producto = obtener_columnas("Producto")

    if "Codigo" in columnas_producto:
        return "p.`Codigo`"

    if "Codigo_Barras" in columnas_producto:
        return "p.`Codigo_Barras`"

    return "'Sin código'"


def obtener_expr_total_venta():
    columnas_venta = obtener_columnas("Venta")
    columnas_producto = obtener_columnas("Producto")

    if "Precio_Unitario" in columnas_venta:
        respaldo = "v.`Cantidad` * v.`Precio_Unitario`"
    elif "Precio" in columnas_producto:
        respaldo = "v.`Cantidad` * p.`Precio`"
    else:
        respaldo = "0"

    if "Total" in columnas_venta:
        return f"COALESCE(NULLIF(v.`Total`, 0), {respaldo})"

    return respaldo


def obtener_expr_total_compra():
    columnas_compra = obtener_columnas("Compra")

    precio_unitario = None

    posibles_precios = [
        "Precio_Unitario",
        "Precio_Compra",
        "Costo_Unitario",
        "Precio"
    ]

    for columna in posibles_precios:
        if columna in columnas_compra:
            precio_unitario = columna
            break

    if precio_unitario:
        respaldo = f"c.`Cantidad` * c.`{precio_unitario}`"
    else:
        respaldo = "0"

    posibles_totales = [
        "Total",
        "Monto_Total",
        "Total_Compra",
        "Monto"
    ]

    for columna in posibles_totales:
        if columna in columnas_compra:
            return f"COALESCE(NULLIF(c.`{columna}`, 0), {respaldo})"

    return respaldo


# =========================================================
# CONSULTAS DE REPORTES
# =========================================================

def reporte_ventas_mensuales_producto():
    fecha_col = obtener_columna_fecha("Venta", ["Fecha", "Fecha_Venta"])
    codigo_expr = obtener_expr_codigo_producto()
    total_expr = obtener_expr_total_venta()

    if fecha_col is None:
        return pd.DataFrame()

    query = f"""
        SELECT
            DATE_FORMAT(v.`{fecha_col}`, '%Y-%m') AS Mes,
            p.`Nombre` AS Producto,
            {codigo_expr} AS Codigo,
            COUNT(v.`Id_Venta`) AS `Registros de ventas`,
            COALESCE(SUM(v.`Cantidad`), 0) AS `Unidades vendidas`,
            COALESCE(SUM({total_expr}), 0) AS `Ingresos del mes`
        FROM Venta v
        INNER JOIN Producto p
            ON v.`Id_Producto` = p.`Id_Producto`
        GROUP BY
            DATE_FORMAT(v.`{fecha_col}`, '%Y-%m'),
            p.`Nombre`,
            {codigo_expr}
        ORDER BY
            Mes DESC,
            `Ingresos del mes` DESC
    """

    return ejecutar_dataframe(query)


def reporte_compras_mensuales_producto():
    fecha_col = obtener_columna_fecha("Compra", ["Fecha", "Fecha_Compra"])
    codigo_expr = obtener_expr_codigo_producto()
    total_expr = obtener_expr_total_compra()

    if fecha_col is None:
        return pd.DataFrame()

    query = f"""
        SELECT
            DATE_FORMAT(c.`{fecha_col}`, '%Y-%m') AS Mes,
            p.`Nombre` AS Producto,
            {codigo_expr} AS Codigo,
            COUNT(c.`Id_Compra`) AS `Registros de compras`,
            COALESCE(SUM(c.`Cantidad`), 0) AS `Unidades compradas`,
            COALESCE(SUM({total_expr}), 0) AS `Monto comprado`
        FROM Compra c
        INNER JOIN Producto p
            ON c.`Id_Producto` = p.`Id_Producto`
        GROUP BY
            DATE_FORMAT(c.`{fecha_col}`, '%Y-%m'),
            p.`Nombre`,
            {codigo_expr}
        ORDER BY
            Mes DESC,
            `Monto comprado` DESC
    """

    return ejecutar_dataframe(query)


def reporte_ventas_mensuales_resumen():
    fecha_col = obtener_columna_fecha("Venta", ["Fecha", "Fecha_Venta"])
    total_expr = obtener_expr_total_venta()

    if fecha_col is None:
        return pd.DataFrame()

    query = f"""
        SELECT
            DATE_FORMAT(v.`{fecha_col}`, '%Y-%m') AS Mes,
            COUNT(v.`Id_Venta`) AS `Registros de ventas`,
            COALESCE(SUM(v.`Cantidad`), 0) AS `Unidades vendidas`,
            COALESCE(SUM({total_expr}), 0) AS `Ingresos del mes`
        FROM Venta v
        INNER JOIN Producto p
            ON v.`Id_Producto` = p.`Id_Producto`
        GROUP BY DATE_FORMAT(v.`{fecha_col}`, '%Y-%m')
        ORDER BY Mes DESC
    """

    return ejecutar_dataframe(query)


def reporte_compras_mensuales_resumen():
    fecha_col = obtener_columna_fecha("Compra", ["Fecha", "Fecha_Compra"])
    total_expr = obtener_expr_total_compra()

    if fecha_col is None:
        return pd.DataFrame()

    query = f"""
        SELECT
            DATE_FORMAT(c.`{fecha_col}`, '%Y-%m') AS Mes,
            COUNT(c.`Id_Compra`) AS `Registros de compras`,
            COALESCE(SUM(c.`Cantidad`), 0) AS `Unidades compradas`,
            COALESCE(SUM({total_expr}), 0) AS `Monto comprado`
        FROM Compra c
        INNER JOIN Producto p
            ON c.`Id_Producto` = p.`Id_Producto`
        GROUP BY DATE_FORMAT(c.`{fecha_col}`, '%Y-%m')
        ORDER BY Mes DESC
    """

    return ejecutar_dataframe(query)


# =========================================================
# MÓDULO PRINCIPAL
# =========================================================

def mostrar_reportes():

    aplicar_estilo_reportes()

    st.markdown("""
        <div class="report-card">
            <div class="report-title">📊 Reportes e Inteligencia de Negocio</div>
            <div class="report-subtitle">
                Análisis de ventas, compras, inventario, productos destacados, baja rotación y comportamiento mensual.
            </div>
            <div class="gold-line"></div>
            <div class="info-box">
                Este módulo permite visualizar información estratégica para la toma de decisiones administrativas
                de Ferretería HELOIM.
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not tabla_existe("Producto"):
        st.error("No existe la tabla Producto. Verifique la base de datos.")
        return

    # =====================================================
    # RESUMEN EJECUTIVO
    # =====================================================

    st.markdown(
        '<div class="section-label">Resumen ejecutivo</div>',
        unsafe_allow_html=True
    )

    total_productos = obtener_valor("SELECT COUNT(*) FROM Producto") if tabla_existe("Producto") else 0
    total_proveedores = obtener_valor("SELECT COUNT(*) FROM Proveedor") if tabla_existe("Proveedor") else 0
    total_ventas_registros = obtener_valor("SELECT COUNT(*) FROM Venta") if tabla_existe("Venta") else 0
    total_compras_registros = obtener_valor("SELECT COUNT(*) FROM Compra") if tabla_existe("Compra") else 0

    df_ventas_resumen = reporte_ventas_mensuales_resumen() if tabla_existe("Venta") else pd.DataFrame()
    df_compras_resumen = reporte_compras_mensuales_resumen() if tabla_existe("Compra") else pd.DataFrame()

    ingresos_totales = 0
    compras_totales = 0

    if not df_ventas_resumen.empty:
        ingresos_totales = float(df_ventas_resumen["Ingresos del mes"].sum())

    if not df_compras_resumen.empty:
        compras_totales = float(df_compras_resumen["Monto comprado"].sum())

    resultado_estimado = ingresos_totales - compras_totales

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Productos registrados", total_productos)

    with col2:
        st.metric("Proveedores registrados", total_proveedores)

    with col3:
        st.metric("Registros de ventas", total_ventas_registros)

    with col4:
        st.metric("Registros de compras", total_compras_registros)

    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric("Ingresos por ventas", formatear_moneda(ingresos_totales))

    with col6:
        st.metric("Monto comprado", formatear_moneda(compras_totales))

    with col7:
        st.metric("Resultado estimado", formatear_moneda(resultado_estimado))

    st.divider()

    # =====================================================
    # VENTAS MENSUALES
    # =====================================================

    with st.expander("🧾 Ventas mensuales", expanded=True):

        if not tabla_existe("Venta"):
            st.info("Todavía no hay tabla de ventas registrada.")
        else:
            try:
                df_ventas_detalle = reporte_ventas_mensuales_producto()

                if df_ventas_detalle.empty:
                    st.info("Todavía no hay ventas registradas.")
                else:
                    df_mostrar = df_ventas_detalle.copy()
                    df_mostrar = df_mostrar.rename(columns={"Codigo": "Código"})
                    df_mostrar = formatear_columna_moneda(df_mostrar, "Ingresos del mes")

                    st.dataframe(
                        df_mostrar,
                        use_container_width=True,
                        hide_index=True
                    )

                    mejor = df_ventas_detalle.sort_values(
                        by="Ingresos del mes",
                        ascending=False
                    ).iloc[0]

                    st.success(
                        f"🏆 Producto con mayores ingresos en ventas: "
                        f"{mejor['Producto']} | Código: {mejor['Codigo']} | "
                        f"Mes: {mejor['Mes']} | Ingresos: {formatear_moneda(mejor['Ingresos del mes'])}."
                    )

            except Exception as e:
                st.error(f"Error al cargar ventas mensuales: {e}")

    # =====================================================
    # COMPRAS MENSUALES
    # =====================================================

    with st.expander("🧾 Compras mensuales", expanded=True):

        if not tabla_existe("Compra"):
            st.info("Todavía no hay tabla de compras registrada.")
        else:
            try:
                df_compras_detalle = reporte_compras_mensuales_producto()

                if df_compras_detalle.empty:
                    st.info("Todavía no hay compras registradas.")
                else:
                    df_mostrar = df_compras_detalle.copy()
                    df_mostrar = df_mostrar.rename(columns={"Codigo": "Código"})
                    df_mostrar = formatear_columna_moneda(df_mostrar, "Monto comprado")

                    st.dataframe(
                        df_mostrar,
                        use_container_width=True,
                        hide_index=True
                    )

                    mayor_compra = df_compras_detalle.sort_values(
                        by="Monto comprado",
                        ascending=False
                    ).iloc[0]

                    st.warning(
                        f"📦 Producto con mayor monto de compras: "
                        f"{mayor_compra['Producto']} | Código: {mayor_compra['Codigo']} | "
                        f"Mes: {mayor_compra['Mes']} | Monto: {formatear_moneda(mayor_compra['Monto comprado'])}."
                    )

            except Exception as e:
                st.error(f"Error al cargar compras mensuales: {e}")

    st.divider()

    # =====================================================
    # COMPARATIVO MENSUAL
    # =====================================================

    with st.expander("📈 Comparativo mensual ventas vs compras", expanded=False):

        try:
            df_ventas = reporte_ventas_mensuales_resumen() if tabla_existe("Venta") else pd.DataFrame()
            df_compras = reporte_compras_mensuales_resumen() if tabla_existe("Compra") else pd.DataFrame()

            if df_ventas.empty and df_compras.empty:
                st.info("Todavía no hay información mensual para comparar.")
            else:
                if df_ventas.empty:
                    df_ventas = pd.DataFrame(columns=["Mes", "Ingresos del mes"])

                if df_compras.empty:
                    df_compras = pd.DataFrame(columns=["Mes", "Monto comprado"])

                df_comparativo = pd.merge(
                    df_ventas[["Mes", "Ingresos del mes"]],
                    df_compras[["Mes", "Monto comprado"]],
                    on="Mes",
                    how="outer"
                ).fillna(0)

                df_comparativo["Resultado estimado"] = (
                    df_comparativo["Ingresos del mes"].astype(float)
                    - df_comparativo["Monto comprado"].astype(float)
                )

                df_comparativo = df_comparativo.sort_values(
                    by="Mes",
                    ascending=False
                )

                df_mostrar = df_comparativo.copy()
                df_mostrar = formatear_columna_moneda(df_mostrar, "Ingresos del mes")
                df_mostrar = formatear_columna_moneda(df_mostrar, "Monto comprado")
                df_mostrar = formatear_columna_moneda(df_mostrar, "Resultado estimado")

                st.dataframe(
                    df_mostrar,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error(f"Error al cargar comparativo mensual: {e}")

    # =====================================================
    # STOCK BAJO Y AGOTADO
    # =====================================================

    with st.expander("⚠️ Productos con stock bajo o agotado", expanded=False):

        try:
            columnas_producto = obtener_columnas("Producto")

            if "Stock_Minimo" in columnas_producto:
                stock_minimo_expr = "p.`Stock_Minimo`"
                filtro_stock = "p.`Stock` <= p.`Stock_Minimo`"
            else:
                stock_minimo_expr = "5"
                filtro_stock = "p.`Stock` <= 5"

            codigo_expr = obtener_expr_codigo_producto()

            categoria_expr = "p.`Categoria`" if "Categoria" in columnas_producto else "'Sin categoría'"

            query = f"""
                SELECT
                    p.`Nombre` AS Producto,
                    {codigo_expr} AS Codigo,
                    {categoria_expr} AS Categoria,
                    p.`Stock` AS Stock,
                    {stock_minimo_expr} AS `Stock mínimo`,
                    CASE
                        WHEN p.`Stock` = 0 THEN 'Agotado'
                        WHEN {filtro_stock} THEN 'Stock bajo'
                        ELSE 'Disponible'
                    END AS Estado
                FROM Producto p
                WHERE p.`Stock` = 0 OR {filtro_stock}
                ORDER BY p.`Stock` ASC
            """

            df_stock = ejecutar_dataframe(query)

            if df_stock.empty:
                st.success("No hay productos con stock bajo o agotado.")
            else:
                df_stock = df_stock.rename(columns={"Codigo": "Código"})

                st.dataframe(
                    df_stock,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error(f"Error al cargar stock bajo: {e}")

    # =====================================================
    # TOP PRODUCTOS VENDIDOS
    # =====================================================

    with st.expander("🏆 Productos más vendidos", expanded=False):

        if not tabla_existe("Venta"):
            st.info("Todavía no hay ventas registradas.")
        else:
            try:
                codigo_expr = obtener_expr_codigo_producto()
                total_expr = obtener_expr_total_venta()

                query = f"""
                    SELECT
                        p.`Nombre` AS Producto,
                        {codigo_expr} AS Codigo,
                        COUNT(v.`Id_Venta`) AS `Registros de ventas`,
                        COALESCE(SUM(v.`Cantidad`), 0) AS `Unidades vendidas`,
                        COALESCE(SUM({total_expr}), 0) AS `Ingresos generados`
                    FROM Venta v
                    INNER JOIN Producto p
                        ON v.`Id_Producto` = p.`Id_Producto`
                    GROUP BY
                        p.`Nombre`,
                        {codigo_expr}
                    ORDER BY
                        `Unidades vendidas` DESC,
                        `Ingresos generados` DESC
                    LIMIT 10
                """

                df_top = ejecutar_dataframe(query)

                if df_top.empty:
                    st.info("Todavía no hay productos vendidos.")
                else:
                    df_top = df_top.rename(columns={"Codigo": "Código"})
                    df_top = formatear_columna_moneda(df_top, "Ingresos generados")

                    st.dataframe(
                        df_top,
                        use_container_width=True,
                        hide_index=True
                    )

            except Exception as e:
                st.error(f"Error al cargar productos más vendidos: {e}")

    # =====================================================
    # PRODUCTOS DE BAJA ROTACIÓN
    # =====================================================

    with st.expander("🐢 Productos de baja rotación", expanded=False):

        try:
            codigo_expr = obtener_expr_codigo_producto()

            query = f"""
                SELECT
                    p.`Nombre` AS Producto,
                    {codigo_expr} AS Codigo,
                    p.`Stock` AS Stock,
                    COALESCE(SUM(v.`Cantidad`), 0) AS `Unidades vendidas`
                FROM Producto p
                LEFT JOIN Venta v
                    ON p.`Id_Producto` = v.`Id_Producto`
                GROUP BY
                    p.`Nombre`,
                    {codigo_expr},
                    p.`Stock`
                ORDER BY
                    `Unidades vendidas` ASC,
                    p.`Stock` DESC
                LIMIT 10
            """

            df_baja = ejecutar_dataframe(query)

            if df_baja.empty:
                st.info("No hay productos para analizar.")
            else:
                df_baja = df_baja.rename(columns={"Codigo": "Código"})

                st.dataframe(
                    df_baja,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error(f"Error al cargar productos de baja rotación: {e}")

    # =====================================================
    # VENTAS POR MÉTODO DE PAGO
    # =====================================================

    with st.expander("💳 Ventas por método de pago", expanded=False):

        if not tabla_existe("Venta"):
            st.info("Todavía no hay ventas registradas.")
        else:
            try:
                columnas_venta = obtener_columnas("Venta")
                total_expr = obtener_expr_total_venta()

                metodo_expr = "COALESCE(v.`Metodo_Pago`, 'No especificado')" if "Metodo_Pago" in columnas_venta else "'No especificado'"

                query = f"""
                    SELECT
                        {metodo_expr} AS `Método de pago`,
                        COUNT(v.`Id_Venta`) AS `Registros de ventas`,
                        COALESCE(SUM(v.`Cantidad`), 0) AS `Unidades vendidas`,
                        COALESCE(SUM({total_expr}), 0) AS `Ingresos`
                    FROM Venta v
                    INNER JOIN Producto p
                        ON v.`Id_Producto` = p.`Id_Producto`
                    GROUP BY {metodo_expr}
                    ORDER BY `Ingresos` DESC
                """

                df_metodo = ejecutar_dataframe(query)

                if df_metodo.empty:
                    st.info("No hay ventas para analizar.")
                else:
                    df_metodo = formatear_columna_moneda(df_metodo, "Ingresos")

                    st.dataframe(
                        df_metodo,
                        use_container_width=True,
                        hide_index=True
                    )

            except Exception as e:
                st.error(f"Error al cargar ventas por método de pago: {e}")

    # =====================================================
    # COMPRAS POR PROVEEDOR
    # =====================================================

    with st.expander("🚚 Compras por proveedor", expanded=False):

        if not tabla_existe("Compra"):
            st.info("Todavía no hay compras registradas.")
        else:
            try:
                columnas_compra = obtener_columnas("Compra")
                columnas_proveedor = obtener_columnas("Proveedor")

                if tabla_existe("Proveedor") and "Id_Proveedor" in columnas_compra and "Id_Proveedor" in columnas_proveedor:

                    nombre_proveedor = "Nombre" if "Nombre" in columnas_proveedor else columnas_proveedor[1]
                    total_expr = obtener_expr_total_compra()

                    query = f"""
                        SELECT
                            COALESCE(pr.`{nombre_proveedor}`, 'Proveedor no especificado') AS Proveedor,
                            COUNT(c.`Id_Compra`) AS `Registros de compras`,
                            COALESCE(SUM(c.`Cantidad`), 0) AS `Unidades compradas`,
                            COALESCE(SUM({total_expr}), 0) AS `Monto comprado`
                        FROM Compra c
                        LEFT JOIN Proveedor pr
                            ON c.`Id_Proveedor` = pr.`Id_Proveedor`
                        INNER JOIN Producto p
                            ON c.`Id_Producto` = p.`Id_Producto`
                        GROUP BY COALESCE(pr.`{nombre_proveedor}`, 'Proveedor no especificado')
                        ORDER BY `Monto comprado` DESC
                    """

                else:
                    total_expr = obtener_expr_total_compra()

                    query = f"""
                        SELECT
                            'Proveedor no especificado' AS Proveedor,
                            COUNT(c.`Id_Compra`) AS `Registros de compras`,
                            COALESCE(SUM(c.`Cantidad`), 0) AS `Unidades compradas`,
                            COALESCE(SUM({total_expr}), 0) AS `Monto comprado`
                        FROM Compra c
                        INNER JOIN Producto p
                            ON c.`Id_Producto` = p.`Id_Producto`
                    """

                df_proveedor = ejecutar_dataframe(query)

                if df_proveedor.empty:
                    st.info("No hay compras para analizar.")
                else:
                    df_proveedor = formatear_columna_moneda(df_proveedor, "Monto comprado")

                    st.dataframe(
                        df_proveedor,
                        use_container_width=True,
                        hide_index=True
                    )

            except Exception as e:
                st.error(f"Error al cargar compras por proveedor: {e}")

    # =====================================================
    # INVENTARIO POR CATEGORÍA
    # =====================================================

    with st.expander("📦 Inventario por categoría", expanded=False):

        try:
            columnas_producto = obtener_columnas("Producto")

            if "Categoria" in columnas_producto:

                query = """
                    SELECT
                        COALESCE(`Categoria`, 'Sin categoría') AS Categoría,
                        COUNT(*) AS `Productos registrados`,
                        COALESCE(SUM(`Stock`), 0) AS `Unidades en inventario`
                    FROM Producto
                    GROUP BY COALESCE(`Categoria`, 'Sin categoría')
                    ORDER BY `Unidades en inventario` DESC
                """

            else:
                query = """
                    SELECT
                        'Sin categoría' AS Categoría,
                        COUNT(*) AS `Productos registrados`,
                        COALESCE(SUM(`Stock`), 0) AS `Unidades en inventario`
                    FROM Producto
                """

            df_categoria = ejecutar_dataframe(query)

            if df_categoria.empty:
                st.info("No hay inventario para analizar.")
            else:
                st.dataframe(
                    df_categoria,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error(f"Error al cargar inventario por categoría: {e}")
