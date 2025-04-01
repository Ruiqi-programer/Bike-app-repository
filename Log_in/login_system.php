<?php
// Enable error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Define the log file path (relative to the script)
$log_file = __DIR__ . '/login_debug.log';

// Function to write logs
function write_debug_log($message) {
    global $log_file;
    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[$timestamp] $message\n";
    file_put_contents($log_file, $log_entry, FILE_APPEND);
}

// Database configuration
$db_host = 'localhost';
$db_user = 'root';
$db_pass = 'grq990823';
$db_name = 'dublinbikesystem';

// Start session
session_start();

// Initialize error message and email variable
$error_message = '';
$email_prefilled = '';

// Handle login form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Write debug info
    write_debug_log("Login attempt started");
    write_debug_log("POST Data: " . print_r($_POST, true));

    // Get user input
    $email = filter_var($_POST['username'], FILTER_SANITIZE_EMAIL);
    $password = $_POST['password'] ?? '';

    // Store attempted email for pre-filling later
    $email_prefilled = $email;

    // Validate input
    if (empty($email) || empty($password)) {
        $error_message = 'Please enter both email and password.';
        write_debug_log("Empty input error");
    } else {
        try {
            // Connect to the database using PDO
            $pdo = new PDO("mysql:host=$db_host;dbname=$db_name", $db_user, $db_pass);
            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

            write_debug_log("Database connection successful");

            // Prepare SQL query to prevent SQL injection
            $stmt = $pdo->prepare("SELECT id, fullname, email, password, status FROM users WHERE email = ?");
            $stmt->execute([$email]);
            $user = $stmt->fetch(PDO::FETCH_ASSOC);

            write_debug_log("Query result: " . ($user ? "User found" : "No user found"));

            if ($user) {
                // Check account status
                if ($user['status'] !== 'active') {
                    $error_message = 'This account is not active. Please contact support.';
                    write_debug_log("Inactive account: " . $email);
                } 
                // Verify password
                elseif (password_verify($password, $user['password'])) {
                    // Password is correct - Set session variables
                    $_SESSION['user_id'] = $user['id'];
                    $_SESSION['fullname'] = $user['fullname'];
                    $_SESSION['email'] = $user['email'];
                    $_SESSION['password'] = $password;
                    $_SESSION['logged_in'] = true;

                    write_debug_log("Login successful for: " . $email);

                    // Update last login timestamp
                    $update_stmt = $pdo->prepare("UPDATE users SET last_login = NOW() WHERE id = ?");
                    $update_stmt->execute([$user['id']]);

                    // Redirect to dashboard
                    write_debug_log("Attempting to redirect to dashboard");

                    // Try multiple redirect paths
                    $dashboard_paths = [
                        '/Log_in/dashboard.php',
                        'dashboard.php',
                        $_SERVER['DOCUMENT_ROOT'] . '/Log_in/dashboard.php'
                    ];

                    foreach ($dashboard_paths as $path) {
                        write_debug_log("Trying path: " . $path);
                        if (file_exists($path)) {
                            write_debug_log("Path exists: " . $path);
                        }
                    }

                    header("Location: /Log_in/dashboard.php");
                    exit;
                } else {
                    $error_message = 'Invalid email or password. Please try again.';
                    write_debug_log("Password verification failed for: " . $email);
                }
            } else {
                $error_message = 'Invalid email or password. Please try again.';
                write_debug_log("No user found with email: " . $email);
            }

        } catch (PDOException $e) {
            // Log errors
            write_debug_log('Login Error: ' . $e->getMessage());
            $error_message = 'An unexpected error occurred. Please try again later.';
        }
    }
}

// Output log file contents (for debugging only)
$debug_log_contents = file_exists($log_file) ? file_get_contents($log_file) : "Log file not found";
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My Account - Dublin Bikes</title>
    <style>
        :root {
            --primary-color: #00594c;
            --text-color: #333333;
            --error-color: #D00E17;
            --white: #ffffff;
            --light-bg: #f2f9f8;
            --font-family: -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif;
        }
        
        /* Add existing styles here */
        
        .debug-log {
            margin-top: 20px;
            background-color: #f4f4f4;
            border: 1px solid #ddd;
            padding: 10px;
            font-family: monospace;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-header">
            <h1 class="login-title">My Account</h1>
            <p class="login-subtitle">Sign in to your account for the best experience</p>
        </div>
        
        <?php if (!empty($error_message)): ?>
            <div class="error-message">
                <?php echo htmlspecialchars($error_message); ?>
            </div>
        <?php endif; ?>
        
        <form method="POST" action="">
            <div class="form-group">
                <input type="email" name="username" class="form-control" 
                       placeholder="Email address" 
                       value="<?php echo htmlspecialchars($email_prefilled); ?>" 
                       required 
                       autocomplete="email">
            </div>
            <div class="form-group">
                <input type="password" name="password" class="form-control" 
                       placeholder="Password" 
                       required 
                       autocomplete="current-password">
            </div>
            
            <div class="forgot-password">
                <a href="/Log_in/reset_password.php">Forgot password?</a>
            </div>
            
            <button type="submit" class="btn">Sign In</button>
        </form>
        
        <div class="signup-section">
            <p>Don't have an account yet?</p>
            <a href="/Log_in/create_account.html" class="signup-link">Sign up</a> today for faster checkout, easy order tracking & exclusive rewards
        </div>

        <!-- Debug Log Section -->
        <div class="debug-log">
            <h3>Debug Log:</h3>
            <?php echo htmlspecialchars($debug_log_contents); ?>
        </div>
    </div>

    <script>
        // Toggle password visibility
        document.addEventListener('DOMContentLoaded', function() {
            const passwordInput = document.querySelector('input[name="password"]');
            const showPasswordLink = document.createElement('span');
            showPasswordLink.textContent = 'Show';
            showPasswordLink.style.position = 'absolute';
            showPasswordLink.style.right = '10px';
            showPasswordLink.style.cursor = 'pointer';
            
            const passwordContainer = passwordInput.parentNode;
            passwordContainer.style.position = 'relative';
            passwordContainer.appendChild(showPasswordLink);

            showPasswordLink.addEventListener('click', function() {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    showPasswordLink.textContent = 'Hide';
                } else {
                    passwordInput.type = 'password';
                    showPasswordLink.textContent = 'Show';
                }
            });
        });
    </script>
</body>
</html>
