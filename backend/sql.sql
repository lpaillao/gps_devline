CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE menus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    url VARCHAR(100) NOT NULL,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Insertar roles base
INSERT INTO roles (name) VALUES ('Administrador');
INSERT INTO roles (name) VALUES ('Usuario');

-- Insertar usuario administrador
-- Nota: La contraseña es 'admin123', pero está hasheada. Cámbiala en producción.
INSERT INTO users (username, password, email, role_id)
VALUES ('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin@example.com', 1);

-- Insertar menús principales para el rol de Administrador
INSERT INTO menus (name, url, role_id) VALUES ('Dashboard', '/dashboard', 1);
INSERT INTO menus (name, url, role_id) VALUES ('Gestión de Usuarios', '/users', 1);
INSERT INTO menus (name, url, role_id) VALUES ('Gestión de Roles', '/roles', 1);
INSERT INTO menus (name, url, role_id) VALUES ('Gestión de Menús', '/menus', 1);