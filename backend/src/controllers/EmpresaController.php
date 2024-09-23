<?php

require_once __DIR__ . '/../models/Empresa.php';

class EmpresaController {
    private $db;
    private $empresa;

    public function __construct($db) {
        $this->db = $db;
        $this->empresa = new Empresa($db);
    }

    public function getAllEmpresas() {
        try {
            $empresas = $this->empresa->getAllEmpresas();
            echo json_encode(['success' => true, 'empresas' => $empresas]);
        } catch (Exception $e) {
            error_log("Error getting empresas: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while fetching empresas.']);
        }
    }

    public function createEmpresa() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->nombre) || !isset($data->direccion) || !isset($data->telefono) || !isset($data->email)) {
            echo json_encode(['success' => false, 'message' => 'All fields are required.']);
            return;
        }

        try {
            $result = $this->empresa->createEmpresa($data->nombre, $data->direccion, $data->telefono, $data->email);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Empresa created successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to create empresa.']);
            }
        } catch (Exception $e) {
            error_log("Error creating empresa: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while creating the empresa.']);
        }
    }

    public function updateEmpresa() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->id) || !isset($data->nombre) || !isset($data->direccion) || !isset($data->telefono) || !isset($data->email)) {
            echo json_encode(['success' => false, 'message' => 'All fields are required.']);
            return;
        }

        try {
            $result = $this->empresa->updateEmpresa($data->id, $data->nombre, $data->direccion, $data->telefono, $data->email);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Empresa updated successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to update empresa.']);
            }
        } catch (Exception $e) {
            error_log("Error updating empresa: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while updating the empresa.']);
        }
    }

    public function deleteEmpresa() {
        if (!isset($_GET['id'])) {
            echo json_encode(['success' => false, 'message' => 'Empresa ID is required.']);
            return;
        }

        try {
            $result = $this->empresa->deleteEmpresa($_GET['id']);
            if ($result) {
                echo json_encode(['success' => true, 'message' => 'Empresa deleted successfully.']);
            } else {
                echo json_encode(['success' => false, 'message' => 'Failed to delete empresa.']);
            }
        } catch (Exception $e) {
            error_log("Error deleting empresa: " . $e->getMessage());
            echo json_encode(['success' => false, 'message' => 'An error occurred while deleting the empresa.']);
        }
    }
}