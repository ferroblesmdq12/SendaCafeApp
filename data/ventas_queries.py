# data/ventas_queries.py

from data.db import run_query_df, get_connection

# =========================
# KPIs / Dashboard general
# =========================

def get_ventas_hoy():
    query = """
        SELECT COALESCE(SUM(total_ticket), 0) AS total
        FROM ventas
        WHERE fecha_hora::date = CURRENT_DATE;
    """
    return run_query_df(query)["total"].iloc[0]


def get_ventas_mes():
    query = """
        SELECT COALESCE(SUM(total_ticket), 0) AS total
        FROM ventas
        WHERE DATE_TRUNC('month', fecha_hora) = DATE_TRUNC('month', CURRENT_DATE);
    """
    return run_query_df(query)["total"].iloc[0]


def get_ticket_promedio_mes():
    query = """
        SELECT COALESCE(AVG(total_ticket), 0) AS ticket_promedio
        FROM ventas
        WHERE DATE_TRUNC('month', fecha_hora) = DATE_TRUNC('month', CURRENT_DATE);
    """
    return run_query_df(query)["ticket_promedio"].iloc[0]


def get_unidades_mes():
    query = """
        SELECT COALESCE(SUM(vd.cantidad), 0) AS unidades
        FROM ventas_detalle vd
        JOIN ventas v ON v.id_venta = vd.id_venta
        WHERE DATE_TRUNC('month', v.fecha_hora) = DATE_TRUNC('month', CURRENT_DATE);
    """
    return run_query_df(query)["unidades"].iloc[0]


def get_ventas_ultimos_30_dias():
    query = """
        SELECT DATE(fecha_hora) AS fecha,
               SUM(total_ticket) AS total
        FROM ventas
        WHERE fecha_hora >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(fecha_hora)
        ORDER BY fecha;
    """
    return run_query_df(query)


def get_ultimas_ventas(limit=50):
    query = f"""
        SELECT id_venta, fecha_hora, servicio, total_ticket
        FROM ventas
        ORDER BY fecha_hora DESC
        LIMIT {limit};
    """
    return run_query_df(query)


def get_top_productos_mes(limit=5):
    query = f"""
        SELECT 
            p.nombre AS producto,
            SUM(vd.cantidad) AS unidades,
            SUM(vd.subtotal) AS total
        FROM ventas_detalle vd
        JOIN ventas v ON v.id_venta = vd.id_venta
        JOIN productos p ON p.id_producto = vd.id_producto
        WHERE DATE_TRUNC('month', v.fecha_hora) = DATE_TRUNC('month', CURRENT_DATE)
        GROUP BY p.nombre
        ORDER BY unidades DESC
        LIMIT {limit};
    """
    return run_query_df(query)


def get_ventas_por_dia_ultimos_30():
    query = """
        SELECT 
            DATE(fecha_hora) AS fecha,
            SUM(total_ticket) AS total
        FROM ventas
        WHERE fecha_hora >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(fecha_hora)
        ORDER BY fecha;
    """
    return run_query_df(query)


def get_stock_critico():
    """
    Productos con stock en o por debajo del mínimo,
    usando la tabla stock + productos.
    """
    query = """
        SELECT 
            p.nombre,
            s.stock_actual,
            s.stock_minimo
        FROM stock s
        JOIN productos p ON p.id_producto = s.id_producto
        WHERE s.stock_actual <= s.stock_minimo
        ORDER BY s.stock_actual ASC;
    """
    return run_query_df(query)


# =========================
# Productos, empleados, stock
# =========================

def get_productos_con_stock():
    """
    Devuelve productos con su stock actual y mínimo.
    """
    query = """
        SELECT 
            p.id_producto,
            p.nombre,
            p.precio_venta,
            s.stock_actual,
            s.stock_minimo
        FROM productos p
        JOIN stock s ON s.id_producto = p.id_producto
        WHERE p.activo = TRUE
        ORDER BY p.nombre;
    """
    return run_query_df(query)


def get_empleados_activos():
    """
    Empleados activos, para seleccionar camarero/barista.
    """
    query = """
        SELECT 
            id_empleado,
            nombre,
            rol
        FROM empleados
        WHERE activo = TRUE
        ORDER BY nombre;
    """
    return run_query_df(query)


