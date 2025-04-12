// Check the session store for error or success messages
document.addEventListener("DOMContentLoaded", function () {
  // Check for error or success messages in the URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const errorMessage = urlParams.get("error");
  const successMessage = urlParams.get("success");

  if (errorMessage) {
    const errorElement = document.getElementById("error-message");
    errorElement.textContent = decodeURIComponent(errorMessage);
    errorElement.classList.add("show");
  }

  if (successMessage) {
    const successElement = document.getElementById("success-message");
    successElement.textContent = decodeURIComponent(successMessage);
    successElement.classList.add("show");
  }

  // Password toggle functionality
  function setupPasswordToggle(inputId, toggleId, showTextId, hideTextId) {
    const passwordInput = document.getElementById(inputId);
    const passwordToggle = document.getElementById(toggleId);
    const showText = document.getElementById(showTextId);
    const hideText = document.getElementById(hideTextId);

    if (passwordToggle) {
      passwordToggle.addEventListener("click", function () {
        const type =
          passwordInput.getAttribute("type") === "password"
            ? "text"
            : "password";
        passwordInput.setAttribute("type", type);

        // Toggle text visibility
        showText.classList.toggle("hide");
        hideText.classList.toggle("hide");

        // Update the aria-label
        passwordToggle.setAttribute(
          "aria-label",
          type === "password" ? "Show password" : "Hide password"
        );
      });
    }
  }

  // Setup password toggles
  setupPasswordToggle(
    "password",
    "password-toggle",
    "show-password-text",
    "hide-password-text"
  );
  setupPasswordToggle(
    "confirm-password",
    "confirm-password-toggle",
    "show-confirm-password-text",
    "hide-confirm-password-text"
  );

  // Password strength meter
  const passwordInput = document.getElementById("password");
  const strengthMeter = document.getElementById("password-strength-meter");

  passwordInput.addEventListener("input", function () {
    const password = this.value;
    let strength = 0;

    // Check for length
    if (password.length >= 8) strength += 1;

    // Check for mixed case
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength += 1;

    // Check for numbers
    if (password.match(/\d/)) strength += 1;

    // Check for special characters
    if (password.match(/[^a-zA-Z\d]/)) strength += 1;

    // Update the strength meter
    strengthMeter.className = "";
    if (password.length === 0) {
      strengthMeter.style.width = "0";
    } else if (strength < 2) {
      strengthMeter.classList.add("strength-weak");
    } else if (strength < 4) {
      strengthMeter.classList.add("strength-medium");
    } else {
      strengthMeter.classList.add("strength-strong");
    }
  });

  // Float labels when input has content (for when autofill happens)
  const inputs = document.querySelectorAll(".form-control");
  inputs.forEach((input) => {
    if (input.value) {
      input.classList.add("has-value");
    }

    input.addEventListener("input", function () {
      if (this.value) {
        this.classList.add("has-value");
      } else {
        this.classList.remove("has-value");
      }
    });
  });

  // Client form validation
  const form = document.querySelector(".signup-form");
  form.addEventListener("submit", function (event) {
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;
    const email = document.getElementById("email").value;
    const terms = document.querySelector('input[name="terms"]').checked;
    let valid = true;
    let errorMessage = "";

    // Verification mailbox format
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
      valid = false;
      errorMessage = "Please enter a valid email address";
    }

    // Verify password match
    if (password !== confirmPassword) {
      valid = false;
      errorMessage = "The two passwords do not match";
    }

    // Verify password strength
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const isLongEnough = password.length >= 8;

    if (!isLongEnough || !hasUpperCase || !hasLowerCase || !hasNumbers) {
      valid = false;
      errorMessage =
        "Passwords must be at least 8 characters long and contain uppercase letters, lowercase letters, and numbers";
    }

    // Acceptance of verification terms
    if (!terms) {
      valid = false;
      errorMessage = "You must agree to the terms and conditions";
    }

    // If the authentication fails, an error message is displayed
    if (!valid) {
      event.preventDefault();
      const errorElement = document.getElementById("error-message");
      errorElement.textContent = errorMessage;
      errorElement.classList.add("show");

      // Scroll to the error message
      errorElement.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});
