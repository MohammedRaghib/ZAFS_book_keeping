# ZAFS Book Keeping

A simple bookkeeping web application to manage products, sales, purchases, and profit reports for small businesses.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**ZAFS Book Keeping** is a PHP-based application designed to help small business owners track their inventory, sales, purchases, and generate monthly profit reports. It provides a clean user interface for easy data entry and visualization.

---

## Features

- **Product Management**: Add, edit, and delete products.
- **Sales Management**: Record and edit sales transactions.
- **Purchase Management**: Log purchases from suppliers.
- **Reporting**: Generate and view monthly profit reports.
- **Responsive Design**: Usable on both desktop and mobile devices.
- **Search & Filtering**: Quickly filter through products, sales, and purchases.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MohammedRaghib/ZAFS_book_keeping.git
   ```
2. **Setup your server:**
   - Ensure you have PHP (v7.0+) and a web server (like Apache or Nginx) installed.
   - Place the project files in your web server's directory (e.g., `htdocs` or `www`).

3. **Database setup:**
   - Create a MySQL database.
   - Import the required tables (please refer to the project or contact the maintainer for the SQL schema if not included).

4. **Configure database connection:**
   - Update the database credentials in your PHP files as needed.

---

## Usage

- Navigate to the main page in your browser (e.g., `http://localhost/ZAFS_book_keeping/`).
- Use the navigation bar to move between Products, Sales, Purchases, and Reports.
- Add, edit, or delete records as needed.
- Generate reports from the Reports section.

---

## Project Structure

- `Products.php` – Manage products.
- `Sales.php` – Manage sales transactions.
- `Purchases.php` – Manage purchase records.
- `Reports.php` – Generate and view profit reports.
- `Nav.php` – Navigation bar.
- `base.css` – Styling.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

---
