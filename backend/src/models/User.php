<?php

// src/models/User.php
class User {
    private $conn;
    private $table_name = "users";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function login($username, $password) {
        if ($this->conn === null) {
            throw new Exception("Database connection is not available");
        }

        $query = "SELECT id, username, password, email, role_id FROM " . $this->table_name . " WHERE username = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $username);
        $stmt->execute();

        if ($stmt->rowCount() > 0) {
            $row = $stmt->fetch(PDO::FETCH_ASSOC);
            if (password_verify($password, $row['password'])) {
                return $row;
            }
        }

        return false;
    }
    public function register($username, $email, $password) {
        if ($this->conn === null) {
            throw new Exception("Database connection is not available");
        }

        // Verificar si el usuario ya existe
        $query = "SELECT id FROM " . $this->table_name . " WHERE username = ? OR email = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $username);
        $stmt->bindParam(2, $email);
        $stmt->execute();

        if ($stmt->rowCount() > 0) {
            return false; // Usuario ya existe
        }

        // Insertar nuevo usuario
        $query = "INSERT INTO " . $this->table_name . " (username, email, password, role_id) VALUES (?, ?, ?, ?)";
        $stmt = $this->conn->prepare($query);

        $hashed_password = password_hash($password, PASSWORD_DEFAULT);
        $role_id = 2; // Asumiendo que 2 es el role_id para usuarios normales

        $stmt->bindParam(1, $username);
        $stmt->bindParam(2, $email);
        $stmt->bindParam(3, $hashed_password);
        $stmt->bindParam(4, $role_id);

        if ($stmt->execute()) {
            return true;
        }

        return false;
    }
    public function getAllUsers() {
        $query = "SELECT u.id, u.username, u.email, r.name as role_name FROM " . $this->table_name . " u
                  INNER JOIN roles r ON u.role_id = r.id";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function createUser($username, $email, $password, $role_id) {
        $query = "INSERT INTO " . $this->table_name . " (username, email, password, role_id) VALUES (?, ?, ?, ?)";
        $stmt = $this->conn->prepare($query);
        $hashed_password = password_hash($password, PASSWORD_DEFAULT);
        $stmt->bindParam(1, $username);
        $stmt->bindParam(2, $email);
        $stmt->bindParam(3, $hashed_password);
        $stmt->bindParam(4, $role_id);
        return $stmt->execute();
    }

    public function updateUser($id, $username, $email, $role_id) {
        $query = "UPDATE " . $this->table_name . " SET username = ?, email = ?, role_id = ? WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $username);
        $stmt->bindParam(2, $email);
        $stmt->bindParam(3, $role_id);
        $stmt->bindParam(4, $id);
        return $stmt->execute();
    }

    public function deleteUser($id) {
        $query = "DELETE FROM " . $this->table_name . " WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $id);
        return $stmt->execute();
    }
}