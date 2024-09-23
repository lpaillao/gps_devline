<?php

require_once __DIR__ . '/../models/TipoGPS.php';

class TipoGPSController {
    private $db;
    private $tipoGPS;

    public function __construct($db) {
        $this->db = $db;
        $this->tipoGPS = new TipoGPS($db);
    }

    public function getAllTiposGPS() {
        try {
            $tipos = $this->tipoGPS->getAllTiposGPS();
            echo json_encode(['success' => true, 'tipos' => $tipos]);
        } catch (Exception $e) {
            error_log("Error getting tipos GPS: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while fetching tipos GPS.']);
        }
    }

    public function createTipoGPS() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->nombre)) {
            echo json_encode(['success' => false, 'message' => 'Nombre is required.']);
            return;
        }

        try {
            $result = $this->tipoGPS->createTipoGPS($data->nombre);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Tipo GPS created successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to create tipo GPS.']);
            }
        } catch (Exception $e) {
            error_log("Error creating tipo GPS: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while creating the tipo GPS.']);
        }
    }

    public function updateTipoGPS() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->id) || !isset($data->nombre)) {
            echo json_encode(['success' => false, 'message' => 'ID and nombre are required.']);
            return;
        }

        try {
            $result = $this->tipoGPS->updateTipoGPS($data->id, $data->nombre);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Tipo GPS updated successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to update tipo GPS.']);
            }
        } catch (Exception $e) {
            error_log("Error updating tipo GPS: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while updating the tipo GPS.']);
        }
    }

    public function deleteTipoGPS() {
        if (!isset($_GET['id'])) {
            echo json_encode(['success' => false, 'message' => 'Tipo GPS ID is required.']);
            return;
        }

        try {
            $result = $this->tipoGPS->deleteTipoGPS($_GET['id']);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Tipo GPS deleted successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to delete tipo GPS.']);
            }
        } catch (Exception $e) {
            error_log("Error deleting tipo GPS: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while deleting the tipo GPS.']);
        }
    }
}