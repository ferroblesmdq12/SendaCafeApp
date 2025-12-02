from data.db import run_query_df


def get_ventas_hoy():
    """
    Suma del total_ticket de las ventas realizadas HOY.
    """
    query = """
        SELECT COALESCE(SUM(total_ticket), 0) AS total
        FROM ventas
        WHERE fecha_hora::date = CURRENT_DATE;
    """
    df = run_query_df(query)
    return float(df["total"].iloc[0])


def get_ventas_mes():
    """
    Suma del total_ticket del mes actual.
    """
    query = """
        SELECT COALESCE(SUM(total_ticket), 0) AS total
        FROM ventas
        WHERE DATE_TRUNC('month', fecha_hora) = DATE_TRUNC('month', CURRENT_DATE);
    """
    df = run_query_df(query)
    return float(df["total"].iloc[0])


def get_ticket_promedio_mes():
    """
    Ticket promedio del mes actual (promedio de total_ticket).
    """
    query = """
        SELECT COALESCE(AVG(total_ticket), 0) AS ticket_promedio
        FROM ventas
        WHERE DATE_TRUNC('month', fecha_hora) = DATE_TRUNC('month', CURRENT_DATE);
    """
    df = run_query_df(query)
    return float(df["ticket_promedio"].iloc[0])


def get_unidades_mes():
    """
    Unidades totales vendidas en el mes actual (suma de ventas_detalle.cantidad).
    """
    query = """
        SELECT COALESCE(SUM(vd.cantidad), 0) AS unidades
        FROM ventas_detalle vd
        JOIN ventas v ON v.id_venta = vd.id_venta
        WHERE DATE_TRUNC('month', v.fecha_hora) = DATE_TRUNC('month', CURRENT_DATE);
    """
    df = run_query_df(query)
    return int(df["unidades"].iloc[0])


def get_ventas_ultimos_30_dias():
    """
    Ventas diarias (total_ticket) de los últimos 30 días.
    """
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


def get_ultimas_ventas(limit: int = 50):
    """
    Últimas N ventas ordenadas por fecha_hora descendente.
    """
    query = f"""
        SELECT
            id_venta,
            fecha_hora,
            servicio,
            id_empleado,
            metodo_pago,
            total_ticket
        FROM ventas
        ORDER BY fecha_hora DESC
        LIMIT {limit};
    """
    return run_query_df(query)
