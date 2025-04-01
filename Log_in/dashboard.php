<?php
// dashboard.php - The page users see after successful login

// Start session
session_start();

// Check if user is logged in
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    // Redirect to login page if not logged in
    header("Location: login_system.php");
    exit;
}

// Database connection information
$db_host = 'localhost';
$db_user = 'root';
$db_pass = 'grq990823';
$db_name = 'dublinbikesystem';

// Establish database connection
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if user is logged in
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    // Redirect to login page if not logged in
    header("Location: login_system.php");
    exit;
}

// Get user information from session
$user_id = $_SESSION['user_id'] ?? '';
$fullname = $_SESSION['fullname'] ?? '';
$email = $_SESSION['email'] ?? '';
$password = $_SESSION['password'] ?? '';
$time = $_SESSION['created_at'] ?? '';

// Handle form submissions for updates
$update_message = '';

if (isset($_POST['update_profile'])) {
    $field = $_POST['field'] ?? '';
    $new_value = $_POST['new_value'] ?? '';
    
    if (!empty($field) && !empty($new_value)) {
        // Validate and sanitize the input based on the field type
        if ($field === 'password') {
            // Hash the password for security
            $hashed_value = password_hash($new_value, PASSWORD_DEFAULT);
            $stmt = $conn->prepare("UPDATE users SET password=? WHERE id=?");
            $stmt->bind_param("si", $hashed_value, $user_id);
        } else if ($field === 'fullname') {
            $stmt = $conn->prepare("UPDATE users SET fullname=? WHERE id=?");
            $stmt->bind_param("si", $new_value, $user_id);
        } else if ($field === 'email') {
            // Validate email format
            if (!filter_var($new_value, FILTER_VALIDATE_EMAIL)) {
                $update_message = "Invalid email format!";
            } else {
                $stmt = $conn->prepare("UPDATE users SET email=? WHERE id=?");
                $stmt->bind_param("si", $new_value, $user_id);
            }
        }
        
        // Execute the update if no validation errors
        if (empty($update_message) && isset($stmt)) {
            if ($stmt->execute()) {
                // Update the session variable
                $_SESSION[$field] = $field === 'password' ? $new_value : $new_value;
                
                // Update local variables to reflect changes immediately
                if ($field === 'fullname') $fullname = $new_value;
                if ($field === 'email') $email = $new_value;
                if ($field === 'password') $password = $new_value;
                
                $update_message = ucfirst($field) . " updated successfully!";
            } else {
                $update_message = "Error updating " . $field . ": " . $conn->error;
            }
            $stmt->close();
        }
    }
}

// Handle logout
if (isset($_POST['logout'])) {
    // Destroy session
    session_unset();
    session_destroy();
    
    // Redirect to login page
    header("Location: log_in.html");
    exit;
}

