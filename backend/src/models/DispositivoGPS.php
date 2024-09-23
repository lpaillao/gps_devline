<?php

class DispositivoGPS {
    private $conn;
    private $table_name = "dispositivos_gps";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getAllDispositivosGPS() {
        $query = "SELECT d.*, t.nombre as tipo_gps FROM " . $this->table_name . " d
                  INNER JOIN tipos_gps t ON d.tipo_gps_id = t.id";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function createDispositivoGPS($imei, $modelo, $marca, $tipo_gps_id) {
        $query = "INSERT INTO " . $this->table_name . " (imei, modelo, marca, tipo_gps_id) VALUES (?, ?, ?, ?)";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $imei);
        $stmt->bindParam(2, $modelo);
        $stmt->bindParam(3, $marca);
        $stmt->bindParam(4, $tipo_gps_id);
        return $stmt->execute();
    }

    public function updateDispositivoGPS($id, $imei, $modelo, $marca, $tipo_gps_id) {
        $query = "UPDATE " . $this->table_name . " SET imei = ?, modelo = ?, marca = ?, tipo_gps_id = ? WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $imei);
        $stmt->bindParam(2, $modelo);
        $stmt->bindParam(3, $marca);
        $stmt->bindParam(4, $tipo_gps_id);
        $stmt->bindParam(5, $id);
        return $stmt->execute();
    }

    public function deleteDispositivoGPS($id) {
        $query = "DELETE FROM " . $this->table_name . " WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $id);
        return $stmt->execute();
    }
}