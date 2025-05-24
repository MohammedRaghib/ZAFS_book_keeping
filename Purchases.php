<?php
include 'db.php';

$purchase_id = $_GET['edit_id'] ?? null;
$edit_mode = false;
$canProceed = true;

if (isset($_GET['delete_id'])) {
    $delete_id = $_GET['delete_id'];

    $stmt = $pdo->prepare("SELECT product_id, quantity FROM purchases WHERE id = ?");
    $stmt->execute([$delete_id]);
    $purchase = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($purchase) {
        $product_id = $purchase['product_id'];
        $quantity = $purchase['quantity'];

        $stmt = $pdo->prepare("SELECT stock_quantity FROM products WHERE id = ?");
        $stmt->execute([$product_id]);
        $product = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$product) {
            echo "<p class='message error'>Product not found.</p>";
        } elseif ($product['stock_quantity'] < $quantity) {
            echo "<p class='message error'>Cannot delete this purchase because stock would go negative.</p>";
        } else {
            $pdo->beginTransaction();
            try {
                $stmt = $pdo->prepare("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?");
                $stmt->execute([$quantity, $product_id]);

                $stmt = $pdo->prepare("DELETE FROM purchases WHERE id = ?");
                $stmt->execute([$delete_id]);

                $pdo->commit();
                echo "<p class='message success'>Purchase deleted successfully, and stock adjusted.</p>";
            } catch (Exception $e) {
                $pdo->rollBack();
                echo "<p class='message error'>Error: Could not delete purchase. {$e->getMessage()}</p>";
            }
        }
    } else {
        echo "<p class='message error'>Purchase not found.</p>";
    }
}


if ($purchase_id) {
    $stmt = $pdo->prepare("SELECT * FROM purchases WHERE id = ?");
    $stmt->execute([$purchase_id]);
    $purchase_data = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($purchase_data) {
        $edit_mode = true;
        $product_id = $purchase_data['product_id'];
        $quantity = $purchase_data['quantity'];
        $purchase_price = $purchase_data['purchase_price'];
        $date = $purchase_data['date'];
        $supplier_name = $purchase_data['supplier_name'];
    }
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['update_purchase'])) {
    $id = $_POST['id'];
    $product_id = $_POST['product_id'];
    $new_quantity = $_POST['quantity'];
    $purchase_price = $_POST['purchase_price'];
    $date = $_POST['date'];
    $supplier_name = $_POST['supplier_name'];

    $stmt = $pdo->prepare("SELECT quantity FROM purchases WHERE id = ?");
    $stmt->execute([$id]);
    $previous_purchase = $stmt->fetch(PDO::FETCH_ASSOC);
    $previous_quantity = $previous_purchase['quantity'] ?? 0;

    $stock_adjustment = $new_quantity - $previous_quantity;

    if ($stock_adjustment < 0) {
        $stmt = $pdo->prepare("SELECT stock_quantity FROM products WHERE id = ?");
        $stmt->execute([$product_id]);
        $product = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$product) {
            echo "<p class='message error'>Product not found.</p>";
            $canProceed = false;
        } elseif ($product['stock_quantity'] > $stock_adjustment) {
            echo "<p class='message error'>Not enough stock to deduct. Increase quantity.</p>";
            $canProceed = false;
        }
    }

    if ($canProceed) {
        $stmt = $pdo->prepare("UPDATE purchases SET product_id=?, quantity=?, purchase_price=?, date=?, supplier_name=? WHERE id=?");
        $stmt->execute([$product_id, $new_quantity, $purchase_price, $date, $supplier_name, $id]);

        $stmt = $pdo->prepare("UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?");
        $stmt->execute([$stock_adjustment, $product_id]);

        echo "<p class='message success'>Purchase updated successfully!</p>";
    }
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['add_purchase'])) {
    $product_id = $_POST['product_id'] ?? null;
    $quantity = $_POST['quantity'] ?? null;
    $purchase_price = $_POST['purchase_price'] ?? null;
    $date = $_POST['date'] ?? null;
    $supplier_name = $_POST['supplier_name'] ?? null;

    if (!$product_id || !$quantity || !$purchase_price || !$date) {
        echo "<p class='message error'>Please fill in all required fields.</p>";
        $canProceed = false;
    }

    if ($canProceed) {
        $stmt = $pdo->prepare("INSERT INTO purchases (product_id, quantity, purchase_price, date, supplier_name) VALUES (?, ?, ?, ?, ?)");
        $stmt->execute([$product_id, $quantity, $purchase_price, $date, $supplier_name]);

        echo "<p class='message success'>Purchase added successfully!</p>";
    }
}

