<?php
include 'db.php';

$sale_id = $_GET['edit_id'] ?? null;
$edit_mode = false;
$canProceed = true;

if (isset($_GET['delete_id'])) {
    $delete_id = $_GET['delete_id'];
    $stmt = $pdo->prepare("SELECT product_id, quantity FROM sales WHERE id = ?");
    $stmt->execute([$delete_id]);
    $deleted_sale = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($deleted_sale) {
        $stmt = $pdo->prepare("UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?");
        $stmt->execute([$deleted_sale['quantity'], $deleted_sale['product_id']]);

        $stmt = $pdo->prepare("DELETE FROM sales WHERE id = ?");
        $stmt->execute([$delete_id]);
    }

    echo "<p class='message success'>Sale deleted successfully!</p>";
}

if ($sale_id) {
    $stmt = $pdo->prepare("SELECT * FROM sales WHERE id = ?");
    $stmt->execute([$sale_id]);
    $sale_data = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($sale_data) {
        $edit_mode = true;
        $product_id = $sale_data['product_id'];
        $quantity = $sale_data['quantity'];
        $selling_price = $sale_data['selling_price'];
        $date = $sale_data['date'];
    }
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['update_sale'])) {
    $id = $_POST['id'];
    $product_id = $_POST['product_id'];
    $new_quantity = $_POST['quantity'];
    $selling_price = $_POST['selling_price'];
    $date = $_POST['date'];

    $stmt = $pdo->prepare("SELECT quantity FROM sales WHERE id = ?");
    $stmt->execute([$id]);
    $previous_sale = $stmt->fetch(PDO::FETCH_ASSOC);
    $previous_quantity = $previous_sale['quantity'] ?? 0;

    $stock_adjustment = $new_quantity - $previous_quantity;

    $stock_adjustment = $new_quantity - $previous_quantity;

    if ($stock_adjustment > 0) {
        $stmt = $pdo->prepare("SELECT stock_quantity FROM products WHERE id = ?");
        $stmt->execute([$product_id]);
        $product = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$product) {
            echo "<p class='message error'>Product not found.</p>";
            $canProceed = false;
        } elseif ($product['stock_quantity'] < $stock_adjustment) {
            echo "<p class='message error'>Not enough stock available to increase quantity.</p>";
            $canProceed = false;
        }
    }


    if ($canProceed) {
        $stmt = $pdo->prepare("UPDATE sales SET product_id=?, quantity=?, selling_price=?, date=? WHERE id=?");
        $stmt->execute([$product_id, $new_quantity, $selling_price, $date, $id]);

        if ($stock_adjustment !== 0) {
            $stmt = $pdo->prepare("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?");
            $stmt->execute([$stock_adjustment, $product_id]);
        }

        echo "<p class='message success'>Sale updated successfully!</p>";
    }
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['add_sale'])) {
    $product_id = $_POST['product_id'] ?? null;
    $quantity = $_POST['quantity'] ?? null;
    $selling_price = $_POST['selling_price'] ?? null;
    $date = $_POST['date'] ?? null;

    if (!$product_id || !$quantity || !$selling_price || !$date) {
        echo "<p class='message error'>Please fill in all required fields.</p>";
        $canProceed = false;
    }

    $stmt = $pdo->prepare("SELECT stock_quantity FROM products WHERE id = ?");
    $stmt->execute([$product_id]);
    $product = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$product) {
        echo "<p class='message error'>Product not found.</p>";
        $canProceed = false;
    } elseif ($product['stock_quantity'] < $quantity) {
        echo "<p class='message error'>Not enough stock available.</p>";
        $canProceed = false;
    }

    if ($canProceed) {
        $stmt = $pdo->prepare("INSERT INTO sales (product_id, quantity, selling_price, date) VALUES (?, ?, ?, ?)");
        $stmt->execute([$product_id, $quantity, $selling_price, $date]);

        $stmt = $pdo->prepare("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?");
        $stmt->execute([$quantity, $product_id]);

        echo "<p class='message success'>Sale added successfully!</p>";
    }
}

$products = $pdo->query("SELECT id, name, stock_quantity, selling_price FROM products")->fetchAll(PDO::FETCH_ASSOC);
$sales = $pdo->query("SELECT sales.id, products.name, sales.quantity, sales.selling_price, sales.date 
                      FROM sales 
                      JOIN products ON sales.product_id = products.id
                      ORDER BY sales.date DESC")->fetchAll(PDO::FETCH_ASSOC);
?>



<!DOCTYPE html>
<html>

<head>
    <title>Sales Management</title>
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
        function filterSales() {
            let input = document.getElementById("searchBar").value.toLowerCase();
            let table = document.getElementById("salesTable");
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
            document.getElementById("saleForm").reset();

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
            document.querySelector('input[name="selling_price"]').value = price;
        }
    </script>
</head>

<body>
    <?php include 'Nav.php'; ?>
    <main class="main-container">
        <div class="grid-container">
            <div class="form-container">
                <h2><?= $edit_mode ? "Edit Sale" : "Record a New Sale" ?></h2>
                <form method="POST" id="saleForm">
                    <input type="hidden" name="id" value="<?= $edit_mode ? $sale_id : '' ?>">

                    <label>Product:</label>
                    <select name="product_id" id="productSelect" required onchange="updatePrice()">
                        <option value="">SELECT PRODUCT</option>
                        <?php foreach ($products as $product) { ?>
                            <option
                                value="<?= $product['id'] ?>"
                                data-price="<?= $product['selling_price'] ?? 0 ?>"
                                <?= ($edit_mode && $product_id == $product['id']) ? 'selected' : '' ?>>
                                <?= $product['name'] ?> (Stock: <?= $product['stock_quantity'] ?>)
                            </option>
                        <?php } ?>
                    </select>


                    <label>Quantity:</label>
                    <input type="number" name="quantity" value="<?= $edit_mode ? $quantity : '' ?>" required>

                    <label>Selling Price:</label>
                    <input type="number" name="selling_price" value="<?= $edit_mode ? $selling_price : '' ?>" required>

                    <label>Date:</label>
                    <input type="date" name="date" value="<?= $edit_mode ? $date : date('Y-m-d') ?>">

                    <button type="submit" name="<?= $edit_mode ? 'update_sale' : 'add_sale' ?>">
                        <?= $edit_mode ? "Update Sale" : "Add Sale" ?>
                    </button>
                </form>
            </div>

            <div class="table-container">
                <h2>Sales Records</h2>

                <input type="text" id="searchBar" placeholder="Search sales records..." onkeyup="filterSales()">

                <table id="salesTable">
                    <tr>
                        <th>ID</th>
                        <th>Product Name</th>
                        <th>Quantity</th>
                        <th>Selling Price</th>
                        <th>Date</th>
                        <th>Action</th>
                    </tr>
                    <?php foreach ($sales as $sale) { ?>
                        <tr>
                            <td><?= $sale['id'] ?></td>
                            <td><?= $sale['name'] ?></td>
                            <td><?= $sale['quantity'] ?></td>
                            <td><?= $sale['selling_price'] ?></td>
                            <td><?= $sale['date'] ?></td>
                            <td>
                                <a href="?edit_id=<?= $sale['id'] ?>">Edit</a> |
                                <a href="?delete_id=<?= $sale['id'] ?>" onclick="return confirm('Are you sure?')" style="color:red;">Delete</a>
                            </td>
                        </tr>
                    <?php } ?>
                </table>
            </div>
        </div>
    </main>
</body>

</html>