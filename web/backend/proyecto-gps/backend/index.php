// index.php
<?php
use Slim\Factory\AppFactory;
use Dotenv\Dotenv;

require __DIR__ . '/vendor/autoload.php';

$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

$app = AppFactory::create();

// Configuración de rutas
require __DIR__ . '/routes/api.php';

$app->addErrorMiddleware(true, true, true);

$app->run();