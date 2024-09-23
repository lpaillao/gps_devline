<?php

require_once __DIR__ . '/../models/AsignacionDispositivo.php';

class AsignacionDispositivoController {
    private $db;
    private $asignacionDispositivo;

    public function __construct($db) {
        $this->db = $db;
        $this->asignacionDispositivo = new AsignacionDispositivo($db);
    }

    public function getAllAsignaciones() {
        try {
            $asignaciones = $this->asignacionDispositivo->getAllAsignaciones();
            echo json_encode(['success' => true, 'asignaciones' => $asignaciones]);
        } catch (Exception $e) {
            error_log("Error getting asignaciones: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while fetching asignaciones.']);
        }
    }

    public function createAsignacion() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->dispositivo_gps_id) || (!isset($data->usuario_id) && !isset($data->empresa_id))) {
            echo json_encode(['success' => false, 'message' => 'Dispositivo GPS ID and either Usuario ID or Empresa ID are required.']);
            return;
        }

        try {
            $result = $this->asignacionDispositivo->createAsignacion($data->dispositivo_gps_id, $data->usuario_id ?? null, $data->empresa_id ?? null);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Asignación created successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to create asignación.']);
            }
        } catch (Exception $e) {
            error_log("Error creating asignación: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while creating the asignación.']);
        }
    }

    public function updateAsignacion() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->id) || !isset($data->dispositivo_gps_id) || (!isset($data->usuario_id) && !isset($data->empresa_id))) {
            echo json_encode(['success' => false, 'message' => 'All fields are required.']);
            return;
        }

        try {
            $result = $this->asignacionDispositivo->updateAsignacion($data->id, $data->dispositivo_gps_id, $data->usuario_id ?? null, $data->empresa_id ?? null);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Asignación updated successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to update asignación.']);
            }
        } catch (Exception $e) {
            error_log("Error updating asignación: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while updating the asignación.']);
        }
    }

    public function deleteAsignacion() {
        if (!isset($_GET['id'])) {
            echo json_encode(['success' => false, 'message' => 'Asignación ID is required.']);
            return;
        }

        try {
            $result = $this->asignacionDispositivo->deleteAsignacion($_GET['id']);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Asignación deleted successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to delete asignación.']);
            }
        } catch (Exception $e) {
            error_log("Error deleting asignación: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while deleting the asignación.']);
        }
    }
}