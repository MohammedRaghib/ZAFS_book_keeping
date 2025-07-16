# Zafs Book Keeping App

**Your simple, powerful desktop solution for inventory and financial tracking.**

---

## Overview

The **Zafs Book Keeping App** is a desktop-based inventory and financial tracking system designed for small businesses. Built with Python's Tkinter library and SQLite for data storage, it offers a user-friendly graphical interface to manage products, sales, purchases, and generate monthly profit reports.

---

## Features

The application is divided into four main sections, accessible via navigation buttons:

### 1. Products Management

- **Add New Product:** Record products with details (name, category, purchase price, selling price, initial stock, optional expiry date).
- **Edit Product:** Modify existing product details.
- **Delete Product:** Remove products from inventory.
- **Stock Tracking:** Stock updates automatically based on sales and purchases.
- **Date Picker:** User-friendly calendar for expiry dates.
- **Search/Filter:** Find products by name or category.
- **Scrollable List:** View all products in a scrollable table.

---

### 2. Sales Management

- **Record New Sale:** Log sales transactions with product selection, quantity, and sale date.
- **Automatic Price Calculation:** Total price auto-calculated from quantity and selling price.
- **Stock Deduction:** Reduces stock quantity upon sale.
- **Stock Availability Check:** Prevents sales if stock is insufficient.
- **Edit Sale:** Adjust or edit previous sales; stock adjusts accordingly.
- **Delete Sale:** Remove sales records and restore deducted stock.
- **Date Picker:** Calendar for selecting sale dates.
- **Search/Filter:** Search sales records by product name.

---

### 3. Purchases Management

- **Add New Purchase:** Record new purchases by selecting product, quantity, cost, date, and supplier.
- **Stock Addition:** Increases product stock on purchase.
- **Edit Purchase:** Modify purchase details with correct stock adjustment.
- **Delete Purchase:** Remove purchase and deduct stock, with checks to prevent negative stock.
- **Date Picker:** Calendar for purchase dates.
- **Search/Filter:** Search purchases by product or supplier.

---

### 4. Reports

- **Generate Monthly Profit Reports:** Calculates total revenue, expenses, and net profit for any selected month.
- **Dynamic Calculation:** Aggregates revenue/expenses from sales and purchases.
- **Store/Update Reports:** Automatically saves or updates reports monthly.
- **View Stored Reports:** Lists all generated monthly reports.
- **Profit Highlighting:** Profits shown in green (positive) or red (negative).
- **Delete Report:** Remove stored reports (summary only, not underlying data).
- **Date Picker:** Select month for report generation.

---

## How to Run the Application

### Prerequisites

- **Python 3.x** installed
- **tkcalendar** library

### Installation Steps

1. **Save the Code:**  
   Save the provided Python code as `inventory_app.py` (or any `.py` filename).

2. **Install tkcalendar:**  
   ```bash
   pip install tkcalendar
   ```

3. **Run the Application:**  
   Navigate to your script's directory and run:
   ```bash
   python inventory_app.py
   ```

The application window will now appear.

---

## Database

- Uses **SQLite**; a file named `inventory.db` will be created in the script's directory on first run.
- All product, sales, purchase, and report data are stored in this file.

---

## How to Use the App

### Navigation

- Use the top buttons (**Products**, **Sales**, **Purchases**, **Reports**) to switch sections.

### Products Tab

- **Add Product:** Fill in "Add New Product" and click *Add Product*. Use *Select Date* for expiry.
- **Edit Product:** Right-click a product in the list, select *Edit Product*, change details, and click *Update Product*. *Cancel Edit* reverts changes.
- **Delete Product:** Right-click and select *Delete Product*. Confirm deletion.
- **Search:** Filter products using the search bar.

### Sales Tab

- **Record Sale:** Select a product, enter quantity, use *Select Date*, then click *Record Sale*.
- **Edit Sale:** Right-click a sale, select *Edit Sale*, adjust, and update.
- **Delete Sale:** Right-click and remove sale, restoring stock.
- **Search:** Filter sales by product name.

### Purchases Tab

- **Add Purchase:** Select product, fill details, pick date, and click *Add Purchase*.
- **Edit Purchase:** Right-click, select *Edit Purchase*, modify, update.
- **Delete Purchase:** Right-click, select *Delete Purchase*, confirm.
- **Search:** Filter by product or supplier.

### Reports Tab

- **Generate Report:** Select date, click *Generate Report*. Appears in "Stored Monthly Reports".
- **Delete Report:** Right-click and remove stored report.

---

## Creating a Standalone Executable (.exe)

Package your Python app into a single executable for Windows:

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Generate the Executable:**
   ```bash
   pyinstaller --onefile --windowed inventory_app.py
   ```
   - `--onefile`: Creates a single file.
   - `--windowed`: Suppresses console window.

3. **Find the Executable:**  
   Located in the `dist` folder inside your project directory.

---

## Future Enhancement Ideas

- **User Authentication:** Add login/user management.
- **Detailed Reports:** Annual reports, product summaries, graphical analysis.
- **Export Data:** Export to CSV/Excel.
- **Alerts/Notifications:** Low stock or expiry reminders.
- **Supplier Management:** Dedicated supplier section.
- **Barcode Scanning:** For faster product selection.
- **Error Logging:** More robust error/debug logging.

---

## License

[MIT License](LICENSE) (or specify your license here)

---

## Contact

For support or feedback, please reach out to the project maintainer.