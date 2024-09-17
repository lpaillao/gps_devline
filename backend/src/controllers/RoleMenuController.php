<?php
// src/controllers/RoleMenuController.php
require_once __DIR__ . '/../models/RoleMenu.php';

class RoleMenuController {
    private $db;
    private $roleMenu;

    public function __construct($db) {
        $this->db = $db;
        $this->roleMenu = new RoleMenu($db);
    }

    public function getMenusByRoleId() {
        if (!isset($_GET['roleId'])) {
            $this->sendJsonResponse(false, 'Se requiere el ID del rol.');
            return;
        }

        $roleId = $_GET['roleId'];

        try {
            $menus = $this->roleMenu->getMenusByRoleId($roleId);
            $this->sendJsonResponse(true, '', ['menus' => $menus]);
        } catch (Exception $e) {
            error_log("Error al obtener menús por rol: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al obtener los menús para el rol.');
        }
    }

    public function updateRoleMenus() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->roleId) || !isset($data->menuIds)) {
            $this->sendJsonResponse(false, 'Se requiere el ID del rol y los IDs de los menús.');
            return;
        }

        try {
            $result = $this->roleMenu->updateRoleMenus($data->roleId, $data->menuIds);
            if ($result) {
                $this->sendJsonResponse(true, 'Menús actualizados para el rol con éxito.');
            } else {
                $this->sendJsonResponse(false, 'No se pudieron actualizar los menús para el rol.');
            }
        } catch (Exception $e) {
            error_log("Error al actualizar menús del rol: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al actualizar los menús del rol.');
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