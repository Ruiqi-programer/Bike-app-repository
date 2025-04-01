<?php
// register_handler.php - Handles registration form submission

// Start session to store error messages and form data
session_start();

// Database configuration
$db_host = "localhost";
$db_name = "dublinbikesystem";
$db_user = "root";
$db_pass = "grq990823"; 

// Create a database connection
try {
    $pdo = new PDO("mysql:host=$db_host;dbname=$db_name", $db_user, $db_pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    // Store error message in session
    $_SESSION['error_message'] = "Database connection failed: " . $e->getMessage();
    // Redirect back to the registration form
    header("Location: /Log_in/create_account.html");
    exit();
}

// Function to sanitize user input
function sanitize_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

// Function to validate password strength
function is_password_strong($password) {
    // At least 8 characters, including uppercase, lowercase letters, and numbers
    return (strlen($password) >= 8 &&
            preg_match('/[A-Z]/', $password) &&
            preg_match('/[a-z]/', $password) &&
            preg_match('/[0-9]/', $password));
}

// Only process POST requests
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Collect and sanitize form data
    $fullname = sanitize_input($_POST["fullname"]);
    $email = sanitize_input($_POST["email"]);
    $password = $_POST["password"];
    $confirm_password = $_POST["confirm-password"];
    $terms_accepted = isset($_POST["terms"]) ? 1 : 0;

    // Store form data in session (except password) for repopulating fields if validation fails
    $_SESSION['form_data'] = [
        'fullname' => $fullname,
        'email' => $email,
        'terms_accepted' => $terms_accepted
    ];

    $error_message = "";

    // Validate input data
    if (empty($fullname) || empty($email) || empty($password)) {
        $error_message = "All fields are required.";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error_message = "Invalid email format.";
    } elseif ($password !== $confirm_password) {
        $error_message = "Passwords do not match.";
    } elseif (!is_password_strong($password)) {
        $error_message = "Password must be at least 8 characters long and include uppercase letters, lowercase letters, and numbers.";
    } elseif (!$terms_accepted) {
        $error_message = "You must accept the terms and conditions.";
    } else {
        // Check if email is already registered
        $stmt = $pdo->prepare("SELECT id FROM users WHERE email = ?");
        $stmt->execute([$email]);

        if ($stmt->rowCount() > 0) {
            $error_message = "This email is already registered. Please log in or use a different email.";
        } else {
            // Encrypt password
            $hashed_password = password_hash($password, PASSWORD_DEFAULT);

            // Insert user data into the database
            try {
                $stmt = $pdo->prepare("INSERT INTO users (fullname, email, password, terms_accepted, created_at) 
                                      VALUES (?, ?, ?, ?, NOW())");
                $stmt->execute([$fullname, $email, $hashed_password, $terms_accepted]);

                // Registration successful
                $_SESSION['success'] = true;
                $_SESSION['user_id'] = $pdo->lastInsertId();
                $_SESSION['user_fullname'] = $fullname;

                // Clear form data
                unset($_SESSION['form_data']);

                // Redirect to account page or dashboard
                header("Location: /Log_in/account/dashboard.php");
                exit();
                
            } catch (PDOException $e) {
                $error_message = "Registration failed: " . $e->getMessage();
            }
        }
    }

    // If there's an error, store it in session and redirect back to the registration form
    if (!empty($error_message)) {
        $_SESSION['error_message'] = $error_message;
        header("Location: /Log_in/create_account.html");
        exit();
    }
} else {
    // If not a POST request, redirect to the registration page
    header("Location: /Log_in/create_account.html");
    exit();
}
?>
