<?php

require_once __DIR__ . '/../models/Ubicacion.php';

class UbicacionController {
    private $db;
    private $ubicacion;

    public function __construct($db) {
        $this->db = $db;
        $this->ubicacion = new Ubicacion($db);
    }

    public function getAllUbicaciones() {
        try {
            $ubicaciones = $this->ubicacion->getAllUbicaciones();
            echo json_encode(['success' => true, 'ubicaciones' => $ubicaciones]);
        } catch (Exception $e) {
            error_log("Error getting ubicaciones: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while fetching ubicaciones.']);
        }
    }

    public function createUbicacion() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->dispositivo_gps_id) || !isset($data->latitud) || !isset($data->longitud) || !isset($data->fecha_hora)) {
            echo json_encode(['success' => false, 'message' => 'All fields are required.']);
            return;
        }

        try {
            $result = $this->ubicacion->createUbicacion($data->dispositivo_gps_id, $data->latitud, $data->longitud, $data->fecha_hora, $data->velocidad ?? null, $data->bateria ?? null);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Ubicación created successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to create ubicación.']);
            }
        } catch (Exception $e) {
            error_log("Error creating ubicación: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while creating the ubicación.']);
        }
    }

    public function getUbicacionesPorDispositivo() {
        if (!isset($_GET['dispositivo_gps_id'])) {
            echo json_encode(['success' => false, 'message' => 'Dispositivo GPS ID is required.']);
            return;
        }

        try {
            $ubicaciones = $this->ubicacion->getUbicacionesPorDispositivo($_GET['dispositivo_gps_id']);
            echo json_encode(['success' => true, 'ubicaciones' => $ubicaciones]);
        } catch (Exception $e) {
            error_log("Error getting ubicaciones por dispositivo: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while fetching ubicaciones for the dispositivo.']);
        }
    }
}