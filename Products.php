<?php
include 'db.php';

$product_id = $_GET['edit_id'] ?? null;
$edit_mode = false;

if (isset($_GET['delete_id'])) {
    $delete_id = $_GET['delete_id'];
    $stmt = $pdo->prepare("DELETE FROM products WHERE id = ?");
    $stmt->execute([$delete_id]);

    echo "<p class='message success'>Product deleted successfully!</p>";
}


if ($product_id) {
    $stmt = $pdo->prepare("SELECT * FROM products WHERE id = ?");
    $stmt->execute([$product_id]);
    $product_data = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($product_data) {
        $edit_mode = true;
        $name = $product_data['name'];
        $category = $product_data['category'];
        $purchase_price = $product_data['purchase_price'];
        $selling_price = $product_data['selling_price'];
        $stock_quantity = $product_data['stock_quantity'];
        $expiry_date = $product_data['expiry_date'];
    }
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['update_product'])) {
    $id = $_POST['id'] ?? null;
    $name = $_POST['name'] ?? null;
    $category = $_POST['category'] ?? null;
    $purchase_price = $_POST['purchase_price'] ?? null;
    $selling_price = $_POST['selling_price'] ?? null;
    $stock_quantity = $_POST['stock_quantity'] ?? 0;
    $expiry_date = $_POST['expiry_date'] ?? null;

    if (!$id || !$name || !$category || !$purchase_price || !$selling_price) {
        echo "<p class='message error'>Please fill in all required fields.</p>";
        return;
    }

    $stmt = $pdo->prepare("UPDATE products SET name=?, category=?, purchase_price=?, selling_price=?, stock_quantity=?, expiry_date=? WHERE id=?");
    $stmt->execute([$name, $category, $purchase_price, $selling_price, $stock_quantity, $expiry_date, $id]);

    echo "<p class='message success'>Product updated successfully!</p>";
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['add_product'])) {
    $name = $_POST['name'] ?? null;
    $category = $_POST['category'] ?? null;
    $purchase_price = $_POST['purchase_price'] ?? null;
    $selling_price = $_POST['selling_price'] ?? null;
    $stock_quantity = $_POST['stock_quantity'] ?? 0;
    $expiry_date = $_POST['expiry_date'] ?? null;

    if (!$name || !$category || !$purchase_price || !$selling_price) {
        echo "<p class='message error'>Please fill in all required fields.</p>";
        return;
    }

    $stmt = $pdo->prepare("INSERT INTO products (name, category, purchase_price, selling_price, stock_quantity, expiry_date) VALUES (?, ?, ?, ?, ?, ?)");
    $stmt->execute([$name, $category, $purchase_price, $selling_price, $stock_quantity, $expiry_date]);

    echo "<p class='message success'>Product added successfully!</p>";
}

$products = $pdo->query("SELECT * FROM products ORDER BY name ASC")->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html>

