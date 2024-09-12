<?php
// routes/api.php
use Slim\Routing\RouteCollectorProxy;

$app->group('/api', function (RouteCollectorProxy $group) {
    $group->post('/login', 'App\Controllers\AuthController:login');
    $group->post('/register', 'App\Controllers\AuthController:register');

    $group->group('/users', function (RouteCollectorProxy $group) {
        $group->get('', 'App\Controllers\UserController:getUsers');
        $group->post('', 'App\Controllers\UserController:createUser');
        // Agregar otras rutas para usuarios
    });

    // Agregar rutas para perfiles, menús y GPS
});