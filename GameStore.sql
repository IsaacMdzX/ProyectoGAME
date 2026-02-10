CREATE TABLE Roles(
	id_rol serial primary key,
	nombre VARCHAR (30)
);

INSERT INTO Roles (nombre) VALUES('Administrador'), ('Cliente');
SELECT * FROM Roles;

SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

CREATE TABLE Usuarios(
	id_usuario serial primary key,
	nombre varchar(50),
	correo varchar(100) NOT NULL UNIQUE,
	nombre_usuario varchar (100) NOT NULL UNIQUE,
	password VARCHAR (255) NOT NULL,
	fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	ultimo_acceso TIMESTAMP DEFAULT NULL,
	telefono varchar (15), 
	rol_id int not null,
	foreign key (rol_id) REFERENCES Roles(id_rol)
);

INSERT INTO Usuarios(nombre,correo, nombre_usuario,password,telefono,rol_id) VALUES('Amron', 'amor@gmail.com' , 'Amron08', 'Amorcito20' , '1234567890', 1);

SELECT 
    Usuarios.id_usuario,
    Usuarios.nombre,
    Usuarios.nombre_usuario,
    Usuarios.password,
	Usuarios.correo,
	Usuarios.fecha_registro,
    Roles.nombre
FROM
    Usuarios
INNER JOIN
    Roles ON Usuarios.rol_id = Roles.id_rol;

-- Carrito
CREATE TABLE Categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

INSERT INTO Categorias (nombre, descripcion) VALUES
('Consolas', 'Consolas de videojuegos'),
('Juegos', 'Videojuegos físicos y digitales'),
('Controles', 'Controles y mandos'),
('Accesorios', 'Accesorios gaming');

CREATE TABLE Productos (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    stock INTEGER DEFAULT 0,
    imagen VARCHAR(500),
    categoria_id INTEGER REFERENCES Categorias(id_categoria),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Carrito (
    id_carrito SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES Usuarios(id_usuario),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE Carrito_Items (
    id_item SERIAL PRIMARY KEY,
    carrito_id INTEGER REFERENCES Carrito(id_carrito),
    producto_id INTEGER REFERENCES Productos(id_producto),
    cantidad INTEGER DEFAULT 1,
    precio_unitario DECIMAL(10,2),
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Pedidos (
    id_pedido SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES Usuarios(id_usuario),
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2),
    estado VARCHAR(50) DEFAULT 'pendiente',
    direccion_envio TEXT
);

CREATE TABLE Pedido_Items (
    id_item SERIAL PRIMARY KEY,
    pedido_id INTEGER REFERENCES Pedidos(id_pedido),
    producto_id INTEGER REFERENCES Productos(id_producto),
    cantidad INTEGER,
    precio_unitario DECIMAL(10,2)
);

INSERT INTO Productos (nombre, descripcion, precio, stock, imagen, categoria_id) VALUES
('Nintendo Switch 2', 'Consola Nintendo Switch 2 con 32GB', 8799.00, 10, '/static/img/Nintendo_Switch_2.jpeg', 1),
('PlayStation 5 Pro', 'Consola PlayStation 5 Pro 1TB', 17755.99, 5, '/static/img/PlayStation_5_pro.png', 1),
('Control Xbox Inalámbrico White', 'Control Xbox Series X/S color blanco', 1496.99, 20, '/static/img/Imagenes/controlxboxwhite.png', 3),
('Audífonos Gamer', 'Audífonos gaming profesionales 7.1', 760.00, 15, '/static/img/Audifonos_Gamer.jpg', 4),
('FC26', 'Control inalámbrico FC26', 1399.00, 8, '/static/img/FC26.jpeg', 3);