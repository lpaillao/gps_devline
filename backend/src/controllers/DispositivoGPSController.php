<?php

require_once __DIR__ . '/../models/DispositivoGPS.php';

class DispositivoGPSController {
    private $db;
    private $dispositivoGPS;

    public function __construct($db) {
        $this->db = $db;
        $this->dispositivoGPS = new DispositivoGPS($db);
    }

    public function getAllDispositivosGPS() {
        try {
            $dispositivos = $this->dispositivoGPS->getAllDispositivosGPS();
            echo json_encode(['success' => true, 'dispositivos' => $dispositivos]);
        } catch (Exception $e) {
            error_log("Error getting dispositivos GPS: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while fetching dispositivos GPS.']);
        }
    }

    public function createDispositivoGPS() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->imei) || !isset($data->modelo) || !isset($data->marca) || !isset($data->tipo_gps_id)) {
            echo json_encode(['success' => false, 'message' => 'All fields are required.']);
            return;
        }

        try {
            $result = $this->dispositivoGPS->createDispositivoGPS($data->imei, $data->modelo, $data->marca, $data->tipo_gps_id);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Dispositivo GPS created successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to create dispositivo GPS.']);
            }
        } catch (Exception $e) {
            error_log("Error creating dispositivo GPS: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while creating the dispositivo GPS.']);
        }
    }

    public function updateDispositivoGPS() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->id) || !isset($data->imei) || !isset($data->modelo) || !isset($data->marca) || !isset($data->tipo_gps_id)) {
            echo json_encode(['success' => false, 'message' => 'All fields are required.']);
            return;
        }

        try {
            $result = $this->dispositivoGPS->updateDispositivoGPS($data->id, $data->imei, $data->modelo, $data->marca, $data->tipo_gps_id);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Dispositivo GPS updated successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to update dispositivo GPS.']);
            }
        } catch (Exception $e) {
            error_log("Error updating dispositivo GPS: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while updating the dispositivo GPS.']);
        }
    }

    public function deleteDispositivoGPS() {
        if (!isset($_GET['id'])) {
            echo json_encode(['success' => false, 'message' => 'Dispositivo GPS ID is required.']);
            return;
        }

        try {
            $result = $this->dispositivoGPS->deleteDispositivoGPS($_GET['id']);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Dispositivo GPS deleted successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to delete dispositivo GPS.']);
            }
        } catch (Exception $e) {
            error_log("Error deleting dispositivo GPS: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while deleting the dispositivo GPS.']);
        }
    }
}