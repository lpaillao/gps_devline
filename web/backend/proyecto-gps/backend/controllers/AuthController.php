<?php
// controllers/AuthController.php
namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Firebase\JWT\JWT;

class AuthController {
    public function login(Request $request, Response $response) {
        // Implementar lógica de login
        $response->getBody()->write(json_encode(['message' => 'Login successful']));
        return $response->withHeader('Content-Type', 'application/json');
    }

    public function register(Request $request, Response $response) {
        // Implementar lógica de registro
        $response->getBody()->write(json_encode(['message' => 'Registration successful']));
        return $response->withHeader('Content-Type', 'application/json');
    }
}