<?php
session_start();

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    // Redirect to login page if not logged in
    header("Location: /Log_in/log_in.html");
    exit();
}

// Get user information
$user_fullname = $_SESSION['user_fullname'];
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Dashboard - Dublin Bike System</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <header>
        <img src="/Log_in/dublin-bike-logo.png" alt="Dublin Bike System Logo">
        <h1>Welcome to Your Dashboard</h1>
    </header>
    
    <main>
        <section class="dashboard-welcome">
            <h2>Hello, <?php echo htmlspecialchars($user_fullname); ?>!</h2>
            <p>Your account has been successfully created.</p>
        </section>
        
        <section class="dashboard-options">
            <h3>What would you like to do?</h3>
            <div class="options-grid">
                <a href="#" class="option-card">View Bike Stations</a>
                <a href="#" class="option-card">Rent a Bike</a>
                <a href="#" class="option-card">View Rental History</a>
                <a href="#" class="option-card">Manage Account</a>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2025 Dublin Bike System. All rights reserved.</p>
    </footer>
</body>
</html>