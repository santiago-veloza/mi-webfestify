CREATE DATABASE IF NOT EXISTS festify_db;
USE festify_db;

-- Tabla usuarios (microempresarios)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla clientes
CREATE TABLE IF NOT EXISTS clientesb (
    cliente_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo_cliente VARCHAR(100) UNIQUE NOT NULL,
    clave_cliente VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla eventos
CREATE TABLE IF NOT EXISTS festify (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    ubicacion VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tiquetes INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    usuario_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla compras
CREATE TABLE IF NOT EXISTS compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    evento_id INT NOT NULL,
    cantidad INT NOT NULL,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientesb(cliente_id),
    FOREIGN KEY (evento_id) REFERENCES festify(id)
);