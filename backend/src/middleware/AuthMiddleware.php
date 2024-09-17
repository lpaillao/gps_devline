<?php

namespace App\Middleware;

class AuthMiddleware {
    public function __invoke($request, $response, $next) {
        if (!isset($_SESSION['user_id'])) {
            return $response->withJson(['error' => 'Unauthorized'], 401);
        }
        return $next($request, $response);
    }
}