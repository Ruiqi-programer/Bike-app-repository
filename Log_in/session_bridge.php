<?php
// session_bridge.php - Passes information between HTML and PHP processor

// Start session
session_start();

// If there's an error message, add it to URL parameters
if (isset($_SESSION['error_message']) && !empty($_SESSION['error_message'])) {
    $error = urlencode($_SESSION['error_message']);
    unset($_SESSION['error_message']);
}

// If there's a success message, add it to URL parameters
if (isset($_SESSION['success']) && $_SESSION['success']) {
    $success = urlencode("Account created successfully! Redirecting to your account...");
    unset($_SESSION['success']);
}

// Get form data (if any)
$formData = '';
if (isset($_SESSION['form_data']) && !empty($_SESSION['form_data'])) {
    foreach ($_SESSION['form_data'] as $key => $value) {
        if (!empty($value)) {
            $formData .= "&" . $key . "=" . urlencode($value);
        }
    }
    unset($_SESSION['form_data']);
}

// Build redirect URL
$redirectUrl = "/Log_in/create_account.html";
$params = [];

if (isset($error)) {
    $params[] = "error=" . $error;
}

if (isset($success)) {
    $params[] = "success=" . $success;
}

if (!empty($formData)) {
    $params[] = substr($formData, 1); // Remove leading &
}

if (!empty($params)) {
    $redirectUrl .= "?" . implode("&", $params);
}

// Redirect back to HTML form page
header("Location: " . $redirectUrl);
exit();
?>
