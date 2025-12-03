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
