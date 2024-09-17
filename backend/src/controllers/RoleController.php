<?php
// src/controllers/RoleController.php
require_once __DIR__ . '/../models/Role.php';

class RoleController {
    private $db;
    private $role;

    public function __construct($db) {
        $this->db = $db;
        $this->role = new Role($db);
    }

    public function getAllRoles() {
        try {
            $roles = $this->role->getAllRoles();
            $this->sendJsonResponse(true, '', ['roles' => $roles]);
        } catch (Exception $e) {
            error_log("Error al obtener todos los roles: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al obtener todos los roles.');
        }
    }

    public function createRole() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->name)) {
            $this->sendJsonResponse(false, 'Se requiere el nombre para crear un rol.');
            return;
        }

        try {
            $result = $this->role->createRole($data->name);
            if ($result) {
                $this->sendJsonResponse(true, 'Rol creado con éxito.', ['role' => $result]);
            } else {
                $this->sendJsonResponse(false, 'No se pudo crear el rol.');
            }
        } catch (Exception $e) {
            error_log("Error al crear rol: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al crear el rol.');
        }
    }

    public function deleteRole() {
        if (!isset($_GET['id'])) {
            $this->sendJsonResponse(false, 'Se requiere el ID del rol para eliminarlo.');
            return;
        }

        $roleId = $_GET['id'];

        try {
            $result = $this->role->deleteRole($roleId);
            if ($result) {
                $this->sendJsonResponse(true, 'Rol eliminado con éxito.');
            } else {
                $this->sendJsonResponse(false, 'No se pudo eliminar el rol.');
            }
        } catch (Exception $e) {
            error_log("Error al eliminar rol: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al eliminar el rol.');
        }
    }

    private function sendJsonResponse($success, $message = '', $data = []) {
        $response = array_merge(
            ['success' => $success],
            $message ? ['message' => $message] : [],
            $data
        );

        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    }
}