<head>
    <title>Product Management</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="base.css">
    <style>
        /* Main Container */
        .main-container {
            max-width: 90%;
            margin: auto;
            padding: 20px;
            background-color: var(--secondary-bg);
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }

        /* Grid Layout */
        .grid-container {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
        }

        /* Form Container */
        .form-container {
            background-color: var(--secondary-bg);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.15);
        }

        /* Headings */
        h2 {
            text-align: center;
            color: var(--secondary-accent);
        }

        /* Form Styling */
        form {
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 100%;
        }

        /* Labels */
        label {
            font-weight: bold;
            color: var(--secondary-text);
        }

        /* Inputs */
        input[type="text"],
        input[type="number"],
        input[type="date"] {
            padding: 10px;
            border-radius: 5px;
            border: 1px solid var(--secondary-text);
            width: 90%;
            background-color: var(--secondary-bg);
            color: var(--secondary-text);
        }

        /* Button */
        button {
            padding: 12px 15px;
            border: none;
            background-color: var(--secondary-accent);
            color: var(--secondary-text);
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
            transition: background 0.3s ease-in-out;
            width: 100%;
        }

        button:hover {
            background-color: var(--secondary-text);
            color: var(--main-text);
        }

        /* Table Container */
        .table-container {
            width: 90%;
            background-color: var(--secondary-bg);
            padding: 15px;
            border-radius: 10px;
            max-height: 100vh;
        }

        /* Search Bar */
        #searchBar {
            width: 90%;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            border: 1px solid var(--secondary-text);
            background-color: var(--secondary-bg);
            color: var(--secondary-text);
        }

        /* Table Styling */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            overflow-x: auto;
            display: block;
        }

        /* Table Headers & Cells */
        th,
        td {
            padding: 12px;
            border: 1px solid var(--secondary-text);
            text-align: left;
        }

        /* Table Header */
        th {
            background-color: var(--secondary-accent);
            color: #000;
        }

        /* Table Data */
        td {
            background-color: var(--secondary-bg);
            color: var(--secondary-text);
        }

        /* Action Links */
        a {
            text-decoration: none;
            font-weight: bold;
            padding: 5px;
            color: var(--secondary-text);
        }

        a:hover {
            text-decoration: underline;
            color: var(--secondary-accent);
        }

        a[onclick] {
            color: red;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .grid-container {
                display: flex;
                flex-direction: column;
                align-items: center;
            }

            .form-container,
            .table-container {
                width: 100%;
                max-width: 95%;
            }

            table {
                font-size: 14px;
            }

            th,
            td {
                padding: 8px;
            }

            button {
                font-size: 14px;
                padding: 10px;
            }
        }
    </style>
    <script>
        function filterProducts() {
            let input = document.getElementById("searchBar").value.toLowerCase();
            let table = document.getElementById("productTable");
            let rows = table.getElementsByTagName("tr");

            for (let i = 1; i < rows.length; i++) {
                let nameCell = rows[i].getElementsByTagName("td")[1];
                if (nameCell) {
                    let nameValue = nameCell.textContent || nameCell.innerText;
                    rows[i].style.display = nameValue.toLowerCase().includes(input) ? "" : "none";
                }
            }
        }

        function resetEverything() {
            document.getElementById("productForm").reset();

            setTimeout(() => {
                let successMessage = document.querySelector(".message");
                if (successMessage) successMessage.style.display = "none";
            }, 2000);

            window.history.replaceState({}, document.title, window.location.pathname);
        }

        setTimeout(() => {
            resetEverything();
        }, 1000);
    </script>

</head>

<body>
    <?php include 'Nav.php'; ?>
    <main class="main-container">
        <div class="grid-container">
            <div class="form-container">
                <h2><?= $edit_mode ? "Edit Product" : "Add Product" ?></h2>
                <form id="productForm" method="POST">
                    <input type="hidden" name="id" value="<?= $edit_mode ? $product_id : '' ?>">

                    <label>Name:</label>
                    <input type="text" name="name" value="<?= $edit_mode ? $name : '' ?>" required>

                    <label>Category:</label>
                    <input type="text" name="category" value="<?= $edit_mode ? $category : '' ?>" required>

                    <label>Purchase Price:</label>
                    <input type="number" name="purchase_price" value="<?= $edit_mode ? $purchase_price : '' ?>" required>

                    <label>Selling Price:</label>
                    <input type="number" name="selling_price" value="<?= $edit_mode ? $selling_price : '' ?>" required>

                    <label>Stock Quantity:</label>
                    <input type="number" name="stock_quantity" value="<?= $edit_mode ? $stock_quantity : '' ?>">

                    <label>Expiry Date:</label>
                    <input type="date" name="expiry_date" value="<?= $edit_mode ? $expiry_date : '' ?>">

                    <button type="submit" name="<?= $edit_mode ? 'update_product' : 'add_product' ?>">
                        <?= $edit_mode ? "Update Product" : "Add Product" ?>
                    </button>
                </form>
            </div>

            <div class="table-container">
                <h2>Product List</h2>

                <input type="text" id="searchBar" placeholder="Search products..." onkeyup="filterProducts()">

                <table id="productTable">
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Purchase Price</th>
                        <th>Selling Price</th>
                        <th>Stock</th>
                        <th>Expiry Date</th>
                        <th>Action</th>
                    </tr>
                    <?php foreach ($products as $product) { ?>
                        <tr>
                            <td><?= $product['id'] ?></td>
                            <td><?= $product['name'] ?></td>
                            <td><?= $product['category'] ?></td>
                            <td><?= $product['purchase_price'] ?></td>
                            <td><?= $product['selling_price'] ?></td>
                            <td><?= $product['stock_quantity'] ?></td>
                            <td><?= $product['expiry_date'] ?></td>
                            <td>
                                <a href="?edit_id=<?= $product['id'] ?>">Edit</a> |
                                <a href="?delete_id=<?= $product['id'] ?>" onclick="return confirm('Are you sure?')" style="color:red;">Delete</a>
                            </td>
                        </tr>
                    <?php } ?>
                </table>
            </div>
        </div>
    </main>
</body>


</html>