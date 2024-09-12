<?php
// middleware/AuthMiddleware.php
namespace App\Middleware;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface as RequestHandler;
use Firebase\JWT\JWT;

class AuthMiddleware implements MiddlewareInterface {
    public function process(Request $request, RequestHandler $handler): Response {
        $token = $request->getHeaderLine('Authorization');

        if (!$token) {
            $response = new \Slim\Psr7\Response();
            return $response
                ->withStatus(401)
                ->withHeader('Content-Type', 'application/json')
                ->write(json_encode(['error' => 'No token provided']));
        }

        try {
            $decoded = JWT::decode($token, getenv('JWT_SECRET'), ['HS256']);
            $request = $request->withAttribute('user', $decoded);
            return $handler->handle($request);
        } catch (\Exception $e) {
            $response = new \Slim\Psr7\Response();
            return $response
                ->withStatus(401)
                ->withHeader('Content-Type', 'application/json')
                ->write(json_encode(['error' => 'Invalid token']));
        }
    }
}