# ventas_queries.py

from data.db import run_query_df


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
    Asumo columnas: productos(nombre, stock_actual, stock_minimo).
    Si se llaman distinto, solo cambiá los nombres en el SELECT.
    """
    query = """
        SELECT 
            nombre,
            stock_actual,
            stock_minimo
        FROM productos
        WHERE stock_actual <= stock_minimo
        ORDER BY stock_actual ASC;
    """
    return run_query_df(query)