// Close the database connection before HTML output
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Dublin Bikes</title>
    <style>
        /* Base styles */
        :root {
            --primary-color: #00594c;
            --text-color: #333333;
            --white: #ffffff;
            --light-bg: #f2f9f8;
            --font-family: -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        html {
            font-size: 16px;
        }
        
        body {
            background-color: var(--light-bg);
            font-family: var(--font-family);
            line-height: 1.5;
            color: var(--text-color);
        }
        
        /* Layout */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Header */
        header {
            background-color: var(--primary-color);
            color: var(--white);
            padding: 1rem 0;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            max-height: 40px;
        }
        
        .user-info {
            display: flex;
            align-items: center;
        }
        
        .user-name {
            margin-right: 1rem;
            font-weight: bold;
        }
        
        .logout-btn {
            background-color: transparent;
            border: 1px solid var(--white);
            color: var(--white);
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .logout-btn:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        /* Dashboard content */
        .dashboard {
            background-color: var(--white);
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin-top: 2rem;
        }
        
        .dashboard h1 {
            color: var(--primary-color);
            margin-bottom: 1.5rem;
            font-size: 24px;
        }
        
        .dashboard-section {
            margin-bottom: 2rem;
        }
        
        .dashboard-section h2 {
            font-size: 20px;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        
        .card {
            background-color: var(--light-bg);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
                
        .card h3 {
            margin-bottom: 0.5rem;
        }
        
        .card p {
            color: #666666;
        }
        
        .editable {
            cursor: pointer;
            padding: 2px 4px;
            border-radius: 3px;
            transition: background-color 0.2s;
        }
        
        .editable:hover {
            background-color: rgba(0, 89, 76, 0.1);
        }
        
        /* Modal styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        .modal-content {
            background-color: var(--white);
            margin: 15% auto;
            padding: 2rem;
            border-radius: 8px;
            width: 80%;
            max-width: 500px;
        }
        
        .modal-title {
            font-size: 20px;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
        }
        
        .form-group input {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .form-actions {
            display: flex;
            justify-content: space-between;
            margin-top: 1.5rem;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            color: var(--white);
            border: none;
        }
        
        .btn-cancel {
            background-color: transparent;
            color: #666;
            border: 1px solid #ddd;
        }
        
        .alert {
            padding: 0.75rem 1.25rem;
            margin-bottom: 1rem;
            border-radius: 4px;
        }
        
        .alert-success {
            background-color: #d4edda;
            color: #155724;
        }
        
        .alert-danger {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        @media screen and (max-width: 768px) {
            .header-content {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .user-info {
                margin-top: 1rem;
            }
            
            .cards {
                grid-template-columns: 1fr;
            }
            
            .modal-content {
                width: 90%;
                margin: 20% auto;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <img class="logo" src="/Log_in/bike-logo.png" alt="Dublin Bikes">
                <div class="user-info">
                    <span class="user-name">Welcome, <?php echo htmlspecialchars($fullname); ?></span>
                    <form method="POST">
                        <button type="submit" name="logout" class="logout-btn">Log Out</button>
                    </form>
                </div>
            </div>
        </div>
    </header>

    <div class="container">
        <?php if (!empty($update_message)): ?>
            <div class="alert <?php echo strpos($update_message, 'successfully') !== false ? 'alert-success' : 'alert-danger'; ?>">
                <?php echo htmlspecialchars($update_message); ?>
            </div>
        <?php endif; ?>
        
        <div class="dashboard">
            <h1>My Dublin Bikes Dashboard</h1>
            
            <div class="dashboard-section">
                <h2>Quick Access</h2>
                <div class="cards">
                    <div class="card">
                        <h3>Find a Bike</h3>
                        <p>Locate available bikes near you on the map</p>
                    </div>
                    <div class="card">
                        <h3>My Journeys</h3>
                        <p>View your recent journeys and statistics</p>
                    </div>
                    <div class="card">
                        <h3>Subscription Details</h3>
                        <p>Manage your subscription and payment details</p>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-section">
                <h2>Your Account</h2>
                <div class="cards">
                    <div class="card">
                        <h3>My Profile</h3>
                        <p>View and update your personal information</p>
                        <p><strong>Password:</strong> <span class="editable" data-field="password" onclick="openModal('password', '<?php echo htmlspecialchars($password); ?>')">••••••••</span></p>
                    </div>
                    <div class="card">
                        <h3>Account Information</h3>
                        <p><strong>Name:</strong> <span class="editable" data-field="fullname" onclick="openModal('fullname', '<?php echo htmlspecialchars($fullname); ?>')"><?php echo htmlspecialchars($fullname); ?></span></p>
                        <p><strong>Email:</strong> <span class="editable" data-field="email" onclick="openModal('email', '<?php echo htmlspecialchars($email); ?>')"><?php echo htmlspecialchars($email); ?></span></p>
                    </div>
                    <div class="card">
                        <h3>Membership Status</h3>
                        <p><strong>Status:</strong> Active</p>
                        <p><strong>Member Since:</strong> January 2025</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Edit Profile Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <div class="modal-title">Update Your Information</div>
            <form method="POST" action="">
                <input type="hidden" id="field" name="field" value="">
                <div class="form-group">
                    <label for="new_value" id="fieldLabel">New Value:</label>
                    <input type="text" id="new_value" name="new_value" required>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-cancel" onclick="closeModal()">Cancel</button>
                    <button type="submit" name="update_profile" class="btn btn-primary">Update</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        // Function to open the modal
        function openModal(field, currentValue) {
            document.getElementById('field').value = field;
            
            // Set appropriate label and input type
            const fieldLabel = document.getElementById('fieldLabel');
            const valueInput = document.getElementById('new_value');
            
            if (field === 'password') {
                fieldLabel.textContent = 'New Password:';
                valueInput.type = 'password';
                valueInput.value = '';
            } else if (field === 'fullname') {
                fieldLabel.textContent = 'New Name:';
                valueInput.type = 'text';
                valueInput.value = currentValue;
            } else if (field === 'email') {
                fieldLabel.textContent = 'New Email:';
                valueInput.type = 'email';
                valueInput.value = currentValue;
            }
            
            // Show the modal
            document.getElementById('editModal').style.display = 'block';
        }
        
        // Function to close the modal
        function closeModal() {
            document.getElementById('editModal').style.display = 'none';
        }
        
        // Close the modal if user clicks outside of it
        window.onclick = function(event) {
            const modal = document.getElementById('editModal');
            if (event.target === modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>