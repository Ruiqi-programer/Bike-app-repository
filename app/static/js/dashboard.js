// Check for URL parameters for error or success messages
document.addEventListener("DOMContentLoaded", function () {
  const urlParams = new URLSearchParams(window.location.search);
  const errorMessage = urlParams.get("error");
  const successMessage = urlParams.get("success");

  if (errorMessage) {
    const errorElement = document.getElementById("error-message");
    errorElement.textContent = decodeURIComponent(errorMessage);
    errorElement.style.display = "block";
  }

  if (successMessage) {
    const successElement = document.getElementById("success-message");
    successElement.textContent = decodeURIComponent(successMessage);
    successElement.style.display = "block";
  }
});

// Toggle edit forms
function toggleEditForm(formId) {
  const form = document.getElementById(formId);
  if (form.style.display === "block") {
    form.style.display = "none";
  } else {
    form.style.display = "block";
  }
}

// Validate password match
function validatePassword() {
  const passwordForm = document.getElementById("password-form");
  const newPassword = passwordForm.querySelector(
    'input[name="new_value"]'
  ).value;
  const confirmPassword = passwordForm.querySelector(
    'input[name="confirm_password"]'
  ).value;

  if (newPassword !== confirmPassword) {
    alert("Passwords do not match");
    return false;
  }

  const hasUpperCase = /[A-Z]/.test(newPassword);
  const hasLowerCase = /[a-z]/.test(newPassword);
  const hasNumbers = /\d/.test(newPassword);
  const isLongEnough = newPassword.length >= 8;

  if (!isLongEnough || !hasUpperCase || !hasLowerCase || !hasNumbers) {
    alert(
      "Password must be at least 8 characters long and include uppercase letters, lowercase letters, and numbers"
    );
    return false;
  }

  return true;
}
