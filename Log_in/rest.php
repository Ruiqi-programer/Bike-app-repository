<?php

// Enable full error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Configure file logging
ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/email_debug.log');

// Include PHPMailer library
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'Exception.php';
require 'PHPMailer.php';
require 'SMTP.php';

// Database configuration
$db_host = 'localhost';
$db_user = 'root';
$db_pass = 'grq990823';
$db_name = 'dublinbikesystem';

// Start session
session_start();

function sendPasswordResetEmail($to_email, $username, $password) {
    $mail = new PHPMailer(true);

    try {
        // SMTP Configuration
        $mail->isSMTP();
        $mail->Host       = 'smtp.gmail.com';
        $mail->SMTPAuth   = true;
        $mail->Username   = 'ruiqiguo0@gmail.com'; // Your Gmail account
        $mail->Password   = 'glkh pchb zhxm qpjj';
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port       = 587;

        // Sender and recipient
        $mail->setFrom('support@dublinbikes.com', 'Dublin Bikes Support');
        $mail->addAddress($to_email, $username);

        // Email content
        $mail->isHTML(true);
        $mail->Subject = 'Dublin Bikes - Password Recovery';
        $mail->Body    = "
            <html>
            <body>
                <h2>Password Recovery</h2>
                <p>Dear {$username},</p>
                <p>You have requested to recover your password. Here are your account details:</p>
                <p><strong>Email:</strong> {$to_email}</p>
                <p><strong>Password:</strong> {$password}</p>
                <p>Please log in and change your password immediately.</p>
                <p>Best regards,<br>Dublin Bikes Support Team</p>
            </body>
            </html>
        ";

        // Send email
        $mail->send();
        return true;
    } catch (Exception $e) {
        // Log error
        error_log("Message could not be sent. Mailer Error: {$mail->ErrorInfo}");
        return false;
    }
}

// Handle password reset request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get and validate email
    $email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
    
    // Validate email format
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $_SESSION['error_message'] = 'Invalid email address.';
        header("Location: reset_password.html");
        exit;
    }
    
    try {
        // Connect to database
        $pdo = new PDO("mysql:host=$db_host;dbname=$db_name", $db_user, $db_pass);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Prepare query
        $stmt = $pdo->prepare("SELECT fullname, email, password FROM users WHERE email = ?");
        $stmt->execute([$email]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($user) {
            // User exists, send password reset email
            $password_reset_success = sendPasswordResetEmail(
                $user['email'], 
                $user['fullname'], 
                $user['password']
            );
            
            if ($password_reset_success) {
                // Password reset email sent successfully
                $_SESSION['success_message'] = 'Password reset information has been sent to your email. Please check your inbox.';
                header("Location: log_in.html");
                exit;
            } else {
                // Email sending failed
                $_SESSION['error_message'] = 'Error sending password reset email. Please try again later.';
                header("Location: reset_password.html");
                exit;
            }
        } else {
            // User does not exist, redirect to sign-up page
            $_SESSION['error_message'] = 'This email is not registered. Please create a new account.';
            header("Location: create_account.html");
            exit;
        }
    } catch (PDOException $e) {
        // Handle database error
        $_SESSION['error_message'] = 'Database error: ' . $e->getMessage();
        header("Location: reset_password.html");
        exit;
    }
} else {
    // If not a POST request, redirect to password reset page
    header("Location: reset_password.html");
    exit;
}
?>