$products = $pdo->query("SELECT id, name, purchase_price, stock_quantity FROM products")->fetchAll(PDO::FETCH_ASSOC);
$purchases = $pdo->query("SELECT purchases.id, products.name, purchases.quantity, purchases.purchase_price, purchases.date, purchases.supplier_name 
                          FROM purchases 
                          JOIN products ON purchases.product_id = products.id
                          ORDER BY purchases.date DESC")->fetchAll(PDO::FETCH_ASSOC);
?>


<!DOCTYPE html>
<html>

<head>
    <title>Purchase Management</title>
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

        /* Table Container */
        .table-container {
            background-color: var(--secondary-bg);
            padding: 15px;
            border-radius: 10px;
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

        /* Inputs & Select */
        input[type="text"],
        input[type="number"],
        input[type="date"],
        select {
            padding: 10px;
            border-radius: 5px;
            border: 1px solid var(--secondary-text);
            width: 90%;
            background-color: var(--secondary-bg);
            color: var(--secondary-text);
        }

        /* Button Styling */
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
            color: var(--secondary-bg);
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
            width: 90%;
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
        function filterPurchases() {
            let input = document.getElementById("searchBar").value.toLowerCase();
            let table = document.getElementById("purchaseTable");
            let rows = table.getElementsByTagName("tr");

            for (let i = 1; i < rows.length; i++) {
                let productCell = rows[i].getElementsByTagName("td")[1];
                if (productCell) {
                    let productValue = productCell.textContent || productCell.innerText;
                    rows[i].style.display = productValue.toLowerCase().includes(input) ? "" : "none";
                }
            }
        }

        function resetEverything() {
            document.getElementById("purchaseForm").reset();

            setTimeout(() => {
                let successMessage = document.querySelector(".message");
                if (successMessage) successMessage.style.display = "none";
            }, 2000);

            window.history.replaceState({}, document.title, window.location.pathname);
        }

        setTimeout(() => {
            resetEverything();
        }, 1000);

        function updatePrice() {
            const select = document.getElementById("productSelect");
            const selectedOption = select.options[select.selectedIndex];
            const price = selectedOption.getAttribute("data-price");
            document.querySelector('input[name="purchase_price"]').value = price;
        }
    </script>

</head>

<body>
    <?php include 'Nav.php'; ?>
    <main class="main-container">
        <div class="grid-container">
            <!-- Small Form -->
            <div class="form-container">
                <h2><?= $edit_mode ? "Edit Purchase" : "Add Purchase" ?></h2>
                <form id="purchaseForm" method="POST">
                    <input type="hidden" name="id" value="<?= $edit_mode ? $purchase_id : '' ?>">

                    <label>Product:</label>
                    <select name="product_id" id="productSelect" required onchange="updatePrice()">
                        <option value="">SELECT PRODUCT</option>
                        <?php foreach ($products as $product) { ?>
                            <option
                                value="<?= $product['id'] ?>"
                                data-price="<?= $product['purchase_price'] ?? 0 ?>"
                                <?= ($edit_mode && $product_id == $product['id']) ? 'selected' : '' ?>>
                                <?= $product['name'] ?> (Stock: <?= $product['stock_quantity'] ?>)
                            </option>
                        <?php } ?>
                    </select>

                    <label>Quantity:</label>
                    <input type="number" name="quantity" value="<?= $edit_mode ? $quantity : '' ?>" required>

                    <label>Purchase Price:</label>
                    <input type="number" name="purchase_price" value="<?= $edit_mode ? $purchase_price : '' ?>" required>

                    <label>Date:</label>
                    <input type="date" name="date" value="<?= $edit_mode ? $date : date('Y-m-d') ?>" required>

                    <label>Supplier Name:</label>
                    <input type="text" name="supplier_name" value="<?= $edit_mode ? $supplier_name : '' ?>">

                    <button type="submit" name="<?= $edit_mode ? 'update_purchase' : 'add_purchase' ?>">
                        <?= $edit_mode ? "Update Purchase" : "Add Purchase" ?>
                    </button>
                </form>
            </div>

            <!-- Purchase Table -->
            <div class="table-container">
                <h2>Purchase List</h2>

                <!-- Search Bar -->
                <input type="text" id="searchBar" placeholder="Search purchases..." onkeyup="filterPurchases()">

                <table id="purchaseTable">
                    <tr>
                        <th>ID</th>
                        <th>Product</th>
                        <th>Quantity</th>
                        <th>Purchase Price</th>
                        <th>Date</th>
                        <th>Supplier</th>
                        <th>Action</th>
                    </tr>
                    <?php foreach ($purchases as $purchase) { ?>
                        <tr>
                            <td><?= $purchase['id'] ?></td>
                            <td><?= $purchase['name'] ?></td>
                            <td><?= $purchase['quantity'] ?></td>
                            <td><?= $purchase['purchase_price'] ?></td>
                            <td><?= $purchase['date'] ?></td>
                            <td><?= $purchase['supplier_name'] ?></td>
                            <td>
                                <a href="?edit_id=<?= $purchase['id'] ?>">Edit</a> |
                                <a href="?delete_id=<?= $purchase['id'] ?>" onclick="return confirm('Are you sure?')" style="color:red;">Delete</a>
                            </td>
                        </tr>
                    <?php } ?>
                </table>
            </div>
        </div>
    </main>
</body>


</html>