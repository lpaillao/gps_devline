<?php
// src/controllers/MenuController.php
require_once __DIR__ . '/../models/Menu.php';

class MenuController {
    private $db;
    private $menu;

    public function __construct($db) {
        $this->db = $db;
        $this->menu = new Menu($db);
    }

    public function getMenusByRoleId() {
        if (!isset($_GET['roleId'])) {
            $this->sendJsonResponse(false, 'Se requiere el ID del rol.');
            return;
        }

        $roleId = $_GET['roleId'];

        try {
            $menus = $this->menu->getMenusByRoleId($roleId);
            $this->sendJsonResponse(true, '', ['menus' => $menus]);
        } catch (Exception $e) {
            error_log("Error al obtener menús: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al obtener los menús.');
        }
    }

    public function getAllMenus() {
        try {
            $menus = $this->menu->getAllMenus();
            $this->sendJsonResponse(true, '', ['menus' => $menus]);
        } catch (Exception $e) {
            error_log("Error al obtener todos los menús: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al obtener todos los menús.');
        }
    }

    public function createMenu() {
        $data = json_decode(file_get_contents("php://input"));

        if (!isset($data->name) || !isset($data->url) || !isset($data->icon)) {
            $this->sendJsonResponse(false, 'Se requieren nombre, URL e icono para crear un menú.');
            return;
        }

        try {
            $result = $this->menu->createMenu($data->name, $data->url, $data->icon);
            if ($result) {
                $this->sendJsonResponse(true, 'Menú creado con éxito.', ['menu' => $result]);
            } else {
                $this->sendJsonResponse(false, 'No se pudo crear el menú.');
            }
        } catch (Exception $e) {
            error_log("Error al crear menú: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al crear el menú.');
        }
    }

    public function deleteMenu() {
        if (!isset($_GET['id'])) {
            $this->sendJsonResponse(false, 'Se requiere el ID del menú para eliminarlo.');
            return;
        }

        $menuId = $_GET['id'];

        try {
            $result = $this->menu->deleteMenu($menuId);
            if ($result) {
                $this->sendJsonResponse(true, 'Menú eliminado con éxito.');
            } else {
                $this->sendJsonResponse(false, 'No se pudo eliminar el menú.');
            }
        } catch (Exception $e) {
            error_log("Error al eliminar menú: " . $e->getMessage());
            $this->sendJsonResponse(false, 'Ocurrió un error al eliminar el menú.');
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