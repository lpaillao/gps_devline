<?php

class AsignacionDispositivo {
    private $conn;
    private $table_name = "asignacion_dispositivos";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getAllAsignaciones() {
        $query = "SELECT a.*, d.imei, u.username as usuario, e.nombre as empresa 
                  FROM " . $this->table_name . " a
                  LEFT JOIN dispositivos_gps d ON a.dispositivo_gps_id = d.id
                  LEFT JOIN users u ON a.usuario_id = u.id
                  LEFT JOIN empresas e ON a.empresa_id = e.id";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function createAsignacion($dispositivo_gps_id, $usuario_id = null, $empresa_id = null) {
        $query = "INSERT INTO " . $this->table_name . " (dispositivo_gps_id, usuario_id, empresa_id) VALUES (?, ?, ?)";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $dispositivo_gps_id);
        $stmt->bindParam(2, $usuario_id);
        $stmt->bindParam(3, $empresa_id);
        return $stmt->execute();
    }

    public function updateAsignacion($id, $dispositivo_gps_id, $usuario_id = null, $empresa_id = null) {
        $query = "UPDATE " . $this->table_name . " SET dispositivo_gps_id = ?, usuario_id = ?, empresa_id = ? WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $dispositivo_gps_id);
        $stmt->bindParam(2, $usuario_id);
        $stmt->bindParam(3, $empresa_id);
        $stmt->bindParam(4, $id);
        return $stmt->execute();
    }

    public function deleteAsignacion($id) {
        $query = "DELETE FROM " . $this->table_name . " WHERE id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $id);
        return $stmt->execute();
    }

    public function getAsignacionesPorUsuario($usuario_id) {
        $query = "SELECT a.*, d.imei, d.modelo, d.marca, t.nombre as tipo_gps
                  FROM " . $this->table_name . " a
                  INNER JOIN dispositivos_gps d ON a.dispositivo_gps_id = d.id
                  INNER JOIN tipos_gps t ON d.tipo_gps_id = t.id
                  WHERE a.usuario_id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $usuario_id);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getAsignacionesPorEmpresa($empresa_id) {
        $query = "SELECT a.*, d.imei, d.modelo, d.marca, t.nombre as tipo_gps, u.username as usuario
                  FROM " . $this->table_name . " a
                  INNER JOIN dispositivos_gps d ON a.dispositivo_gps_id = d.id
                  INNER JOIN tipos_gps t ON d.tipo_gps_id = t.id
                  LEFT JOIN users u ON a.usuario_id = u.id
                  WHERE a.empresa_id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $empresa_id);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getAsignacionPorDispositivo($dispositivo_gps_id) {
        $query = "SELECT a.*, u.username as usuario, e.nombre as empresa
                  FROM " . $this->table_name . " a
                  LEFT JOIN users u ON a.usuario_id = u.id
                  LEFT JOIN empresas e ON a.empresa_id = e.id
                  WHERE a.dispositivo_gps_id = ?";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(1, $dispositivo_gps_id);
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
}