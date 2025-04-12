// Simple email validation
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(email).toLowerCase());
}

// Get DOM elements
const form = document.getElementById("resetForm");
const emailInput = document.getElementById("email");
const emailError = document.getElementById("emailError");
const submitButton = document.getElementById("submitButton");

// Form submission handling
form.addEventListener("submit", function (e) {
  // Reset previous error states
  emailInput.classList.remove("error");
  emailError.style.display = "none";

  // Validate email
  if (!validateEmail(emailInput.value.trim())) {
    e.preventDefault();
    emailInput.classList.add("error");
    emailError.style.display = "block";
    return false;
  }

  // Disable button to prevent multiple submissions
  submitButton.disabled = true;
  submitButton.textContent = "Processing...";
});

// Clear error state when typing
emailInput.addEventListener("input", function () {
  emailInput.classList.remove("error");
  emailError.style.display = "none";
});

// Back to sign in link
document.getElementById("backToSignIn").addEventListener("click", function (e) {
  e.preventDefault();
  // Check if the referrer contains the reset password path
  if (document.referrer.includes("/u/reset-password/")) {
    history.go(-3);
  } else {
    history.go(-1);
  }
});

// Auto-focus on email field
window.addEventListener("load", function () {
  emailInput.focus();
});
