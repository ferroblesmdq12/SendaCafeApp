-- Creando Tablas -- 
BEGIN;

CREATE TABLE turnos (
    id_turno       SERIAL PRIMARY KEY,
    nombre_turno   VARCHAR(50) NOT NULL,
    hora_inicio    TIME NOT NULL,
    hora_fin       TIME NOT NULL
);

CREATE TABLE empleados (
    id_empleado      SERIAL PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    rol              VARCHAR(50)  NOT NULL,
    id_turno         INT NULL,
    sueldo_mensual   NUMERIC(12,2) NOT NULL DEFAULT 0,
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en        TIMESTAMP NOT NULL DEFAULT NOW(),
    actualizado_en   TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_empleados_turnos
        FOREIGN KEY (id_turno) REFERENCES turnos(id_turno)
);

CREATE TABLE categorias_producto (
    id_categoria   SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL
);

CREATE TABLE productos (
    id_producto     SERIAL PRIMARY KEY,
    nombre          VARCHAR(150) NOT NULL,
    id_categoria    INT NULL,
    precio_venta    NUMERIC(12,2) NOT NULL,
    costo_unitario  NUMERIC(12,2) NOT NULL,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMP NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_productos_categorias
        FOREIGN KEY (id_categoria) REFERENCES categorias_producto(id_categoria)
);

