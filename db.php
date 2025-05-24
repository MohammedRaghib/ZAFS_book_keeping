<?php
$host = 'localhost';
$dbname = 'zafs';
$username = 'Admin';
$password = '&(3w92^$&NeTgNyEFM';
/*
    CREATE TABLE products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        purchase_price DECIMAL(10,2) NOT NULL,
        selling_price DECIMAL(10,2) NOT NULL,
        stock_quantity INT NOT NULL,
        expiry_date DATE
    );

    CREATE TABLE purchases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        purchase_price DECIMAL(10,2) NOT NULL,
        date DATE NOT NULL,
        supplier_name VARCHAR(255),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE sales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        selling_price DECIMAL(10,2) NOT NULL,
        date DATE NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE reports (
        id INT AUTO_INCREMENT PRIMARY KEY,
        month VARCHAR(7) NOT NULL, -- Stores "YYYY-MM" format
        total_revenue DECIMAL(10,2) NOT NULL,
        total_expenses DECIMAL(10,2) NOT NULL,
        profit DECIMAL(10,2) NOT NULL,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
*/

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}
