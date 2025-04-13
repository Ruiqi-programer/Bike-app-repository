// Check the session store for error or success messages
document.addEventListener("DOMContentLoaded", function () {
  // Check for error or success messages in the URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const errorMessage = urlParams.get("error");
  const successMessage = urlParams.get("success");

  if (errorMessage) {
    const errorElement = document.getElementById("error-message");
    if (errorElement) {
      errorElement.textContent = decodeURIComponent(errorMessage);
      errorElement.classList.add("show");
    }
  }

  if (successMessage) {
    const successElement = document.getElementById("success-message");
    successElement.textContent = decodeURIComponent(successMessage);
    successElement.classList.add("show");
  }

  // Password visibility toggle
  const passwordInput = document.getElementById("password");
  const passwordToggle = document.getElementById("password-toggle");
  const showText = document.getElementById("show-password-text");
  const hideText = document.getElementById("hide-password-text");

  if (passwordToggle) {
    passwordToggle.addEventListener("click", function () {
      const type =
        passwordInput.getAttribute("type") === "password" ? "text" : "password";
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
});
// const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// fetch('/login', {
//   method: 'POST',
//   headers: {
//     'Content-Type': 'application/json',
//     'X-CSRFToken': csrfToken
//   },
//   body: JSON.stringify({ email, password })
// });