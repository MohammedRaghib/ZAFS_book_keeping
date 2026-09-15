# ZAFS Book Keeping

A simple bookkeeping web application to manage products, sales, purchases, and profit reports for small businesses.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Docker Setup](#docker-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
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

## Docker Setup

The project includes a `Dockerfile` and `docker-compose.yml` for containerized development. This runs the PHP app in Apache and a MySQL 8.0 database.

1. **Prerequisites:**
   - Ensure [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/) are installed.

2. **Configure environment variables (optional):**
   - Docker Compose reads the `.env` file automatically and all values have sensible defaults, so no setup is needed to get started.
   - To customize the ports or database credentials, edit `.env` (e.g., `APP_PORT`, `MYSQL_ROOT_PASSWORD`). This file is git-ignored — never commit it.

3. **Start the containers:**
   ```bash
   docker-compose up -d
   ```
   This builds and starts two containers:
   - `zafs` – the PHP/Apache application, exposed on `http://localhost:8080`
   - `zafs-db` – the MySQL 8.0 database on port `3306`

4. **Access the application:**
   - Open `http://localhost:8080` in your browser. The app redirects to `Products.php`.

5. **Create the schema (first time only):**
   - The tables are not auto-created. Run the `CREATE TABLE` statements from `db.php` inside the MySQL container:
     ```bash
     docker exec -it zafs-db mysql -u root -prootpass zafs
     ```
     Then paste the schema from `db.php` and exit with `exit`. Use the root password from `.env` (`MYSQL_ROOT_PASSWORD`) if you changed it.

6. **Stop the containers:**
   ```bash
   docker-compose down
   ```
   Database data is persisted in the `db_data` volume and survives container restarts. To remove it along with the containers, use `docker-compose down -v`.

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
- `index.php` – Redirects to `Products.php`.
- `Nav.php` – Navigation bar.
- `base.css` – Styling.
- `db.php` – Database connection (uses `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS` env vars with defaults).
- `Dockerfile` – Builds the PHP/Apache container.
- `docker-compose.yml` – Orchestrates the app and MySQL services.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

---
