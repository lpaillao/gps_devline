<?php

class TipoGPS {
    private $conn;
    private $table_name = "tipos_gps";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getAllTiposGPS() {
        $query = "SELECT * FROM " . $this->table_name;
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function createTipoGPS($nombre) {
        $query = "INSERT INTO " . $this->table_name . " (nombre) VALUES (?)";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $nombre);
        return $stmt->execute();
    }

    public function updateTipoGPS($id, $nombre) {
        $query = "UPDATE " . $this->table_name . " SET nombre = ? WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $nombre);
        $stmt->bindParam(2, $id);
        return $stmt->execute();
    }

    public function deleteTipoGPS($id) {
        $query = "DELETE FROM " . $this->table_name . " WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $id);
        return $stmt->execute();
    }

    public function getTipoGPSById($id) {
        $query = "SELECT * FROM " . $this->table_name . " WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $id);
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
}