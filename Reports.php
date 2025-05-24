<?php
include 'db.php';

$selected_date = $_POST['selected_date'] ?? date('Y-m-d');
$selected_month = date('Y-m', strtotime($selected_date));

$total_revenue = 0;
$total_expenses = 0;
$profit = 0;

if (isset($_GET['delete_month'])) {
    $month_to_delete = $_GET['delete_month'];

    $stmt = $pdo->prepare("DELETE FROM reports WHERE month = ?");
    $stmt->execute([$month_to_delete]);

    echo "<p class='message'>Report for {$month_to_delete} deleted successfully!</p>";
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['generate_report'])) {
    $sales_query = "SELECT SUM(quantity * selling_price) AS total_revenue FROM sales WHERE DATE_FORMAT(date, '%Y-%m') = ?";
    $stmt = $pdo->prepare($sales_query);
    $stmt->execute([$selected_month]);
    $total_revenue = $stmt->fetchColumn() ?? 0;

    $purchases_query = "SELECT SUM(quantity * purchase_price) AS total_expenses FROM purchases WHERE DATE_FORMAT(date, '%Y-%m') = ?";
    $stmt = $pdo->prepare($purchases_query);
    $stmt->execute([$selected_month]);
    $total_expenses = $stmt->fetchColumn() ?? 0;

    $profit = $total_revenue - $total_expenses;

    $stmt = $pdo->prepare("INSERT INTO reports (month, total_revenue, total_expenses, profit) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE total_revenue=?, total_expenses=?, profit=?");
    $stmt->execute([$selected_month, $total_revenue, $total_expenses, $profit, $total_revenue, $total_expenses, $profit]);
}

$reports = $pdo->query("SELECT * FROM reports ORDER BY month DESC")->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html>

<head>
    <title>Monthly Profit Report</title>
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

        /* Headings */
        h2 {
            color: var(--secondary-accent);
            margin-bottom: 15px;
        }

        /* Form Styling */
        form {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
            padding: 20px;
            background-color: var(--secondary-bg);
            border-radius: 10px;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.15);
        }

        /* Labels */
        label {
            font-weight: bold;
            color: var(--secondary-text);
        }

        /* Input */
        input[type="date"] {
            padding: 10px;
            border-radius: 5px;
            border: 1px solid var(--secondary-text);
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
        }

        button:hover {
            background-color: var(--secondary-text);
            color: var(--secondary-bg);
        }

        /* Table Styling */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: var(--secondary-bg);
            border-radius: 10px;
            overflow: hidden;
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

        /* Profit Styling */
        td.profit {
            font-weight: bold;
        }

        /* Negative Profit Styling */
        td.profit.negative {
            color: red;
        }

        /* Positive Profit Styling */
        td.profit.positive {
            color: green;
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
            .main-container {
                width: 95%;
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
        function resetEverything() {
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
        <h2>Generate Monthly Profit Report</h2>
        <form method="POST">
            <label>Select Date:</label>
            <input type="date" name="selected_date" value="<?= $selected_date ?>">
            <button type="submit" name="generate_report">Generate Report</button>
        </form>

        <h2>Stored Reports</h2>
        <table border="1">
            <tr>
                <th>Month</th>
                <th>Total Revenue</th>
                <th>Total Expenses</th>
                <th>Profit</th>
                <th>Action</th>
            </tr>
            <?php foreach ($reports as $report) { ?>
                <tr>
                    <td><?= $report['month'] ?></td>
                    <td><?= number_format($report['total_revenue'], 2) ?></td>
                    <td><?= number_format($report['total_expenses'], 2) ?></td>
                    <td style="color: <?= $report['profit'] < 0 ? 'red' : 'green' ?>;">
                        <?= number_format($report['profit'], 2) ?>
                    </td>
                    <td>
                        <a href="?delete_month=<?= $report['month'] ?>" onclick="return confirm('Are you sure you want to delete this report?')">Delete</a>
                    </td>
                </tr>
            <?php } ?>
        </table>
    </main>
</body>

</html>