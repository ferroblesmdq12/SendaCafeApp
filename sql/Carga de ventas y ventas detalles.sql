DO $$
DECLARE
    start_date date := DATE '2025-05-15';
    end_date   date := DATE '2025-11-28';
    d          date;
    dow        int;
    tickets_day int;
    i          int;
    j          int;
    n_items    int;
    v_id_venta int;
    v_emp_id   int;
    v_metodo   text;
    v_servicio text;
    r_cat      float8;
    r_pay      float8;
    r_serv     float8;
    random_time time;
    v_prod_id  int;
    v_qty      int;
    v_price    numeric(12,2);
    v_total    numeric(12,2);
BEGIN
    d := start_date;
    WHILE d <= end_date LOOP
        dow := extract(dow FROM d);  -- 0=domingo, 1=lunes, ... 6=sábado

        -- tickets por día según el día de la semana (aleatorio dentro de un rango)
        IF dow IN (1,2,3) THEN          -- Lunes, Martes, Miércoles
            tickets_day := 35 + floor(random() * 26);   -- 35 a 60
        ELSIF dow = 4 THEN              -- Jueves
            tickets_day := 40 + floor(random() * 21);   -- 40 a 60
        ELSIF dow = 5 THEN              -- Viernes
            tickets_day := 50 + floor(random() * 31);   -- 50 a 80
        ELSIF dow = 6 THEN              -- Sábado
            tickets_day := 70 + floor(random() * 41);   -- 70 a 110
        ELSE                            -- Domingo (0)
            tickets_day := 60 + floor(random() * 31);   -- 60 a 90
        END IF;

        FOR i IN 1..tickets_day LOOP
            -- elegir camarero al azar
            SELECT id_empleado
            INTO v_emp_id
            FROM empleados
            WHERE lower(rol) LIKE 'camarero%'
            ORDER BY random()
            LIMIT 1;

            -- hora aleatoria entre 08:00 y 23:00
            random_time := time '08:00' + (random() * interval '15 hours');

            -- servicio
            r_serv := random();
            IF r_serv < 0.7 THEN
                v_servicio := 'salón';
            ELSE
                v_servicio := 'take away';
            END IF;

            -- método de pago
            r_pay := random();
            IF r_pay < 0.30 THEN
                v_metodo := 'Efectivo';
            ELSIF r_pay < 0.70 THEN
                v_metodo := 'Tarjeta';
            ELSE
                v_metodo := 'MercadoPago';
            END IF;

            v_total := 0;

            -- insertar cabecera de venta con total 0 (después se actualiza)
            INSERT INTO ventas (ticket_id_origen, fecha_hora, servicio, id_empleado, metodo_pago, total_ticket)
            VALUES (
                NULL,
                d::timestamp + random_time,
                v_servicio,
                v_emp_id,
                v_metodo,
                0
            )
            RETURNING id_venta INTO v_id_venta;

            -- ítems por ticket (1 a 4)
            n_items := 1 + floor(random() * 4);

            FOR j IN 1..n_items LOOP
                -- elegir categoría según distribución
                r_cat := random();

                IF r_cat < 0.60 THEN
                    -- Café
                    SELECT p.id_producto, p.precio_venta
                    INTO v_prod_id, v_price
                    FROM productos p
                    JOIN categorias_producto c ON p.id_categoria = c.id_categoria
                    WHERE c.nombre = 'Café'
                    ORDER BY random()
                    LIMIT 1;

                ELSIF r_cat < 0.85 THEN
                    -- Pastelería
                    SELECT p.id_producto, p.precio_venta
                    INTO v_prod_id, v_price
                    FROM productos p
                    JOIN categorias_producto c ON p.id_categoria = c.id_categoria
                    WHERE c.nombre = 'Pastelería'
                    ORDER BY random()
                    LIMIT 1;

                ELSIF r_cat < 0.95 THEN
                    -- Comidas
                    SELECT p.id_producto, p.precio_venta
                    INTO v_prod_id, v_price
                    FROM productos p
                    JOIN categorias_producto c ON p.id_categoria = c.id_categoria
                    WHERE c.nombre = 'Comidas'
                    ORDER BY random()
                    LIMIT 1;

                ELSE
                    -- Bebidas
                    SELECT p.id_producto, p.precio_venta
                    INTO v_prod_id, v_price
                    FROM productos p
                    JOIN categorias_producto c ON p.id_categoria = c.id_categoria
                    WHERE c.nombre = 'Bebidas'
                    ORDER BY random()
                    LIMIT 1;
                END IF;

                IF v_prod_id IS NULL OR v_price IS NULL THEN
                    CONTINUE;
                END IF;

                -- cantidad 1–3
                v_qty := 1 + floor(random() * 3);

                -- insertar detalle
                INSERT INTO ventas_detalle (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (v_id_venta, v_prod_id, v_qty, v_price, v_price * v_qty);

                v_total := v_total + (v_price * v_qty);
            END LOOP;

            -- actualizar total del ticket
            UPDATE ventas
            SET total_ticket = v_total
            WHERE id_venta = v_id_venta;
        END LOOP;

        d := d + 1;
    END LOOP;
END $$;



-- Total de cada tabla
SELECT COUNT(*) FROM ventas;
SELECT COUNT(*) FROM ventas_detalle;


--Genera detalles para ventas existentes
DO $$
DECLARE
    v_rec    RECORD;
    j        INT;
    n_items  INT;
    v_prod_id INT;
    v_qty    INT;
    v_price  NUMERIC(12,2);
    v_total  NUMERIC(12,2);
BEGIN
    -- Recorremos todas las ventas existentes
    FOR v_rec IN
        SELECT id_venta
        FROM ventas
        ORDER BY id_venta
    LOOP
        v_total := 0;

        -- Cada ticket tendrá entre 1 y 4 ítems
        n_items := 1 + FLOOR(random() * 4);

        FOR j IN 1..n_items LOOP
            -- Elegimos un producto al azar de la tabla productos
            SELECT id_producto, precio_venta
            INTO v_prod_id, v_price
            FROM productos
            ORDER BY random()
            LIMIT 1;

            IF v_prod_id IS NULL THEN
                CONTINUE;
            END IF;

            -- Cantidad entre 1 y 3
            v_qty := 1 + FLOOR(random() * 3);

            -- Insertamos el detalle
            INSERT INTO ventas_detalle (id_venta, id_producto, cantidad, precio_unitario, subtotal)
            VALUES (v_rec.id_venta, v_prod_id, v_qty, v_price, v_price * v_qty);

            v_total := v_total + (v_price * v_qty);
        END LOOP;

        -- Actualizamos el total_ticket con la suma de subtotales
        UPDATE ventas
        SET total_ticket = v_total
        WHERE id_venta = v_rec.id_venta;
    END LOOP;
END $$;


SELECT COUNT(*) FROM ventas_detalle;

SELECT * 
FROM ventas_detalle
LIMIT 10;

SELECT v.id_venta, v.total_ticket,
       SUM(d.subtotal) AS total_calculado
FROM ventas v
JOIN ventas_detalle d ON v.id_venta = d.id_venta
GROUP BY v.id_venta, v.total_ticket
LIMIT 20;


