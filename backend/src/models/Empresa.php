<?php

class Empresa {
    private $conn;
    private $table_name = "empresas";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getAllEmpresas() {
        $query = "SELECT * FROM " . $this->table_name;
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function createEmpresa($nombre, $direccion, $telefono, $email) {
        $query = "INSERT INTO " . $this->table_name . " (nombre, direccion, telefono, email) VALUES (?, ?, ?, ?)";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $nombre);
        $stmt->bindParam(2, $direccion);
        $stmt->bindParam(3, $telefono);
        $stmt->bindParam(4, $email);
        return $stmt->execute();
    }

    public function updateEmpresa($id, $nombre, $direccion, $telefono, $email) {
        $query = "UPDATE " . $this->table_name . " SET nombre = ?, direccion = ?, telefono = ?, email = ? WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $nombre);
        $stmt->bindParam(2, $direccion);
        $stmt->bindParam(3, $telefono);
        $stmt->bindParam(4, $email);
        $stmt->bindParam(5, $id);
        return $stmt->execute();
    }

    public function deleteEmpresa($id) {
        $query = "DELETE FROM " . $this->table_name . " WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $id);
        return $stmt->execute();
    }
}