document.addEventListener("DOMContentLoaded", function () {
  const reviewsWrapper = document.querySelector(".reviews-wrapper");
  const reviewsContent = document.querySelector(".reviews-content");
  const originalReviews = document.querySelectorAll(".single-testimonial-box");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  const reviewWidth = originalReviews[0].offsetWidth + 20;
  const totalOriginal = originalReviews.length;

  // Clone the first and last reviews to create seamless looping
  const firstClone = originalReviews[0].cloneNode(true);
  const lastClone = originalReviews[totalOriginal - 1].cloneNode(true);

  reviewsContent.appendChild(firstClone);
  reviewsContent.insertBefore(lastClone, originalReviews[0]);

  const allReviews = document.querySelectorAll(".single-testimonial-box");
  let currentIndex = 1;

  // Center the active review card
  function centerCurrentReview(animate = true) {
    allReviews.forEach((card) => {
      card.style.opacity = "0.5";
      card.style.transform = "scale(0.9)";
    });

    allReviews[currentIndex].style.opacity = "1";
    allReviews[currentIndex].style.transform = "scale(1.1)";

    const shift =
      -currentIndex * reviewWidth +
      reviewsWrapper.offsetWidth / 2 -
      reviewWidth / 2;
    reviewsContent.style.transition = animate ? "transform 0.4s ease" : "none";
    reviewsContent.style.transform = `translateX(${shift}px)`;
  }

  // Handle instant jump after reaching clone card (for infinite loop effect)
  function handleTransitionEnd() {
    if (currentIndex === 0) {
      currentIndex = totalOriginal;
      centerCurrentReview(false);
    } else if (currentIndex === allReviews.length - 1) {
      currentIndex = 1;
      centerCurrentReview(false);
    }
  }

  reviewsContent.addEventListener("transitionend", handleTransitionEnd);

  // Navigation button click handlers
  prevBtn.addEventListener("click", () => {
    if (currentIndex <= 0) return;
    currentIndex--;
    centerCurrentReview();
  });

  nextBtn.addEventListener("click", () => {
    if (currentIndex >= allReviews.length - 1) return;
    currentIndex++;
    centerCurrentReview();
  });

  // Initial load
  centerCurrentReview(false);
});

// Toggle FAQ content
const faqs = document.querySelectorAll(".faq");
faqs.forEach((faq) => {
  const button = faq.querySelector(".faq-question");

  button.addEventListener("click", () => {
    faq.classList.toggle("active");
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const backToTop = document.querySelector(".back-to-top");

  window.addEventListener("scroll", () => {
    if (window.scrollY > 100) {
      backToTop.classList.add("show");
    } else {
      backToTop.classList.remove("show");
    }
  });

  backToTop.addEventListener("click", (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
});
