<?php
// db_init.php - Database initialization file
// This file is responsible for creating the database and tables

// Database connection information
$db_host = "localhost";
$db_user = "root";
$db_pass = "grq990823";
$db_port = "3306";
$db_name = "dublinbikesystem";

// Step 1: Connect to MySQL server (without specifying a database)
try {
    $pdo = new PDO("mysql:host=$db_host;port=$db_port", $db_user, $db_pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Connection success message
    echo "<p>Successfully connected to MySQL server.</p>";
    
    // Step 2: Create database (if it doesn't exist)
    $sql = "CREATE DATABASE IF NOT EXISTS $db_name";
    $pdo->exec($sql);
    echo "<p>Database '$db_name' has been created or already exists.</p>";

    // Step 3: Select the database
    $pdo->exec("USE $db_name");
    echo "<p>Database '$db_name' selected.</p>";
    
    // Step 4: Create users table
    $sql = "CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fullname VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        terms_accepted TINYINT(1) NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL,
        last_login DATETIME,
        status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
        verification_token VARCHAR(255),
        is_verified TINYINT(1) DEFAULT 0,
        reset_token VARCHAR(255),
        reset_token_expiry DATETIME
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
    
    $pdo->exec($sql);
    echo "<p>Users table has been created or already exists.</p>";
    
    echo "<p>Database initialization complete! You can now use the registration system.</p>";
    
} catch(PDOException $e) {
    die("Database initialization error: " . $e->getMessage());
}
?>
