import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import Calendar

class Database:
    def __init__(self, db_name="inventory.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self._check_and_migrate_schema() # Call migration after ensuring tables exist

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                purchase_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                stock_quantity REAL NOT NULL,
                expiry_date TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                sale_date TEXT NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                cost_price REAL NOT NULL,
                supplier_name TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL UNIQUE,
                total_revenue REAL NOT NULL,
                total_expenses REAL NOT NULL,
                profit REAL NOT NULL
            )
        """)
        self.conn.commit()

    def _check_and_migrate_schema(self):
        tables_to_check = {
            "products": {"column": "stock_quantity", "current_schema_sql": """
                CREATE TABLE products_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT,
                    purchase_price REAL NOT NULL,
                    selling_price REAL NOT NULL,
                    stock_quantity REAL NOT NULL,
                    expiry_date TEXT
                )
            """},
            "sales": {"column": "quantity", "current_schema_sql": """
                CREATE TABLE sales_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity REAL NOT NULL,
                    sale_date TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """},
            "purchases": {"column": "quantity", "current_schema_sql": """
                CREATE TABLE purchases_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity REAL NOT NULL,
                    purchase_date TEXT NOT NULL,
                    cost_price REAL NOT NULL,
                    supplier_name TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """}
        }

        for table_name, details in tables_to_check.items():
            column_name = details["column"]
            try:
                self.cursor.execute(f"PRAGMA table_info({table_name});")
                columns_info = self.cursor.fetchall()
                current_type = None
                for col in columns_info:
                    if col[1] == column_name:
                        current_type = col[2].upper()
                        break

                if current_type == "INTEGER":
                    messagebox.showinfo("Database Migration",
                                        f"Migrating '{column_name}' in '{table_name}' table from INTEGER to REAL. "
                                        "This may take a moment.")
                    self._perform_migration(table_name, details["current_schema_sql"])
                    messagebox.showinfo("Database Migration",
                                        f"Migration for '{column_name}' in '{table_name}' complete.")
            except sqlite3.OperationalError as e:
                if "no such table" not in str(e):
                    messagebox.showerror("Database Error", f"Error checking schema for {table_name}: {e}")
            except Exception as e:
                messagebox.showerror("Migration Error", f"Failed to migrate schema for {table_name}: {e}")

    def _perform_migration(self, table_name, new_table_schema_sql):
        old_table_name = f"{table_name}_old"
        self.conn.execute("BEGIN TRANSACTION;")
        try:
            self.cursor.execute(f"ALTER TABLE {table_name} RENAME TO {old_table_name};")
            new_table_create_sql = new_table_schema_sql.replace(f"{table_name}_new", table_name)
            self.cursor.execute(new_table_create_sql)

            self.cursor.execute(f"PRAGMA table_info({old_table_name});")
            old_columns = [col[1] for col in self.cursor.fetchall()]
            columns_str = ", ".join(old_columns)
            placeholders = ", ".join(["?" for _ in old_columns])

            self.cursor.execute(f"SELECT {columns_str} FROM {old_table_name};")
            data_to_copy = self.cursor.fetchall()

            self.cursor.executemany(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});", data_to_copy)

            self.cursor.execute(f"DROP TABLE {old_table_name};")

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Migration failed for table {table_name}: {e}")

    def add_product(self, name, category, purchase_price, selling_price, stock_quantity, expiry_date):
        try:
            self.cursor.execute("INSERT INTO products (name, category, purchase_price, selling_price, stock_quantity, expiry_date) VALUES (?, ?, ?, ?, ?, ?)",
                                (name, category, purchase_price, selling_price, stock_quantity, expiry_date))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Product '{name}' already exists.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {e}")
            return False

    def get_products(self):
        self.cursor.execute("SELECT id, name, category, purchase_price, selling_price, stock_quantity, expiry_date FROM products ORDER BY name ASC")
        return self.cursor.fetchall()

    def get_product_by_id(self, product_id):
        self.cursor.execute("SELECT id, name, category, purchase_price, selling_price, stock_quantity, expiry_date FROM products WHERE id = ?", (product_id,))
        return self.cursor.fetchone()

    def get_product_by_name(self, name):
        self.cursor.execute("SELECT id, name, category, purchase_price, selling_price, stock_quantity, expiry_date FROM products WHERE name = ?", (name,))
        return self.cursor.fetchone()

    def update_product(self, product_id, name, category, purchase_price, selling_price, stock_quantity, expiry_date):
        try:
            self.cursor.execute("UPDATE products SET name=?, category=?, purchase_price=?, selling_price=?, stock_quantity=?, expiry_date=? WHERE id=?",
                                (name, category, purchase_price, selling_price, stock_quantity, expiry_date, product_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Product name '{name}' already exists for another product.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {e}")
            return False

    def delete_product(self, product_id):
        try:
            self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {e}")
            return False

    def update_product_stock(self, product_id, quantity_change):
        try:
            self.cursor.execute("UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                                (quantity_change, product_id))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Stock Update Error", f"Failed to update stock: {e}")
            return False

    def record_sale(self, product_id, quantity, total_price, sale_date):
        try:
            self.cursor.execute("INSERT INTO sales (product_id, quantity, total_price, sale_date) VALUES (?, ?, ?, ?)",
                                (product_id, quantity, total_price, sale_date))
            self.conn.commit()
            self.update_product_stock(product_id, -quantity)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record sale: {e}")
            return False

    def get_sales_report(self):
        self.cursor.execute("""
            SELECT s.id, p.name, s.quantity, s.total_price, s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.sale_date DESC
        """)
        return self.cursor.fetchall()

    def get_sale_by_id(self, sale_id):
        self.cursor.execute("SELECT id, product_id, quantity, total_price, sale_date FROM sales WHERE id = ?", (sale_id,))
        return self.cursor.fetchone()

    def update_sale(self, sale_id, product_id, new_quantity, new_total_price, new_sale_date, previous_quantity):
        try:
            stock_adjustment = new_quantity - previous_quantity

            self.cursor.execute("UPDATE sales SET product_id=?, quantity=?, total_price=?, sale_date=? WHERE id=?",
                                (product_id, new_quantity, new_total_price, new_sale_date, sale_id))
            self.conn.commit()

            if stock_adjustment != 0:
                self.update_product_stock(product_id, -stock_adjustment)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update sale: {e}")
            return False

    def delete_sale(self, sale_id):
        try:
            self.cursor.execute("SELECT product_id, quantity FROM sales WHERE id = ?", (sale_id,))
            deleted_sale_data = self.cursor.fetchone()

            if deleted_sale_data:
                product_id, quantity = deleted_sale_data
                self.cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
                self.conn.commit()
                self.update_product_stock(product_id, quantity)
                return True
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete sale: {e}")
            return False

    def record_purchase(self, product_id, quantity, cost_price, purchase_date, supplier_name):
        try:
            self.cursor.execute("INSERT INTO purchases (product_id, quantity, cost_price, purchase_date, supplier_name) VALUES (?, ?, ?, ?, ?)",
                                (product_id, quantity, cost_price, purchase_date, supplier_name))
            self.conn.commit()
            self.update_product_stock(product_id, quantity)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record purchase: {e}")
            return False

    def get_purchases_report(self):
        self.cursor.execute("""
            SELECT pu.id, p.name, pu.quantity, pu.cost_price, pu.purchase_date, pu.supplier_name
            FROM purchases pu
            JOIN products p ON pu.product_id = p.id
            ORDER BY pu.purchase_date DESC
        """)
        return self.cursor.fetchall()

    def get_purchase_by_id(self, purchase_id):
        self.cursor.execute("SELECT id, product_id, quantity, cost_price, purchase_date, supplier_name FROM purchases WHERE id = ?", (purchase_id,))
        return self.cursor.fetchone()

    def update_purchase(self, purchase_id, product_id, new_quantity, new_cost_price, new_purchase_date, new_supplier_name, previous_quantity):
        try:
            stock_adjustment = new_quantity - previous_quantity

            if stock_adjustment < 0:
                current_product_data = self.get_product_by_id(product_id)
                if current_product_data:
                    current_stock = current_product_data[5]
                    if current_stock < abs(stock_adjustment):
                        messagebox.showerror("Stock Error", f"Cannot reduce purchase quantity. Not enough stock to deduct {abs(stock_adjustment):.2f} units. Current stock: {current_stock:.2f}")
                        return False
                else:
                    messagebox.showerror("Error", "Product not found for stock check.")
                    return False

            self.cursor.execute("UPDATE purchases SET product_id=?, quantity=?, cost_price=?, purchase_date=?, supplier_name=? WHERE id=?",
                                (product_id, new_quantity, new_cost_price, new_purchase_date, new_supplier_name, purchase_id))
            self.conn.commit()

            if stock_adjustment != 0:
                self.update_product_stock(product_id, stock_adjustment)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update purchase: {e}")
            return False

    def delete_purchase(self, purchase_id):
        try:
            self.cursor.execute("SELECT product_id, quantity FROM purchases WHERE id = ?", (purchase_id,))
            deleted_purchase_data = self.cursor.fetchone()

            if deleted_purchase_data:
                product_id, quantity = deleted_purchase_data
                current_product_data = self.get_product_by_id(product_id)
                if current_product_data:
                    current_stock = current_product_data[5]
                    if current_stock < quantity:
                        messagebox.showerror("Stock Error", f"Cannot delete this purchase. Deleting would make stock negative. Current stock: {current_stock:.2f}, Purchase quantity: {quantity:.2f}")
                        return False
                else:
                    messagebox.showerror("Error", "Product not found for stock check.")
                    return False

                self.cursor.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
                self.conn.commit()
                self.update_product_stock(product_id, -quantity)
                return True
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete purchase: {e}")
            return False

    def calculate_monthly_revenue(self, month_str):
        self.cursor.execute("SELECT SUM(total_price) FROM sales WHERE SUBSTR(sale_date, 1, 7) = ?", (month_str,))
        return self.cursor.fetchone()[0] or 0.0

    def calculate_monthly_expenses(self, month_str):
        self.cursor.execute("SELECT SUM(quantity * cost_price) FROM purchases WHERE SUBSTR(purchase_date, 1, 7) = ?", (month_str,))
        return self.cursor.fetchone()[0] or 0.0

    def save_or_update_report(self, month, total_revenue, total_expenses, profit):
        try:
            self.cursor.execute("""
                INSERT INTO reports (month, total_revenue, total_expenses, profit)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(month) DO UPDATE SET
                    total_revenue = EXCLUDED.total_revenue,
                    total_expenses = EXCLUDED.total_expenses,
                    profit = EXCLUDED.profit
            """, (month, total_revenue, total_expenses, profit))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to save/update report: {e}")
            return False

    def get_stored_reports(self):
        self.cursor.execute("SELECT id, month, total_revenue, total_expenses, profit FROM reports ORDER BY month DESC")
        return self.cursor.fetchall()

    def delete_stored_report(self, report_id):
        try:
            self.cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to delete report: {e}")
            return False

    def close(self):
        self.conn.close()

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("1000x700")
        self.db = Database()

        self.create_widgets()
        self.show_frame("products")

    def create_widgets(self):
        nav_frame = tk.Frame(self, bg="#333", height=50)
        nav_frame.pack(fill="x", side="top")

        s = ttk.Style()
        s.configure('TButton', font=('Arial', 12), padding=10)
        s.map('TButton', background=[('active', '#555')], foreground=[('active', 'white')])

        btn_products = ttk.Button(nav_frame, text="Products", command=lambda: self.show_frame("products"))
        btn_products.pack(side="left", padx=10, pady=5)

        btn_sales = ttk.Button(nav_frame, text="Sales", command=lambda: self.show_frame("sales"))
        btn_sales.pack(side="left", padx=10, pady=5)

        btn_purchases = ttk.Button(nav_frame, text="Purchases", command=lambda: self.show_frame("purchases"))
        btn_purchases.pack(side="left", padx=10, pady=5)

        btn_reports = ttk.Button(nav_frame, text="Reports", command=lambda: self.show_frame("reports"))
        btn_reports.pack(side="left", padx=10, pady=5)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.frames = {}
        for F in (ProductsFrame, SalesFrame, PurchasesFrame, ReportsFrame):
            page_name = F.__name__.replace("Frame", "").lower()
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'refresh_data'):
            frame.refresh_data()

class ProductsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.edit_mode = False
        self.current_product_id = None

        self.input_frame = tk.LabelFrame(self, text="Add New Product", padx=10, pady=10)
        self.input_frame.pack(pady=10, fill="x")

        tk.Label(self.input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.input_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.category_entry = tk.Entry(self.input_frame, width=40)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Purchase Price:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.purchase_price_entry = tk.Entry(self.input_frame, width=40)
        self.purchase_price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Selling Price:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.selling_price_entry = tk.Entry(self.input_frame, width=40)
        self.selling_price_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Stock Quantity:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.stock_quantity_entry = tk.Entry(self.input_frame, width=40)
        self.stock_quantity_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Expiry Date:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.expiry_date_display = tk.StringVar()
        self.expiry_date_label = tk.Label(self.input_frame, textvariable=self.expiry_date_display, width=37, anchor="w", relief="sunken", bd=1)
        self.expiry_date_label.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.date_picker_button = ttk.Button(self.input_frame, text="Select Date", command=self.open_date_picker)
        self.date_picker_button.grid(row=5, column=2, padx=5, pady=5)

        self.action_button = ttk.Button(self.input_frame, text="Add Product", command=self.handle_product_action)
        self.action_button.grid(row=6, column=0, columnspan=3, pady=10)

        self.cancel_button = ttk.Button(self.input_frame, text="Cancel Edit", command=self.reset_form)
        self.cancel_button.grid(row=7, column=0, columnspan=3, pady=5)
        self.cancel_button.grid_remove()

        products_display_frame = tk.LabelFrame(self, text="Product List", padx=10, pady=10)
        products_display_frame.pack(pady=10, fill="both", expand=True)

        self.search_entry = tk.Entry(products_display_frame, width=50)
        self.search_entry.pack(pady=5, padx=5, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_products)
        self.search_entry.insert(0, "Search products...")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_search_placeholder)

        tree_frame = tk.Frame(products_display_frame)
        tree_frame.pack(fill="both", expand=True)

        self.products_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Category", "Purchase Price", "Selling Price", "Stock", "Expiry Date"), show="headings")
        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Name", text="Name")
        self.products_tree.heading("Category", text="Category")
        self.products_tree.heading("Purchase Price", text="Purchase Price")
        self.products_tree.heading("Selling Price", text="Selling Price")
        self.products_tree.heading("Stock", text="Stock")
        self.products_tree.heading("Expiry Date", text="Expiry Date")

        self.products_tree.column("ID", width=30, anchor="center")
        self.products_tree.column("Name", width=120)
        self.products_tree.column("Category", width=80)
        self.products_tree.column("Purchase Price", width=90, anchor="e")
        self.products_tree.column("Selling Price", width=90, anchor="e")
        self.products_tree.column("Stock", width=60, anchor="e")
        self.products_tree.column("Expiry Date", width=100, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.products_tree.yview)
        vsb.pack(side='right', fill='y')
        self.products_tree.configure(yscrollcommand=vsb.set)

        self.products_tree.pack(side='left', fill="both", expand=True)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Product", command=self.load_product_for_edit)
        self.context_menu.add_command(label="Delete Product", command=self.delete_product)
        self.products_tree.bind("<Button-3>", self.show_context_menu)

        self.refresh_data()

    def open_date_picker(self):
        def grab_date():
            selected_date = cal.selection_get()
            self.expiry_date_display.set(selected_date.strftime("%Y-%m-%d"))
            top.destroy()

        top = tk.Toplevel(self)
        top.title("Select Expiry Date")
        top.grab_set()

        current_date_str = self.expiry_date_display.get()
        initial_date = datetime.now().date()
        if current_date_str:
            try:
                initial_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        cal = Calendar(top, selectmode='day',
                       year=initial_date.year,
                       month=initial_date.month,
                       day=initial_date.day)
        cal.pack(pady=20)

        confirm_button = ttk.Button(top, text="Select", command=grab_date)
        confirm_button.pack(pady=10)

    def handle_product_action(self):
        if self.edit_mode:
            self.update_product()
        else:
            self.add_product()

    def add_product(self):
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()
        purchase_price_str = self.purchase_price_entry.get().strip()
        selling_price_str = self.selling_price_entry.get().strip()
        stock_quantity_str = self.stock_quantity_entry.get().strip()
        expiry_date = self.expiry_date_display.get().strip()

        if not name or not category or not purchase_price_str or not selling_price_str or not stock_quantity_str:
            messagebox.showerror("Input Error", "Name, Category, Purchase Price, Selling Price, and Stock Quantity are required.")
            return

        try:
            purchase_price = float(purchase_price_str)
            selling_price = float(selling_price_str)
            stock_quantity = float(stock_quantity_str)
            if purchase_price < 0 or selling_price < 0 or stock_quantity < 0:
                messagebox.showerror("Input Error", "Prices and stock must be non-negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Prices and Stock Quantity must be numbers.")
            return

        if expiry_date == "":
            expiry_date = None

        if self.controller.db.add_product(name, category, purchase_price, selling_price, stock_quantity, expiry_date):
            messagebox.showinfo("Success", f"Product '{name}' added successfully.")
            self.reset_form()
            self.refresh_data()
            self.controller.frames["sales"].refresh_data()
            self.controller.frames["purchases"].refresh_data()
            self.controller.frames["reports"].refresh_data()

    def load_product_for_edit(self):
        selected_item = self.products_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a product to edit.")
            return

        product_id = self.products_tree.item(selected_item)['values'][0]
        product_data = self.controller.db.get_product_by_id(product_id)

        if product_data:
            self.edit_mode = True
            self.current_product_id = product_data[0]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, product_data[1])
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, product_data[2])
            self.purchase_price_entry.delete(0, tk.END)
            self.purchase_price_entry.insert(0, product_data[3])
            self.selling_price_entry.delete(0, tk.END)
            self.selling_price_entry.insert(0, product_data[4])
            self.stock_quantity_entry.delete(0, tk.END)
            self.stock_quantity_entry.insert(0, product_data[5])
            self.expiry_date_display.set(product_data[6] if product_data[6] else "")

            self.action_button.config(text="Update Product")
            self.cancel_button.grid()
            self.input_frame.config(text=f"Edit Product (ID: {self.current_product_id})")

    def update_product(self):
        if not self.current_product_id:
            messagebox.showerror("Error", "No product selected for update.")
            return

        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()
        purchase_price_str = self.purchase_price_entry.get().strip()
        selling_price_str = self.selling_price_entry.get().strip()
        stock_quantity_str = self.stock_quantity_entry.get().strip()
        expiry_date = self.expiry_date_display.get().strip()

        if not name or not category or not purchase_price_str or not selling_price_str or not stock_quantity_str:
            messagebox.showerror("Input Error", "Name, Category, Purchase Price, Selling Price, and Stock Quantity are required.")
            return

        try:
            purchase_price = float(purchase_price_str)
            selling_price = float(selling_price_str)
            stock_quantity = float(stock_quantity_str)
            if purchase_price < 0 or selling_price < 0 or stock_quantity < 0:
                messagebox.showerror("Input Error", "Prices and stock must be non-negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Prices and Stock Quantity must be numbers.")
            return

        if expiry_date == "":
            expiry_date = None

        if self.controller.db.update_product(self.current_product_id, name, category, purchase_price, selling_price, stock_quantity, expiry_date):
            messagebox.showinfo("Success", f"Product '{name}' updated successfully.")
            self.reset_form()
            self.refresh_data()
            self.controller.frames["sales"].refresh_data()
            self.controller.frames["purchases"].refresh_data()
            self.controller.frames["reports"].refresh_data()

    def delete_product(self):
        selected_item = self.products_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a product to delete.")
            return

        product_id = self.products_tree.item(selected_item)['values'][0]
        product_name = self.products_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product '{product_name}' (ID: {product_id})?"):
            if self.controller.db.delete_product(product_id):
                messagebox.showinfo("Success", f"Product '{product_name}' deleted successfully.")
                self.refresh_data()
                self.reset_form()
                self.controller.frames["sales"].refresh_data()
                self.controller.frames["purchases"].refresh_data()
                self.controller.frames["reports"].refresh_data()

    def reset_form(self):
        self.edit_mode = False
        self.current_product_id = None
        self.clear_entries()
        self.action_button.config(text="Add Product")
        self.cancel_button.grid_remove()
        self.input_frame.config(text="Add New Product")

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.purchase_price_entry.delete(0, tk.END)
        self.selling_price_entry.delete(0, tk.END)
        self.stock_quantity_entry.delete(0, tk.END)
        self.expiry_date_display.set("")

    def refresh_data(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        products = self.controller.db.get_products()
        for product in products:
            formatted_product = list(product)
            formatted_product[5] = f"{product[5]:.2f}"
            self.products_tree.insert("", "end", values=formatted_product)
        self.filter_products()

    def filter_products(self, event=None):
        search_term = self.search_entry.get().lower()
        if search_term == "search products...":
            search_term = ""

        all_products = self.controller.db.get_products()

        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        filtered_products = [
            p for p in all_products
            if search_term in str(p[1]).lower() or
               search_term in str(p[2]).lower()
        ]

        for product in filtered_products:
            formatted_product = list(product)
            formatted_product[5] = f"{product[5]:.2f}"
            self.products_tree.insert("", "end", values=formatted_product)

    def clear_search_placeholder(self, event):
        if self.search_entry.get() == "Search products...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg='black')

    def restore_search_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search products...")
            self.search_entry.config(fg='grey')

    def show_context_menu(self, event):
        item_id = self.products_tree.identify_row(event.y)
        if item_id:
            self.products_tree.selection_set(item_id)
            self.products_tree.focus(item_id)
            self.context_menu.post(event.x_root, event.y_root)

class SalesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.edit_mode = False
        self.current_sale_id = None
        self.previous_sale_quantity = 0.0

        self.input_frame = tk.LabelFrame(self, text="Record New Sale", padx=10, pady=10)
        self.input_frame.pack(pady=10, fill="x")

        tk.Label(self.input_frame, text="Product Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.product_combobox = ttk.Combobox(self.input_frame, width=37)
        self.product_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.product_combobox.bind("<<ComboboxSelected>>", self.on_product_select)

        tk.Label(self.input_frame, text="Available Stock:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.available_stock_label = tk.Label(self.input_frame, text="N/A", width=37, anchor="w", relief="sunken", bd=1)
        self.available_stock_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.input_frame, text="Quantity:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = tk.Entry(self.input_frame, width=40)
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=5)
        self.quantity_entry.bind("<KeyRelease>", self.calculate_total_price)

        tk.Label(self.input_frame, text="Price per unit:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.price_per_unit_label = tk.Label(self.input_frame, text="N/A", width=37, anchor="w", relief="sunken", bd=1)
        self.price_per_unit_label.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.input_frame, text="Total Price:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.total_price_label = tk.Label(self.input_frame, text="0.00", width=37, anchor="w", relief="sunken", bd=1)
        self.total_price_label.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.input_frame, text="Sale Date:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.sale_date_display = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.sale_date_label = tk.Label(self.input_frame, textvariable=self.sale_date_display, width=37, anchor="w", relief="sunken", bd=1)
        self.sale_date_label.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.date_picker_button = ttk.Button(self.input_frame, text="Select Date", command=self.open_date_picker)
        self.date_picker_button.grid(row=5, column=2, padx=5, pady=5)

        self.action_button = ttk.Button(self.input_frame, text="Record Sale", command=self.handle_sale_action)
        self.action_button.grid(row=6, column=0, columnspan=3, pady=10)

        self.cancel_button = ttk.Button(self.input_frame, text="Cancel Edit", command=self.reset_form)
        self.cancel_button.grid(row=7, column=0, columnspan=3, pady=5)
        self.cancel_button.grid_remove()

        sales_display_frame = tk.LabelFrame(self, text="Sales Records", padx=10, pady=10)
        sales_display_frame.pack(pady=10, fill="both", expand=True)

        self.search_entry = tk.Entry(sales_display_frame, width=50)
        self.search_entry.pack(pady=5, padx=5, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_sales)
        self.search_entry.insert(0, "Search sales...")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_search_placeholder)

        tree_frame = tk.Frame(sales_display_frame)
        tree_frame.pack(fill="both", expand=True)

        self.sales_tree = ttk.Treeview(tree_frame, columns=("ID", "Product", "Quantity", "Total Price", "Date"), show="headings")
        self.sales_tree.heading("ID", text="ID")
        self.sales_tree.heading("Product", text="Product Name")
        self.sales_tree.heading("Quantity", text="Quantity")
        self.sales_tree.heading("Total Price", text="Total Price")
        self.sales_tree.heading("Date", text="Sale Date")

        self.sales_tree.column("ID", width=30, anchor="center")
        self.sales_tree.column("Product", width=150)
        self.sales_tree.column("Quantity", width=80, anchor="e")
        self.sales_tree.column("Total Price", width=100, anchor="e")
        self.sales_tree.column("Date", width=120, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.sales_tree.yview)
        vsb.pack(side='right', fill='y')
        self.sales_tree.configure(yscrollcommand=vsb.set)

        self.sales_tree.pack(side='left', fill="both", expand=True)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Sale", command=self.load_sale_for_edit)
        self.context_menu.add_command(label="Delete Sale", command=self.delete_sale)
        self.sales_tree.bind("<Button-3>", self.show_context_menu)

        self.product_data = {}
        self.refresh_data()

    def open_date_picker(self):
        def grab_date():
            selected_date = cal.selection_get()
            self.sale_date_display.set(selected_date.strftime("%Y-%m-%d"))
            top.destroy()

        top = tk.Toplevel(self)
        top.title("Select Sale Date")
        top.grab_set()

        current_date_str = self.sale_date_display.get()
        initial_date = datetime.now().date()
        if current_date_str:
            try:
                initial_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        cal = Calendar(top, selectmode='day',
                       year=initial_date.year,
                       month=initial_date.month,
                       day=initial_date.day)
        cal.pack(pady=20)

        confirm_button = ttk.Button(top, text="Select", command=grab_date)
        confirm_button.pack(pady=10)

    def refresh_data(self):
        products = self.controller.db.get_products()
        product_names = []
        self.product_data = {}
        for prod_id, name, category, purchase_price, selling_price, stock, expiry_date in products:
            product_names.append(name)
            self.product_data[name] = {"id": prod_id, "price": selling_price, "stock": stock}
        self.product_combobox['values'] = product_names
        self.product_combobox.set("")

        self.available_stock_label.config(text="N/A")
        self.price_per_unit_label.config(text="N/A")
        self.quantity_entry.delete(0, tk.END)
        self.total_price_label.config(text="0.00")
        self.sale_date_display.set(datetime.now().strftime("%Y-%m-%d"))

        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        sales = self.controller.db.get_sales_report()
        for sale in sales:
            formatted_sale = list(sale)
            formatted_sale[2] = f"{sale[2]:.2f}"
            self.sales_tree.insert("", "end", values=formatted_sale)
        self.filter_sales()

    def on_product_select(self, event=None):
        selected_product_name = self.product_combobox.get()
        if selected_product_name in self.product_data:
            product_info = self.product_data[selected_product_name]
            self.available_stock_label.config(text=f"{product_info['stock']:.2f}")
            self.price_per_unit_label.config(text=f"{product_info['price']:.2f}")
            self.calculate_total_price()
        else:
            self.available_stock_label.config(text="N/A")
            self.price_per_unit_label.config(text="N/A")
            self.total_price_label.config(text="0.00")

    def calculate_total_price(self, event=None):
        selected_product_name = self.product_combobox.get()
        if selected_product_name not in self.product_data:
            self.total_price_label.config(text="0.00")
            return

        try:
            quantity = float(self.quantity_entry.get())
            price_per_unit = self.product_data[selected_product_name]["price"]
            total_price = quantity * price_per_unit
            self.total_price_label.config(text=f"{total_price:.2f}")
        except ValueError:
            self.total_price_label.config(text="0.00")
        except Exception:
            self.total_price_label.config(text="0.00")

    def handle_sale_action(self):
        if self.edit_mode:
            self.update_sale()
        else:
            self.record_sale()

    def record_sale(self):
        selected_product_name = self.product_combobox.get()
        quantity_str = self.quantity_entry.get().strip()
        sale_date = self.sale_date_display.get().strip()

        if not selected_product_name or not quantity_str or not sale_date:
            messagebox.showerror("Input Error", "Product, Quantity, and Sale Date are required.")
            return

        if selected_product_name not in self.product_data:
            messagebox.showerror("Error", "Selected product is not valid.")
            return

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                messagebox.showerror("Input Error", "Quantity must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number.")
            return

        product_info = self.product_data[selected_product_name]
        product_id = product_info["id"]
        current_stock = product_info["stock"]
        price_per_unit = product_info["price"]

        if quantity > current_stock:
            messagebox.showerror("Stock Error", f"Not enough stock available. Current stock: {current_stock:.2f}")
            return

        total_price = quantity * price_per_unit

        if self.controller.db.record_sale(product_id, quantity, total_price, sale_date):
            messagebox.showinfo("Success", f"Sale of {quantity:.2f} x {selected_product_name} recorded.")
            self.reset_form()
            self.refresh_data()
            self.controller.frames["products"].refresh_data()
            self.controller.frames["reports"].refresh_data()

    def load_sale_for_edit(self):
        selected_item = self.sales_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a sale to edit.")
            return

        sale_id = self.sales_tree.item(selected_item)['values'][0]
        sale_data = self.controller.db.get_sale_by_id(sale_id)

        if sale_data:
            self.edit_mode = True
            self.current_sale_id = sale_data[0]
            product_id_from_sale = sale_data[1]
            self.previous_sale_quantity = sale_data[2]

            product_info = self.controller.db.get_product_by_id(product_id_from_sale)
            if product_info:
                product_name = product_info[1]
                self.product_combobox.set(product_name)
                self.on_product_select()

            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, f"{sale_data[2]:.2f}")

            self.total_price_label.config(text=f"{sale_data[3]:.2f}")

            self.sale_date_display.set(sale_data[4])

            self.action_button.config(text="Update Sale")
            self.cancel_button.grid()
            self.input_frame.config(text=f"Edit Sale (ID: {self.current_sale_id})")

    def update_sale(self):
        if not self.current_sale_id:
            messagebox.showerror("Error", "No sale selected for update.")
            return

        selected_product_name = self.product_combobox.get()
        new_quantity_str = self.quantity_entry.get().strip()
        new_sale_date = self.sale_date_display.get().strip()

        if not selected_product_name or not new_quantity_str or not new_sale_date:
            messagebox.showerror("Input Error", "Product, Quantity, and Sale Date are required.")
            return

        if selected_product_name not in self.product_data:
            messagebox.showerror("Error", "Selected product is not valid.")
            return

        try:
            new_quantity = float(new_quantity_str)
            if new_quantity <= 0:
                messagebox.showerror("Input Error", "Quantity must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number.")
            return

        product_info = self.product_data[selected_product_name]
        product_id = product_info["id"]
        current_stock = product_info["stock"]
        price_per_unit = product_info["price"]

        stock_needed = new_quantity - self.previous_sale_quantity

        if stock_needed > 0 and current_stock < stock_needed:
            messagebox.showerror("Stock Error", f"Not enough stock available to increase quantity. Available: {current_stock:.2f}")
            return

        new_total_price = new_quantity * price_per_unit

        if self.controller.db.update_sale(self.current_sale_id, product_id, new_quantity, new_total_price, new_sale_date, self.previous_sale_quantity):
            messagebox.showinfo("Success", f"Sale (ID: {self.current_sale_id}) updated successfully.")
            self.reset_form()
            self.refresh_data()
            self.controller.frames["products"].refresh_data()
            self.controller.frames["reports"].refresh_data()

    def delete_sale(self):
        selected_item = self.sales_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a sale to delete.")
            return

        sale_id = self.sales_tree.item(selected_item)['values'][0]
        product_name = self.sales_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete sale for '{product_name}' (ID: {sale_id})?"):
            if self.controller.db.delete_sale(sale_id):
                messagebox.showinfo("Success", f"Sale (ID: {sale_id}) for '{product_name}' deleted successfully.")
                self.refresh_data()
                self.reset_form()
                self.controller.frames["products"].refresh_data()
                self.controller.frames["reports"].refresh_data()

    def reset_form(self):
        self.edit_mode = False
        self.current_sale_id = None
        self.previous_sale_quantity = 0.0
        self.product_combobox.set("")
        self.quantity_entry.delete(0, tk.END)
        self.available_stock_label.config(text="N/A")
        self.price_per_unit_label.config(text="N/A")
        self.total_price_label.config(text="0.00")
        self.sale_date_display.set(datetime.now().strftime("%Y-%m-%d"))

        self.action_button.config(text="Record Sale")
        self.cancel_button.grid_remove()
        self.input_frame.config(text="Record New Sale")

    def filter_sales(self, event=None):
        search_term = self.search_entry.get().lower()
        if search_term == "search sales...":
            search_term = ""

        all_sales = self.controller.db.get_sales_report()

        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        filtered_sales = [
            s for s in all_sales
            if search_term in str(s[1]).lower()
        ]

        for sale in filtered_sales:
            formatted_sale = list(sale)
            formatted_sale[2] = f"{sale[2]:.2f}"
            self.sales_tree.insert("", "end", values=formatted_sale)

    def clear_search_placeholder(self, event):
        if self.search_entry.get() == "Search sales...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg='black')

    def restore_search_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search sales...")
            self.search_entry.config(fg='grey')

    def show_context_menu(self, event):
        item_id = self.sales_tree.identify_row(event.y)
        if item_id:
            self.sales_tree.selection_set(item_id)
            self.sales_tree.focus(item_id)
            self.context_menu.post(event.x_root, event.y_root)

class PurchasesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.edit_mode = False
        self.current_purchase_id = None
        self.previous_purchase_quantity = 0.0

        self.input_frame = tk.LabelFrame(self, text="Add New Purchase", padx=10, pady=10)
        self.input_frame.pack(pady=10, fill="x")

        tk.Label(self.input_frame, text="Product Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.product_combobox = ttk.Combobox(self.input_frame, width=37)
        self.product_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.product_combobox.bind("<<ComboboxSelected>>", self.on_product_select)

        tk.Label(self.input_frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = tk.Entry(self.input_frame, width=40)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Cost Price per unit:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.cost_price_entry = tk.Entry(self.input_frame, width=40)
        self.cost_price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Purchase Date:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.purchase_date_display = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.purchase_date_label = tk.Label(self.input_frame, textvariable=self.purchase_date_display, width=37, anchor="w", relief="sunken", bd=1)
        self.purchase_date_label.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.date_picker_button = ttk.Button(self.input_frame, text="Select Date", command=self.open_date_picker)
        self.date_picker_button.grid(row=3, column=2, padx=5, pady=5)

        tk.Label(self.input_frame, text="Supplier Name:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.supplier_name_entry = tk.Entry(self.input_frame, width=40)
        self.supplier_name_entry.grid(row=4, column=1, padx=5, pady=5)


        self.action_button = ttk.Button(self.input_frame, text="Add Purchase", command=self.handle_purchase_action)
        self.action_button.grid(row=5, column=0, columnspan=3, pady=10)

        self.cancel_button = ttk.Button(self.input_frame, text="Cancel Edit", command=self.reset_form)
        self.cancel_button.grid(row=6, column=0, columnspan=3, pady=5)
        self.cancel_button.grid_remove()

        purchases_display_frame = tk.LabelFrame(self, text="Purchase Records", padx=10, pady=10)
        purchases_display_frame.pack(pady=10, fill="both", expand=True)

        self.search_entry = tk.Entry(purchases_display_frame, width=50)
        self.search_entry.pack(pady=5, padx=5, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_purchases)
        self.search_entry.insert(0, "Search purchases...")
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_search_placeholder)

        tree_frame = tk.Frame(purchases_display_frame)
        tree_frame.pack(fill="both", expand=True)

        self.purchases_tree = ttk.Treeview(tree_frame, columns=("ID", "Product", "Quantity", "Cost Price", "Date", "Supplier"), show="headings")
        self.purchases_tree.heading("ID", text="ID")
        self.purchases_tree.heading("Product", text="Product Name")
        self.purchases_tree.heading("Quantity", text="Quantity")
        self.purchases_tree.heading("Cost Price", text="Cost Price")
        self.purchases_tree.heading("Date", text="Purchase Date")
        self.purchases_tree.heading("Supplier", text="Supplier Name")

        self.purchases_tree.column("ID", width=30, anchor="center")
        self.purchases_tree.column("Product", width=120)
        self.purchases_tree.column("Quantity", width=80, anchor="e")
        self.purchases_tree.column("Cost Price", width=90, anchor="e")
        self.purchases_tree.column("Date", width=100, anchor="center")
        self.purchases_tree.column("Supplier", width=120)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.purchases_tree.yview)
        vsb.pack(side='right', fill='y')
        self.purchases_tree.configure(yscrollcommand=vsb.set)

        self.purchases_tree.pack(side='left', fill="both", expand=True)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Purchase", command=self.load_purchase_for_edit)
        self.context_menu.add_command(label="Delete Purchase", command=self.delete_purchase)
        self.purchases_tree.bind("<Button-3>", self.show_context_menu)

        self.product_data = {}
        self.refresh_data()

    def open_date_picker(self):
        def grab_date():
            selected_date = cal.selection_get()
            self.purchase_date_display.set(selected_date.strftime("%Y-%m-%d"))
            top.destroy()

        top = tk.Toplevel(self)
        top.title("Select Purchase Date")
        top.grab_set()

        current_date_str = self.purchase_date_display.get()
        initial_date = datetime.now().date()
        if current_date_str:
            try:
                initial_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        cal = Calendar(top, selectmode='day',
                       year=initial_date.year,
                       month=initial_date.month,
                       day=initial_date.day)
        cal.pack(pady=20)

        confirm_button = ttk.Button(top, text="Select", command=grab_date)
        confirm_button.pack(pady=10)

    def refresh_data(self):
        products = self.controller.db.get_products()
        product_names = []
        self.product_data = {}
        for prod_id, name, category, purchase_price, selling_price, stock, expiry_date in products:
            product_names.append(name)
            self.product_data[name] = {"id": prod_id, "purchase_price": purchase_price, "stock": stock}
        self.product_combobox['values'] = product_names
        self.product_combobox.set("")

        self.quantity_entry.delete(0, tk.END)
        self.cost_price_entry.delete(0, tk.END)
        self.supplier_name_entry.delete(0, tk.END)
        self.purchase_date_display.set(datetime.now().strftime("%Y-%m-%d"))

        for item in self.purchases_tree.get_children():
            self.purchases_tree.delete(item)
        purchases = self.controller.db.get_purchases_report()
        for purchase in purchases:
            formatted_purchase = list(purchase)
            formatted_purchase[2] = f"{purchase[2]:.2f}"
            self.purchases_tree.insert("", "end", values=formatted_purchase)
        self.filter_purchases()

    def on_product_select(self, event=None):
        selected_product_name = self.product_combobox.get()
        if selected_product_name in self.product_data:
            product_info = self.product_data[selected_product_name]
            self.cost_price_entry.delete(0, tk.END)
            self.cost_price_entry.insert(0, f"{product_info['purchase_price']:.2f}")
        else:
            self.cost_price_entry.delete(0, tk.END)

    def handle_purchase_action(self):
        if self.edit_mode:
            self.update_purchase()
        else:
            self.record_purchase()

    def record_purchase(self):
        selected_product_name = self.product_combobox.get()
        quantity_str = self.quantity_entry.get().strip()
        cost_price_str = self.cost_price_entry.get().strip()
        purchase_date = self.purchase_date_display.get().strip()
        supplier_name = self.supplier_name_entry.get().strip()

        if not selected_product_name or not quantity_str or not cost_price_str or not purchase_date:
            messagebox.showerror("Input Error", "Product, Quantity, Cost Price, and Purchase Date are required.")
            return

        if selected_product_name not in self.product_data:
            messagebox.showerror("Error", "Selected product is not valid.")
            return

        try:
            quantity = float(quantity_str)
            cost_price = float(cost_price_str)
            if quantity <= 0 or cost_price < 0:
                messagebox.showerror("Input Error", "Quantity must be positive and Cost Price non-negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number and Cost Price a number.")
            return

        product_info = self.product_data[selected_product_name]
        product_id = product_info["id"]

        if self.controller.db.record_purchase(product_id, quantity, cost_price, purchase_date, supplier_name):
            messagebox.showinfo("Success", f"Purchase of {quantity:.2f} x {selected_product_name} recorded.")
            self.reset_form()
            self.refresh_data()
            self.controller.frames["products"].refresh_data()
            self.controller.frames["reports"].refresh_data()

    def load_purchase_for_edit(self):
        selected_item = self.purchases_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a purchase to edit.")
            return

        purchase_id = self.purchases_tree.item(selected_item)['values'][0]
        purchase_data = self.controller.db.get_purchase_by_id(purchase_id)

        if purchase_data:
            self.edit_mode = True
            self.current_purchase_id = purchase_data[0]
            product_id_from_purchase = purchase_data[1]
            self.previous_purchase_quantity = purchase_data[2]

            product_info = self.controller.db.get_product_by_id(product_id_from_purchase)
            if product_info:
                product_name = product_info[1]
                self.product_combobox.set(product_name)

            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, f"{purchase_data[2]:.2f}")

            self.cost_price_entry.delete(0, tk.END)
            self.cost_price_entry.insert(0, f"{purchase_data[3]:.2f}")

            self.purchase_date_display.set(purchase_data[4])

            self.supplier_name_entry.delete(0, tk.END)
            self.supplier_name_entry.insert(0, purchase_data[5] if purchase_data[5] else "")

            self.action_button.config(text="Update Purchase")
            self.cancel_button.grid()
            self.input_frame.config(text=f"Edit Purchase (ID: {self.current_purchase_id})")

    def update_purchase(self):
        if not self.current_purchase_id:
            messagebox.showerror("Error", "No purchase selected for update.")
            return

        selected_product_name = self.product_combobox.get()
        new_quantity_str = self.quantity_entry.get().strip()
        new_cost_price_str = self.cost_price_entry.get().strip()
        new_purchase_date = self.purchase_date_display.get().strip()
        new_supplier_name = self.supplier_name_entry.get().strip()

        if not selected_product_name or not new_quantity_str or not new_cost_price_str or not new_purchase_date:
            messagebox.showerror("Input Error", "Product, Quantity, Cost Price, and Purchase Date are required.")
            return

        if selected_product_name not in self.product_data:
            messagebox.showerror("Error", "Selected product is not valid.")
            return

        try:
            new_quantity = float(new_quantity_str)
            new_cost_price = float(new_cost_price_str)
            if new_quantity <= 0 or new_cost_price < 0:
                messagebox.showerror("Input Error", "Quantity must be positive and Cost Price non-negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number and Cost Price a number.")
            return

        product_info = self.product_data[selected_product_name]
        product_id = product_info["id"]

        if self.controller.db.update_purchase(self.current_purchase_id, product_id, new_quantity, new_cost_price, new_purchase_date, new_supplier_name, self.previous_purchase_quantity):
            messagebox.showinfo("Success", f"Purchase (ID: {self.current_purchase_id}) updated successfully.")
            self.reset_form()
            self.refresh_data()
            self.controller.frames["products"].refresh_data()
            self.controller.frames["reports"].refresh_data()

    def delete_purchase(self):
        selected_item = self.purchases_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a purchase to delete.")
            return

        purchase_id = self.purchases_tree.item(selected_item)['values'][0]
        product_name = self.purchases_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete purchase for '{product_name}' (ID: {purchase_id})?"):
            if self.controller.db.delete_purchase(purchase_id):
                messagebox.showinfo("Success", f"Purchase (ID: {purchase_id}) for '{product_name}' deleted successfully.")
                self.refresh_data()
                self.reset_form()
                self.controller.frames["products"].refresh_data()
                self.controller.frames["reports"].refresh_data()

    def reset_form(self):
        self.edit_mode = False
        self.current_purchase_id = None
        self.previous_purchase_quantity = 0.0
        self.product_combobox.set("")
        self.quantity_entry.delete(0, tk.END)
        self.cost_price_entry.delete(0, tk.END)
        self.supplier_name_entry.delete(0, tk.END)
        self.purchase_date_display.set(datetime.now().strftime("%Y-%m-%d"))

        self.action_button.config(text="Add Purchase")
        self.cancel_button.grid_remove()
        self.input_frame.config(text="Add New Purchase")

    def filter_purchases(self, event=None):
        search_term = self.search_entry.get().lower()
        if search_term == "search purchases...":
            search_term = ""

        all_purchases = self.controller.db.get_purchases_report()

        for item in self.purchases_tree.get_children():
            self.purchases_tree.delete(item)

        filtered_purchases = [
            p for p in all_purchases
            if search_term in str(p[1]).lower() or
               search_term in str(p[5]).lower()
        ]

        for purchase in filtered_purchases:
            formatted_purchase = list(purchase)
            formatted_purchase[2] = f"{purchase[2]:.2f}"
            self.purchases_tree.insert("", "end", values=formatted_purchase)

    def clear_search_placeholder(self, event):
        if self.search_entry.get() == "Search purchases...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg='black')

    def restore_search_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search purchases...")
            self.search_entry.config(fg='grey')

    def show_context_menu(self, event):
        item_id = self.purchases_tree.identify_row(event.y)
        if item_id:
            self.purchases_tree.selection_set(item_id)
            self.purchases_tree.focus(item_id)
            self.context_menu.post(event.x_root, event.y_root)

class ReportsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.input_frame = tk.LabelFrame(self, text="Generate Monthly Profit Report", padx=10, pady=10)
        self.input_frame.pack(pady=10, fill="x")

        tk.Label(self.input_frame, text="Select Month:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.report_date_display = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.report_date_label = tk.Label(self.input_frame, textvariable=self.report_date_display, width=37, anchor="w", relief="sunken", bd=1)
        self.report_date_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.date_picker_button = ttk.Button(self.input_frame, text="Select Date", command=self.open_date_picker)
        self.date_picker_button.grid(row=0, column=2, padx=5, pady=5)

        generate_btn = ttk.Button(self.input_frame, text="Generate Report", command=self.generate_report)
        generate_btn.grid(row=1, column=0, columnspan=3, pady=10)

        reports_display_frame = tk.LabelFrame(self, text="Stored Monthly Reports", padx=10, pady=10)
        reports_display_frame.pack(pady=10, fill="both", expand=True)

        tree_frame = tk.Frame(reports_display_frame)
        tree_frame.pack(fill="both", expand=True)

        self.reports_tree = ttk.Treeview(tree_frame, columns=("ID", "Month", "Revenue", "Expenses", "Profit"), show="headings")
        self.reports_tree.heading("ID", text="ID")
        self.reports_tree.heading("Month", text="Month (YYYY-MM)")
        self.reports_tree.heading("Revenue", text="Total Revenue")
        self.reports_tree.heading("Expenses", text="Total Expenses")
        self.reports_tree.heading("Profit", text="Profit")

        self.reports_tree.column("ID", width=30, anchor="center")
        self.reports_tree.column("Month", width=100, anchor="center")
        self.reports_tree.column("Revenue", width=120, anchor="e")
        self.reports_tree.column("Expenses", width=120, anchor="e")
        self.reports_tree.column("Profit", width=120, anchor="e")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.reports_tree.yview)
        vsb.pack(side='right', fill='y')
        self.reports_tree.configure(yscrollcommand=vsb.set)

        self.reports_tree.pack(side='left', fill="both", expand=True)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete Report", command=self.delete_report)
        self.reports_tree.bind("<Button-3>", self.show_context_menu)

        self.refresh_data()

    def open_date_picker(self):
        def grab_date():
            selected_date = cal.selection_get()
            self.report_date_display.set(selected_date.strftime("%Y-%m-%d"))
            top.destroy()

        top = tk.Toplevel(self)
        top.title("Select Date for Report Month")
        top.grab_set()

        current_date_str = self.report_date_display.get()
        initial_date = datetime.now().date()
        if current_date_str:
            try:
                initial_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        cal = Calendar(top, selectmode='day',
                       year=initial_date.year,
                       month=initial_date.month,
                       day=initial_date.day)
        cal.pack(pady=20)

        confirm_button = ttk.Button(top, text="Select", command=grab_date)
        confirm_button.pack(pady=10)

    def generate_report(self):
        selected_date_str = self.report_date_display.get().strip()
        if not selected_date_str:
            messagebox.showerror("Input Error", "Please select a date to generate the report for its month.")
            return

        try:
            selected_date_obj = datetime.strptime(selected_date_str, "%Y-%m-%d")
            report_month = selected_date_obj.strftime("%Y-%m")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        total_revenue = self.controller.db.calculate_monthly_revenue(report_month)
        total_expenses = self.controller.db.calculate_monthly_expenses(report_month)
        profit = total_revenue - total_expenses

        if self.controller.db.save_or_update_report(report_month, total_revenue, total_expenses, profit):
            messagebox.showinfo("Success", f"Report for {report_month} generated/updated successfully.")
            self.refresh_data()
        else:
            messagebox.showerror("Error", "Failed to generate/update report.")

    def delete_report(self):
        selected_item = self.reports_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a report to delete.")
            return

        report_id = self.reports_tree.item(selected_item)['values'][0]
        report_month = self.reports_tree.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the report for '{report_month}'? This will NOT affect sales/purchases data."):
            if self.controller.db.delete_stored_report(report_id):
                messagebox.showinfo("Success", f"Report for '{report_month}' deleted successfully.")
                self.refresh_data()

    def refresh_data(self):
        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)

        reports = self.controller.db.get_stored_reports()
        for report in reports:
            formatted_report = (
                report[0],
                report[1],
                f"{report[2]:.2f}",
                f"{report[3]:.2f}",
                f"{report[4]:.2f}"
            )
            item_id = self.reports_tree.insert("", "end", values=formatted_report)
            profit_value = report[4]
            if profit_value < 0:
                self.reports_tree.tag_configure('negative_profit', foreground='red')
                self.reports_tree.item(item_id, tags=('negative_profit',))
            else:
                self.reports_tree.tag_configure('positive_profit', foreground='green')
                self.reports_tree.item(item_id, tags=('positive_profit',))


    def show_context_menu(self, event):
        item_id = self.reports_tree.identify_row(event.y)
        if item_id:
            self.reports_tree.selection_set(item_id)
            self.reports_tree.focus(item_id)
            self.context_menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
