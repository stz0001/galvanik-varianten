<?php
// Application configuration
define('APP_NAME', 'Variantenexplorer');
define('APP_VERSION', '2.0');

// Database configuration
define('DB_HOST', 'localhost');
define('DB_NAME', 'varianten');
define('DB_USER', 'postgres');
define('DB_PASS', 'postgres');

// PDO connection
function getDB() {
    try {
        $dsn = "pgsql:host=" . DB_HOST . ";dbname=" . DB_NAME;
        $pdo = new PDO($dsn, DB_USER, DB_PASS);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        return $pdo;
    } catch (PDOException $e) {
        die("Connection failed: " . $e->getMessage());
    }
}

// Helper function for HTML escaping
function h($str) {
    return htmlspecialchars($str ?? '', ENT_QUOTES, 'UTF-8');
}

// Render navigation with active state
function renderNavigation($currentPage = '') {
    $pages = [
        'index.php' => 'Übersicht',
        'details.php' => 'Details'
    ];
    
    echo '<nav>';
    echo '<ul>';
    foreach ($pages as $page => $label) {
        $active = ($currentPage === $page) ? ' class="active"' : '';
        echo '<li><a href="' . $page . '"' . $active . '>' . $label . '</a></li>';
    }
    echo '</ul>';
    echo '</nav>';
}

// Get CSS class for anlage
function getAnlageClass($anlage) {
    $anlage = strtolower($anlage);
    return 'anlage-' . $anlage;
}
?>