CREATE TABLE usuarios (
    id_usuario     SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    email          VARCHAR(150) NOT NULL UNIQUE,
    usuario        VARCHAR(50)  NOT NULL UNIQUE,
    hash_password  TEXT         NOT NULL,
    rol            VARCHAR(20)  NOT NULL,
    activo         BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en      TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE costos_fijos (
    id_costo       SERIAL PRIMARY KEY,
    categoria      VARCHAR(150) NOT NULL,
    monto_ars      NUMERIC(14,2) NOT NULL,
    frecuencia     VARCHAR(20)  NOT NULL DEFAULT 'mensual',
    activo         BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en      TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE ventas (
    id_venta        SERIAL PRIMARY KEY,
    ticket_id_origen INT NULL,
    fecha_hora      TIMESTAMP NOT NULL,
    servicio        VARCHAR(50) NOT NULL,
    id_empleado     INT NOT NULL,
    metodo_pago     VARCHAR(50) NULL,
    total_ticket    NUMERIC(12,2) NOT NULL,
    creado_en       TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_ventas_empleados
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

CREATE TABLE stock (
    id_producto     INT PRIMARY KEY,
    stock_actual    INT NOT NULL DEFAULT 0,
    stock_minimo    INT NOT NULL DEFAULT 0,
    actualizado_en  TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_stock_productos
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE movimientos_stock (
    id_movimiento      SERIAL PRIMARY KEY,
    id_producto        INT NOT NULL,
    fecha_hora         TIMESTAMP NOT NULL DEFAULT NOW(),
    tipo_movimiento    VARCHAR(20) NOT NULL,
    cantidad           INT NOT NULL,
    comentario         TEXT NULL,
    creado_por         INT NULL,
    CONSTRAINT chk_movimientos_cantidad_not_zero
        CHECK (cantidad <> 0),
    CONSTRAINT fk_mov_stock_productos
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    CONSTRAINT fk_mov_stock_usuarios
        FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario)
);

CREATE TABLE ventas_detalle (
    id_detalle      SERIAL PRIMARY KEY,
    id_venta        INT NOT NULL,
    id_producto     INT NOT NULL,
    cantidad        INT NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12,2) NOT NULL,
    subtotal        NUMERIC(12,2) NOT NULL,
    creado_en       TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_detalle_ventas
        FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    CONSTRAINT fk_detalle_productos
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

COMMIT;


-- Mostrando Tablas Creadas -- 

SELECT * FROM turnos;
SELECT * FROM empleados;
SELECT * FROM categorias_producto;
SELECT * FROM productos;
SELECT * FROM usuarios;
SELECT * FROM costos_fijos;
SELECT * FROM ventas;
SELECT * FROM ventas_detalle;
SELECT * FROM stock;
SELECT * FROM movimientos_stock;



-- CARGANDO TABLAS -- 

-- Cargando tablas de usuarios
INSERT INTO usuarios (nombre, email, usuario, hash_password, rol, activo)
VALUES
('Fernando Robles', 'fernando@senda.com', 'fernando', '$2b$12$E5zlmdddX0zXg.Mi9iYl1.0dHwMIcpr4m80r3780rM.zqFVw0Yd0y', 'admin', TRUE),
('Gissel', 'gissel@senda.com', 'gissel', '$2b$12$G1Mtx6sN0p1ovI9r4K4dPuxU1obXDhyqIR7rtt3nW4Z5pkUEEmjhm', 'owner', TRUE),
('Cristian', 'cristian@senda.com', 'cristian', '$2b$12$1.ohgcu4MbrbrbZ/dsfnLuG6/DtofC1KiWH6bhg7EzRjXt6DTs7m6', 'owner', TRUE);

-- Cargando tablas turnos
INSERT INTO turnos (nombre_turno, hora_inicio, hora_fin) VALUES
('mañana','08:00','16:00'),
('tarde','16:00','00:00');

-- Cargando tabla empleados
INSERT INTO empleados (nombre, rol, id_turno, sueldo_mensual, activo)
VALUES
  ('Empleado_1', 'CocinerO', (SELECT id_turno FROM turnos WHERE nombre_turno = 'mañana'), 450000, TRUE),
  ('Empleado_2', 'Cajero', (SELECT id_turno FROM turnos WHERE nombre_turno = 'tarde'), 400000, TRUE),
  ('Empleado_3', 'Barista', (SELECT id_turno FROM turnos WHERE nombre_turno = 'mañana'), 420000, TRUE),
  ('Empleado_4', 'Barista', (SELECT id_turno FROM turnos WHERE nombre_turno = 'tarde'), 380000, TRUE),
  ('Empleado_5', 'Camarero', (SELECT id_turno FROM turnos WHERE nombre_turno = 'mañana'), 380000, TRUE),
  ('Empleado_6', 'Camarero', (SELECT id_turno FROM turnos WHERE nombre_turno = 'tarde'), 380000, TRUE),
  ('Empleado_7', 'Camarero', (SELECT id_turno FROM turnos WHERE nombre_turno = 'mañana'), 380000, TRUE),
  ('Empleado_8', 'Camarero', (SELECT id_turno FROM turnos WHERE nombre_turno = 'tarde'), 380000, TRUE),
  ('Empleado_9', 'Camarero', (SELECT id_turno FROM turnos WHERE nombre_turno = 'mañana'), 380000, TRUE),
  ('Empleado_10', 'Camarero', (SELECT id_turno FROM turnos WHERE nombre_turno = 'tarde'), 380000, TRUE),
  ('Empleado_11', 'Camarero', (SELECT id_turno FROM turnos WHERE nombre_turno = 'mañana'), 380000, TRUE);

-- Cargando tabla productos
INSERT INTO productos (nombre, id_categoria, precio_venta, costo_unitario, activo)
VALUES
('Espresso', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Café'), 1200, 300, TRUE),
('Americano', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Café'), 1400, 350, TRUE),
('Latte', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Café'), 1800, 450, TRUE),
('Cappuccino', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Café'), 1900, 480, TRUE),
('Flat White', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Café'), 2000, 500, TRUE),

('Té', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Bebidas'), 1200, 300, TRUE),
('Jugo de Naranja', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Bebidas'), 1600, 600, TRUE),
('Agua Mineral', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Bebidas'), 900, 250, TRUE),

('Medialuna', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Pastelería'), 550, 150, TRUE),
('Pain au Chocolat', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Pastelería'), 1100, 350, TRUE),
('Cookie', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Pastelería'), 900, 200, TRUE),

('Tostado de Jamón y Queso', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Comidas'), 2500, 800, TRUE),
('Sandwich de Pollo', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Comidas'), 2800, 900, TRUE),
('Ensalada', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Comidas'), 3200, 1000, TRUE),

('Botella de Cold Brew', (SELECT id_categoria FROM categorias_producto WHERE nombre = 'Otros'), 3500, 1200, TRUE);

-- Cargando tabla stock
INSERT INTO stock (id_producto, stock_actual, stock_minimo)
SELECT id_producto,
CASE 
    WHEN nombre IN ('Espresso','Americano','Latte','Cappuccino','Flat White') THEN 200
    WHEN nombre IN ('Té','Agua Mineral','Jugo de Naranja') THEN 100
    WHEN nombre IN ('Medialuna','Pain au Chocolat','Cookie') THEN 80
    WHEN nombre IN ('Tostado de Jamón y Queso','Sandwich de Pollo','Ensalada') THEN 50
    ELSE 40
END,
10
FROM productos;

SELECT * FROM categorias_producto;
SELECT id_producto, nombre, precio_venta FROM productos;
SELECT * FROM stock;

--Creando Tabla ventas_raw (tabla intermedia)
CREATE TABLE ventas_raw (
    ticket_id      INT,
    fecha          DATE,
    hora           TIME,
    servicio       TEXT,
    camarero       TEXT,
    productos      TEXT,
    cantidades     TEXT,
    total_ticket   NUMERIC(12,2)
);

INSERT INTO empleados (nombre, rol, id_turno, sueldo_mensual, activo)
VALUES ('Camarero_Sistema', 'Camarero', NULL, 0, TRUE);

SELECT id_empleado, nombre FROM empleados WHERE nombre = 'Camarero_Sistema';


ve


