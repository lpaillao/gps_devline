<?php

class Ubicacion {
    private $conn;
    private $table_name = "ubicaciones";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getAllUbicaciones() {
        $query = "SELECT * FROM " . $this->table_name . " ORDER BY fecha_hora DESC";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function createUbicacion($dispositivo_gps_id, $latitud, $longitud, $fecha_hora, $velocidad = null, $bateria = null) {
        $query = "INSERT INTO " . $this->table_name . " (dispositivo_gps_id, latitud, longitud, fecha_hora, velocidad, bateria) VALUES (?, ?, ?, ?, ?, ?)";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $dispositivo_gps_id);
        $stmt->bindParam(2, $latitud);
        $stmt->bindParam(3, $longitud);
        $stmt->bindParam(4, $fecha_hora);
        $stmt->bindParam(5, $velocidad);
        $stmt->bindParam(6, $bateria);
        return $stmt->execute();
    }

    public function getUbicacionesPorDispositivo($dispositivo_gps_id) {
        $query = "SELECT * FROM " . $this->table_name . " WHERE dispositivo_gps_id = ? ORDER BY fecha_hora DESC";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $dispositivo_gps_id);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}