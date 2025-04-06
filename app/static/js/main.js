document.addEventListener("DOMContentLoaded", function () {
  const reviewsWrapper = document.querySelector(".reviews-wrapper");
  const reviewsContent = document.querySelector(".reviews-content");
  const reviews = document.querySelectorAll(".single-testimonial-box");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  let currentIndex = 0;
  let reviewWidth = reviews[0].offsetWidth + 20; // 卡片宽度 + 间距
  let totalReviews = reviews.length;

  // 复制首尾的卡片，制造无缝循环
  const firstClone = reviews[0].cloneNode(true);
  const lastClone = reviews[totalReviews - 1].cloneNode(true);

  reviewsContent.appendChild(firstClone);
  reviewsContent.insertBefore(lastClone, reviews[0]);

  const allReviews = document.querySelectorAll(".single-testimonial-box"); // 包含克隆的卡片
  let newTotalReviews = allReviews.length;

  function updateActiveReview() {
    allReviews.forEach((review, index) => {
      review.classList.remove("active");
      review.style.opacity = "0.5";
      review.style.transform = "scale(0.9)";
    });

    allReviews[currentIndex].classList.add("active");
    allReviews[currentIndex].style.opacity = "1";
    allReviews[currentIndex].style.transform = "scale(1.1)";

    let translateX =
      -currentIndex * reviewWidth +
      reviewsWrapper.offsetWidth / 2 -
      reviewWidth / 2;
    reviewsContent.style.transition = "transform 0.5s ease-in-out";
    reviewsContent.style.transform = `translateX(${translateX}px)`;

    // 如果滑动到克隆的第一个或最后一个，瞬间跳转到原始位置
    setTimeout(() => {
      if (currentIndex === 0) {
        reviewsContent.style.transition = "none";
        currentIndex = totalReviews;
        let resetTranslateX =
          -currentIndex * reviewWidth +
          reviewsWrapper.offsetWidth / 2 -
          reviewWidth / 2;
        reviewsContent.style.transform = `translateX(${resetTranslateX}px)`;
      } else if (currentIndex === newTotalReviews - 1) {
        reviewsContent.style.transition = "none";
        currentIndex = totalReviews - 1;
        let resetTranslateX =
          -currentIndex * reviewWidth +
          reviewsWrapper.offsetWidth / 2 -
          reviewWidth / 2;
        reviewsContent.style.transform = `translateX(${resetTranslateX}px)`;
      }
    }, 500);
  }

  prevBtn.addEventListener("click", function () {
    currentIndex = (currentIndex - 1 + newTotalReviews) % newTotalReviews;
    updateActiveReview();
  });

  nextBtn.addEventListener("click", function () {
    currentIndex = (currentIndex + 1) % newTotalReviews;
    updateActiveReview();
  });

  // 初始状态调整
  currentIndex = totalReviews; // 从原始的第一个评论开始（跳过克隆）
  updateActiveReview();
});

// 点击下拉显示内容
const faqs = document.querySelectorAll(".faq");
faqs.forEach((faq) => {
  const button = faq.querySelector(".faq-question");

  button.addEventListener("click", () => {
    faq.classList.toggle("active");
  });
});
