-- Ventas por día
SELECT DATE(fecha_hora) AS fecha,
       COUNT(*) AS cant_tickets,
       SUM(total_ticket) AS facturacion
FROM ventas
GROUP BY DATE(fecha_hora)
ORDER BY fecha;

-- Top 10 productos más vendidos
SELECT p.nombre,
       SUM(d.cantidad) AS unidades_vendidas,
       SUM(d.subtotal) AS ingreso_total
FROM ventas_detalle d
JOIN productos p ON d.id_producto = p.id_producto
GROUP BY p.nombre
ORDER BY unidades_vendidas DESC
LIMIT 10;


INSERT INTO stock (id_producto, stock_actual, stock_minimo)
SELECT p.id_producto, 0, 10
FROM productos p
LEFT JOIN stock s ON s.id_producto = p.id_producto
WHERE s.id_producto IS NULL;

UPDATE stock s
SET stock_actual = GREATEST(
        0,
        s.stock_actual - COALESCE(v.cant_vendida, 0)
    ),
    actualizado_en = NOW()
FROM (
    SELECT id_producto, SUM(cantidad) AS cant_vendida
    FROM ventas_detalle
    GROUP BY id_producto
) v
WHERE s.id_producto = v.id_producto;


SELECT p.nombre, s.stock_actual, s.stock_minimo
FROM stock s
JOIN productos p ON p.id_producto = s.id_producto
ORDER BY p.nombre;
