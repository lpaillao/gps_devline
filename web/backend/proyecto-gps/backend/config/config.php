<?php
// config/database.php
return [
    'driver' => 'mysql',
    'host' => getenv('DB_HOST'),
    'database' => getenv('DB_NAME'),
    'username' => getenv('DB_USER'),
    'password' => getenv('DB_PASS'),
    'charset' => 'utf8mb4',
    'collation' => 'utf8mb4_unicode_ci',
    'prefix' => '',
];

// config/config.php
<?php
return [
    'displayErrorDetails' => true,
    'addContentLengthHeader' => false,
    'jwt' => [
        'secret' => getenv('JWT_SECRET'),
        'algorithm' => 'HS256',
        'expires' => 3600 // 1 hour
    ],
];