def get_stock_resumen():
    """
    Resumen de stock actual por producto.
    """
    query = """
        SELECT 
            p.id_producto,
            p.nombre,
            s.stock_actual,
            s.stock_minimo
        FROM stock s
        JOIN productos p ON p.id_producto = s.id_producto
        ORDER BY p.nombre;
    """
    return run_query_df(query)


# =========================
# Registrar venta completa
# =========================

def registrar_venta_completa(fecha_hora, servicio, id_empleado, metodo_pago, items, id_usuario=None, ticket_id_origen=None):
    """
    Registra una venta completa:
      - Insert en ventas
      - Inserts en ventas_detalle
      - Descuenta stock en tabla stock
      - Inserta movimientos_stock por cada producto

    items = lista de dicts:
      [
        {"id_producto": 1, "cantidad": 2, "precio_unitario": 1500.0},
        ...
      ]
    """
    total_ticket = sum(i["cantidad"] * i["precio_unitario"] for i in items)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1) Insert en ventas
            cur.execute(
                """
                INSERT INTO ventas (
                    ticket_id_origen,
                    fecha_hora,
                    servicio,
                    id_empleado,
                    metodo_pago,
                    total_ticket
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_venta;
                """,
                (ticket_id_origen, fecha_hora, servicio, id_empleado, metodo_pago, total_ticket)
            )
            id_venta = cur.fetchone()[0]

            # 2) Detalles + stock + movimientos
            for item in items:
                id_prod = item["id_producto"]
                cant = int(item["cantidad"])
                precio = float(item["precio_unitario"])
                subtotal = cant * precio

                # 2.a) Insert detalle
                cur.execute(
                    """
                    INSERT INTO ventas_detalle (
                        id_venta, id_producto, cantidad, precio_unitario, subtotal
                    )
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (id_venta, id_prod, cant, precio, subtotal)
                )

                # 2.b) Descuento de stock
                cur.execute(
                    """
                    UPDATE stock
                    SET stock_actual = stock_actual - %s,
                        actualizado_en = NOW()
                    WHERE id_producto = %s;
                    """,
                    (cant, id_prod)
                )

                # 2.c) Movimiento de stock (venta: cantidad negativa)
                cur.execute(
                    """
                    INSERT INTO movimientos_stock (
                        id_producto,
                        fecha_hora,
                        tipo_movimiento,
                        cantidad,
                        comentario,
                        creado_por
                    )
                    VALUES (%s, NOW(), %s, %s, %s, %s);
                    """,
                    (
                        id_prod,
                        "VENTA",
                        -cant,
                        f"Venta {id_venta}",
                        id_usuario
                    )
                )

            conn.commit()

        return id_venta, total_ticket

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


# =========================
# Entradas de stock
# =========================

def registrar_entrada_stock(id_producto, cantidad, comentario=None, id_usuario=None, tipo_movimiento="ENTRADA"):
    """
    Registra una entrada de stock (compra, ajuste positivo).
    Suma al stock_actual y agrega un movimiento_stock.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Actualizar stock
            cur.execute(
                """
                UPDATE stock
                SET stock_actual = stock_actual + %s,
                    actualizado_en = NOW()
                WHERE id_producto = %s;
                """,
                (cantidad, id_producto)
            )

            # Movimiento
            cur.execute(
                """
                INSERT INTO movimientos_stock (
                    id_producto,
                    fecha_hora,
                    tipo_movimiento,
                    cantidad,
                    comentario,
                    creado_por
                )
                VALUES (%s, NOW(), %s, %s, %s, %s);
                """,
                (
                    id_producto,
                    tipo_movimiento,
                    cantidad,  # entrada: positiva
                    comentario,
                    id_usuario
                )
            )

            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# =========================
# Ventas filtradas (fecha / producto / empleado)
# =========================

from datetime import timedelta

def _build_in_clause(field: str, values: list, params: list):
    """
    Construye un IN dinámico seguro: field IN (%s, %s, ...)
    y agrega values a params.
    Devuelve el SQL (string) para concatenar al WHERE.
    """
    if not values:
        return ""
    placeholders = ", ".join(["%s"] * len(values))
    params.extend(values)
    return f" AND {field} IN ({placeholders}) "

def get_catalogo_productos_activos():
    """
    Catálogo simple para el filtro (no requiere stock).
    """
    query = """
        SELECT id_producto, nombre
        FROM productos
        WHERE activo = TRUE
        ORDER BY nombre;
    """
    return run_query_df(query)

def get_ventas_resumen_filtrado(date_from, date_to, empleados=None, productos=None):
    """
    Resumen por día: ventas_total y tickets, filtrando por:
    - rango de fechas (incluye date_to)
    - empleados (opcional)
    - productos (opcional) usando EXISTS para NO duplicar tickets
    """
    empleados = empleados or []
    productos = productos or []

    date_to_plus1 = date_to + timedelta(days=1)

    params = [date_from, date_to_plus1]
    where_extra = ""

    # filtro empleados (sobre cabecera)
    where_extra += _build_in_clause("v.id_empleado", empleados, params)

    # filtro productos (por existencia en detalle)
    if productos:
        placeholders = ", ".join(["%s"] * len(productos))
        params.extend(productos)
        where_extra += f"""
            AND EXISTS (
                SELECT 1
                FROM ventas_detalle vd
                WHERE vd.id_venta = v.id_venta
                  AND vd.id_producto IN ({placeholders})
            )
        """

    query = f"""
        SELECT
            DATE(v.fecha_hora) AS dia,
            SUM(v.total_ticket) AS ventas_total,
            COUNT(*) AS tickets
        FROM ventas v
        WHERE v.fecha_hora >= %s
          AND v.fecha_hora <  %s
          {where_extra}
        GROUP BY 1
        ORDER BY 1;
    """
    return run_query_df(query, params=params)

def get_tickets_filtrados(date_from, date_to, empleados=None, productos=None, limit=5000):
    """
    Tickets (cabecera) filtrados. Usa EXISTS para productos para evitar duplicados.
    """
    empleados = empleados or []
    productos = productos or []

    date_to_plus1 = date_to + timedelta(days=1)

    params = [date_from, date_to_plus1]
    where_extra = ""

    where_extra += _build_in_clause("v.id_empleado", empleados, params)

    if productos:
        placeholders = ", ".join(["%s"] * len(productos))
        params.extend(productos)
        where_extra += f"""
            AND EXISTS (
                SELECT 1
                FROM ventas_detalle vd
                WHERE vd.id_venta = v.id_venta
                  AND vd.id_producto IN ({placeholders})
            )
        """

    query = f"""
        SELECT
            v.id_venta,
            v.fecha_hora,
            e.nombre AS empleado,
            v.servicio,
            v.metodo_pago,
            v.total_ticket
        FROM ventas v
        LEFT JOIN empleados e ON e.id_empleado = v.id_empleado
        WHERE v.fecha_hora >= %s
          AND v.fecha_hora <  %s
          {where_extra}
        ORDER BY v.fecha_hora DESC
        LIMIT {int(limit)};
    """
    return run_query_df(query, params=params)

def get_top_productos_filtrado(date_from, date_to, empleados=None, productos=None, limit=10):
    """
    Top productos por unidades y total dentro del período y filtros.
    Si se selecciona productos en el filtro, restringe a esos productos.
    """
    empleados = empleados or []
    productos = productos or []

    date_to_plus1 = date_to + timedelta(days=1)

    params = [date_from, date_to_plus1]
    where_extra = ""

    where_extra += _build_in_clause("v.id_empleado", empleados, params)
    where_extra += _build_in_clause("vd.id_producto", productos, params)

    query = f"""
        SELECT
            p.nombre AS producto,
            SUM(vd.cantidad) AS unidades,
            SUM(vd.subtotal) AS total
        FROM ventas_detalle vd
        JOIN ventas v ON v.id_venta = vd.id_venta
        JOIN productos p ON p.id_producto = vd.id_producto
        WHERE v.fecha_hora >= %s
          AND v.fecha_hora <  %s
          {where_extra}
        GROUP BY p.nombre
        ORDER BY unidades DESC
        LIMIT {int(limit)};
    """
    return run_query_df(query, params=params)

def get_top_empleados_filtrado(date_from, date_to, empleados=None, productos=None, limit=10):
    """
    Top empleados por ventas, respetando filtro de productos vía EXISTS.
    """
    empleados = empleados or []
    productos = productos or []

    date_to_plus1 = date_to + timedelta(days=1)

    params = [date_from, date_to_plus1]
    where_extra = ""

    where_extra += _build_in_clause("v.id_empleado", empleados, params)

    if productos:
        placeholders = ", ".join(["%s"] * len(productos))
        params.extend(productos)
        where_extra += f"""
            AND EXISTS (
                SELECT 1
                FROM ventas_detalle vd
                WHERE vd.id_venta = v.id_venta
                  AND vd.id_producto IN ({placeholders})
            )
        """

    query = f"""
        SELECT
            COALESCE(e.nombre, 'Sin empleado') AS empleado,
            SUM(v.total_ticket) AS total
        FROM ventas v
        LEFT JOIN empleados e ON e.id_empleado = v.id_empleado
        WHERE v.fecha_hora >= %s
          AND v.fecha_hora <  %s
          {where_extra}
        GROUP BY 1
        ORDER BY total DESC
        LIMIT {int(limit)};
    """
    return run_query_df(query, params=params)



# =========================
# Empleados (performance)
# =========================

from datetime import timedelta

def get_empleados_ranking_filtrado(date_from, date_to, productos=None, limit=20):
    """
    Ranking de empleados por ventas, tickets y ticket promedio.
    Filtra por productos (opcional) usando EXISTS para no duplicar tickets.
    """
    productos = productos or []
    date_to_plus1 = date_to + timedelta(days=1)

    params = [date_from, date_to_plus1]
    where_extra = ""

    if productos:
        placeholders = ", ".join(["%s"] * len(productos))
        params.extend(productos)
        where_extra += f"""
            AND EXISTS (
                SELECT 1
                FROM ventas_detalle vd
                WHERE vd.id_venta = v.id_venta
                  AND vd.id_producto IN ({placeholders})
            )
        """

    query = f"""
        SELECT
            e.id_empleado,
            e.nombre AS empleado,
            e.rol,
            SUM(v.total_ticket) AS ventas_total,
            COUNT(*) AS tickets,
            (SUM(v.total_ticket) / NULLIF(COUNT(*), 0)) AS ticket_promedio
        FROM ventas v
        LEFT JOIN empleados e ON e.id_empleado = v.id_empleado
        WHERE v.fecha_hora >= %s
          AND v.fecha_hora <  %s
          {where_extra}
        GROUP BY e.id_empleado, e.nombre, e.rol
        ORDER BY ventas_total DESC
        LIMIT {int(limit)};
    """
    return run_query_df(query, params=params)

def get_empleado_resumen_filtrado(date_from, date_to, id_empleado, productos=None):
    """
    KPIs de un empleado específico: ventas, tickets, ticket promedio, unidades.
    Unidades requiere join con ventas_detalle.
    """
    productos = productos or []
    date_to_plus1 = date_to + timedelta(days=1)

    params = [date_from, date_to_plus1, id_empleado]
    where_extra = ""

    # filtro por productos (opcional) sobre tickets
    if productos:
        placeholders = ", ".join(["%s"] * len(productos))
        params.extend(productos)
        where_extra += f"""
            AND EXISTS (
                SELECT 1
                FROM ventas_detalle vd
                WHERE vd.id_venta = v.id_venta
                  AND vd.id_producto IN ({placeholders})
            )
        """

    query = f"""
        SELECT
            COALESCE(SUM(v.total_ticket), 0) AS ventas_total,
            COALESCE(COUNT(*), 0) AS tickets,
            COALESCE(AVG(v.total_ticket), 0) AS ticket_promedio,
            COALESCE((
                SELECT SUM(vd.cantidad)
                FROM ventas_detalle vd
                JOIN ventas v2 ON v2.id_venta = vd.id_venta
                WHERE v2.fecha_hora >= %s
                  AND v2.fecha_hora <  %s
                  AND v2.id_empleado = %s
            ), 0) AS unidades
        FROM ventas v
        WHERE v.fecha_hora >= %s
          AND v.fecha_hora <  %s
          AND v.id_empleado = %s
          {where_extra};
    """
    # Nota: reuso de params en subquery + query principal:
    # params debe tener [from,to,emp, from,to,emp] + productos(opcional) para EXISTS.
    # Para simplificar, armamos params duplicados:
    params_base = [date_from, date_to_plus1, id_empleado, date_from, date_to_plus1, id_empleado]
    if productos:
        params = params_base + productos
    else:
        params = params_base

    return run_query_df(query, params=params)

def get_empleado_ventas_por_dia(date_from, date_to, id_empleado, productos=None):
    """
    Serie temporal por día para un empleado. Filtro de productos opcional vía EXISTS.
    """
    productos = productos or []
    date_to_plus1 = date_to + timedelta(days=1)

    params = [date_from, date_to_plus1, id_empleado]
    where_extra = ""

    if productos:
        placeholders = ", ".join(["%s"] * len(productos))
        params.extend(productos)
        where_extra += f"""
            AND EXISTS (
                SELECT 1
                FROM ventas_detalle vd
                WHERE vd.id_venta = v.id_venta
                  AND vd.id_producto IN ({placeholders})
            )
        """

    query = f"""
        SELECT
            DATE(v.fecha_hora) AS dia,
            SUM(v.total_ticket) AS ventas_total,
            COUNT(*) AS tickets
        FROM ventas v
        WHERE v.fecha_hora >= %s
          AND v.fecha_hora <  %s
          AND v.id_empleado = %s
          {where_extra}
        GROUP BY 1
        ORDER BY 1;
    """
    return run_query_df(query, params=params)

def get_empleado_top_productos(date_from, date_to, id_empleado, limit=10):
    """
    Top productos para un empleado dentro del período.
    """
    date_to_plus1 = date_to + timedelta(days=1)
    params = [date_from, date_to_plus1, id_empleado]

    query = f"""
        SELECT
            p.nombre AS producto,
            SUM(vd.cantidad) AS unidades,
            SUM(vd.subtotal) AS total
        FROM ventas_detalle vd
        JOIN ventas v ON v.id_venta = vd.id_venta
        JOIN productos p ON p.id_producto = vd.id_producto
        WHERE v.fecha_hora >= %s
          AND v.fecha_hora <  %s
          AND v.id_empleado = %s
        GROUP BY p.nombre
        ORDER BY unidades DESC
        LIMIT {int(limit)};
    """
    return run_query_df(query, params=params)


# =========================
# Ganancias (Ventas - Costos)
# =========================

def get_costos_fijos_total_filtrado(date_from, date_to):
    """
    Total de costos fijos en el rango. Asume tabla costos_fijos(fecha, monto, ...).
    Si tu tabla se llama distinto o tiene periodo, lo ajustamos.
    """
    date_to_plus1 = date_to + timedelta(days=1)
    params = [date_from, date_to_plus1]

    query = """
        SELECT COALESCE(SUM(monto), 0) AS costos_total
        FROM costos_fijos
        WHERE fecha >= %s
          AND fecha <  %s;
    """
    return run_query_df(query, params=params)["costos_total"].iloc[0]

def get_costos_fijos_por_dia(date_from, date_to):
    """
    Costos por día (si tu tabla registra fecha por imputación).
    """
    date_to_plus1 = date_to + timedelta(days=1)
    params = [date_from, date_to_plus1]

    query = """
        SELECT
            DATE(fecha) AS dia,
            SUM(monto) AS costos_total
        FROM costos_fijos
        WHERE fecha >= %s
          AND fecha <  %s
        GROUP BY 1
        ORDER BY 1;
    """
    return run_query_df(query, params=params)

def get_ganancias_por_dia(date_from, date_to):
    """
    Une ventas por día con costos por día y calcula ganancia.
    """
    df_v = get_ventas_resumen_filtrado(date_from, date_to, empleados=[], productos=[])
    df_c = get_costos_fijos_por_dia(date_from, date_to)

    if df_v.empty and df_c.empty:
        return df_v  # vacío

    # normalizar columnas
    if df_v.empty:
        df_v = df_c[["dia"]].copy()
        df_v["ventas_total"] = 0
        df_v["tickets"] = 0

    if df_c.empty:
        df_c = df_v[["dia"]].copy()
        df_c["costos_total"] = 0

    df = df_v.merge(df_c, on="dia", how="outer").fillna(0)
    df["ganancia"] = df["ventas_total"] - df["costos_total"]
    return df.sort_values("dia")

def get_costos_fijos_total_filtrado(date_from, date_to):
    date_to_plus1 = date_to + timedelta(days=1)
    params = [date_from, date_to_plus1]
    query = """
        SELECT COALESCE(SUM(monto_ars), 0) AS costos_total
        FROM costos_fijos
        WHERE activo = TRUE
          AND fecha >= %s
          AND fecha <  %s;
    """
    return run_query_df(query, params=params)["costos_total"].iloc[0]

def get_costos_fijos_por_dia(date_from, date_to):
    date_to_plus1 = date_to + timedelta(days=1)
    params = [date_from, date_to_plus1]
    query = """
        SELECT
            fecha AS dia,
            SUM(monto_ars) AS costos_total
        FROM costos_fijos
        WHERE activo = TRUE
          AND fecha >= %s
          AND fecha <  %s
        GROUP BY 1
        ORDER BY 1;
    """
    return run_query_df(query, params=params)
