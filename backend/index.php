<?php
// index.php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

mb_internal_encoding('UTF-8');
mb_http_output('UTF-8');

header("Access-Control-Allow-Origin: http://127.0.0.1:3000");
header("Access-Control-Allow-Credentials: true");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

require_once __DIR__ . '/src/config/Database.php';
require_once __DIR__ . '/src/controllers/UserController.php';
require_once __DIR__ . '/src/controllers/MenuController.php';
require_once __DIR__ . '/src/controllers/RoleController.php';
require_once __DIR__ . '/src/controllers/RoleMenuController.php';
require_once __DIR__ . '/src/controllers/EmpresaController.php';
require_once __DIR__ . '/src/controllers/DispositivoGPSController.php';
require_once __DIR__ . '/src/controllers/UbicacionController.php';
require_once __DIR__ . '/src/controllers/AsignacionDispositivoController.php';
require_once __DIR__ . '/src/controllers/TipoGPSController.php';

try {
    $database = new Database();
    $db = $database->getConnection();

    if (!$db) {
        throw new Exception("Database connection failed");
    }

    $userController = new UserController($db);
    $menuController = new MenuController($db);
    $roleController = new RoleController($db);
    $roleMenuController = new RoleMenuController($db);
    $empresaController = new EmpresaController($db);
    $dispositivoGPSController = new DispositivoGPSController($db);
    $ubicacionController = new UbicacionController($db);
    $asignacionDispositivoController = new AsignacionDispositivoController($db);
    $tipoGPSController = new TipoGPSController($db);

    $action = isset($_GET['action']) ? $_GET['action'] : '';

    switch ($action) {
        // User actions
        case 'login':
            $userController->login();
            break;
        case 'register':
            $userController->register();
            break;
        case 'getAllUsers':
            $userController->getAllUsers();
            break;
        case 'createUser':
            $userController->createUser();
            break;
        case 'updateUser':
            $userController->updateUser();
            break;
        case 'deleteUser':
            $userController->deleteUser();
            break;
        
        // Menu actions
        case 'getAllMenus':
            $menuController->getAllMenus();
            break;
        case 'createMenu':
            $menuController->createMenu();
            break;
        case 'deleteMenu':
            $menuController->deleteMenu();
            break;
        
        // Role actions
        case 'getAllRoles':
            $roleController->getAllRoles();
            break;
        case 'createRole':
            $roleController->createRole();
            break;
        case 'deleteRole':
            $roleController->deleteRole();
            break;
        
        // Role-Menu association actions
        case 'getMenusByRoleId':
            $roleMenuController->getMenusByRoleId();
            break;
        case 'updateRoleMenus':
            $roleMenuController->updateRoleMenus();
            break;

        // Empresa actions
        case 'getAllEmpresas':
            $empresaController->getAllEmpresas();
            break;
        case 'createEmpresa':
            $empresaController->createEmpresa();
            break;
        case 'updateEmpresa':
            $empresaController->updateEmpresa();
            break;
        case 'deleteEmpresa':
            $empresaController->deleteEmpresa();
            break;

        // DispositivoGPS actions
        case 'getAllDispositivosGPS':
            $dispositivoGPSController->getAllDispositivosGPS();
            break;
        case 'createDispositivoGPS':
            $dispositivoGPSController->createDispositivoGPS();
            break;
        case 'updateDispositivoGPS':
            $dispositivoGPSController->updateDispositivoGPS();
            break;
        case 'deleteDispositivoGPS':
            $dispositivoGPSController->deleteDispositivoGPS();
            break;

        // Ubicacion actions
        case 'getAllUbicaciones':
            $ubicacionController->getAllUbicaciones();
            break;
        case 'createUbicacion':
            $ubicacionController->createUbicacion();
            break;
        case 'getUbicacionesPorDispositivo':
            $ubicacionController->getUbicacionesPorDispositivo();
            break;

        // AsignacionDispositivo actions
        case 'getAllAsignaciones':
            $asignacionDispositivoController->getAllAsignaciones();
            break;
        case 'createAsignacion':
            $asignacionDispositivoController->createAsignacion();
            break;
        case 'updateAsignacion':
            $asignacionDispositivoController->updateAsignacion();
            break;
        case 'deleteAsignacion':
            $asignacionDispositivoController->deleteAsignacion();
            break;
        case 'createTipoGPS';
            $tipoGPSController->createTipoGPS();
            break;
        case 'getAllTiposGPS';
            $tipoGPSController->getAllTiposGPS();
            break;
        case 'updateTipoGPS';
            $tipoGPSController->updateTipoGPS();
            break;
        case 'deleteTipoGPS';
            $tipoGPSController->deleteTipoGPS();
            break;        

        default:
            echo json_encode(['error' => 'Invalid action']);
            break;
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Server error: ' . $e->getMessage()]);
}