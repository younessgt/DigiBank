"use strict";

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.querySelector(".modal");
  const modal2 = document.querySelector(".modal2");
  const modal3 = document.querySelector(".modal3");
  const modal4 = document.querySelector(".modal4");

  const overlay = document.querySelector(".overlay");
  const btnCloseModal = document.querySelector(".btn--close-modal");
  const btnCloseModal2 = document.querySelector(".btn--close-modal2");
  const btnCloseModal3 = document.querySelector(".btn--close-modal3");
  const btnCloseModal4 = document.querySelector(".btn--close-modal4");

  const btnsOpenModal = document.querySelectorAll(".btn--show-modal");
  const btnsOpenModal2 = document.querySelectorAll(".btn--show-modal2");

  const btnLearnMore = document.querySelector(".btn--scroll-to");
  const section1 = document.querySelector("#section--1");

  const servicesBtn = document.querySelectorAll(".services__tab");
  const servicesContent = document.querySelectorAll(".services__content");
  const servicesBtnContainer = document.querySelector(
    ".services__tab-container"
  );

  const header = document.querySelector(".header");

  const rightBtnSlide = document.querySelector(".slider__btn--right");

  const leftBtnSlide = document.querySelector(".slider__btn--left");

  const inputs = document.querySelectorAll(".code"),
    verifyCodeButton = document.querySelector(".verify_code");

  let combinedNumber = "";

  const verificationMsg = document.getElementById("verification-msg");

  // open modal function
  const openModal = function (e) {
    e.preventDefault();
    modal.classList.remove("hidden");
    overlay.classList.remove("hidden");
  };

  // close modal function (sign up )
  const closeModal = function () {
    modal.classList.add("hidden");
    overlay.classList.add("hidden");
  };

  const openModal2 = function (e) {
    e.preventDefault();
    modal2.classList.remove("hidden");
    overlay.classList.remove("hidden");
  };

  const openModal4 = function () {
    modal4.classList.remove("hidden");
    overlay.classList.remove("hidden");
  };

  // close modal function (login)
  const closeModal2 = function () {
    modal2.classList.add("hidden");
    overlay.classList.add("hidden");
  };

  const closeModal3 = function () {
    modal3.classList.add("hidden");
    overlay.classList.add("hidden");
  };

  const closeModal4 = function () {
    modal4.classList.add("hidden");
    overlay.classList.add("hidden");
  };

  btnsOpenModal.forEach((btn) => btn.addEventListener("click", openModal));
  btnsOpenModal2.forEach((btn) => btn.addEventListener("click", openModal2));

  // handling close modal
  btnCloseModal.addEventListener("click", closeModal);
  btnCloseModal2.addEventListener("click", closeModal2);
  btnCloseModal3.addEventListener("click", closeModal3);
  btnCloseModal4.addEventListener("click", closeModal4);

  overlay.addEventListener("click", closeModal);
  overlay.addEventListener("click", closeModal2);
  overlay.addEventListener("click", closeModal4);

  // handle escape btn to close the model
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !modal2.classList.contains("hidden")) {
      closeModal();
    }
  });

  // scrolling
  btnLearnMore.addEventListener("click", function () {
    section1.scrollIntoView({ behavior: "smooth" });
  });

  // smooth scrolling for the features
  // using event delegation

  document.querySelector(".nav__links").addEventListener("click", function (e) {
    e.preventDefault();
    // console.log(e.target);
    // console.log(e.currentTarget);

    if (e.target.classList.contains("nav__link")) {
      const id = e.target.getAttribute("href");

      // prevent the login and sign up buttons by checking id !== '#'
      if (id !== "#") {
        document.querySelector(id).scrollIntoView({
          behavior: "smooth",
        });
      }
    }
  });

  // service part

  // event delegation
  servicesBtnContainer.addEventListener("click", function (e) {
    if (!e.target.classList.contains("services__tab-container")) {
      // prevent span element  inside the button from been the target
      const clikedBtn = e.target.closest(".services__tab");

      // remove from all btns the class : services__tab--active to prevent the transform

      servicesBtn.forEach((btn) => {
        btn.classList.remove("services__tab--active");
      });

      // transform activated
      clikedBtn.classList.add("services__tab--active");

      // activating the content of the clicked btn

      const btnNumber = clikedBtn.dataset.tab;

      servicesContent.forEach((content) => {
        content.classList.remove("services__content--active");
      });

      const currentContent = document.querySelector(
        `.services__content--${btnNumber}`
      );

      currentContent.classList.add("services__content--active");
    }
  });

  // animate the menu

  const nav = document.querySelector(".nav");
  // console.log(nav);

  const hoverMenu = function (e) {
    if (e.target.classList.contains("nav__link")) {
      const siblings = e.target.closest(".nav").querySelectorAll(".nav__link");

      siblings.forEach((element) => {
        if (element !== e.target) {
          element.style.opacity = this;
        }
      });
    }
  };

  nav.addEventListener("mouseover", hoverMenu.bind(0.5));

  nav.addEventListener("mouseout", hoverMenu.bind(1));

  // fixing nav when  scrolling on a precise position

  // method intersection Observer API

  const obsCallback = function (entries, observer) {
    const [entry] = entries;
    // console.log(entry);
    if (!entry.isIntersecting) {
      nav.classList.add("fixnav");
    } else {
      nav.classList.remove("fixnav");
    }
  };

  const objOptions = {
    root: null,
    threshold: 0,
    rootMargin: `-${nav.getBoundingClientRect().height}px`,
  };

  const headerObserver = new IntersectionObserver(obsCallback, objOptions);

  headerObserver.observe(header);

  // section animation

  const An = ScrollReveal({
    distance: "70px",
    duration: 2000,
    delay: 400,
    reset: true,
  });

  An.reveal(".header__title", { delay: 300, origin: "left" });

  An.reveal(".header__title h4", { delay: 300, origin: "left" });
  An.reveal(".header__title .btn--text", { delay: 300, origin: "left" });
  An.reveal(".section", { delay: 400, origin: "bottom" });

  // load images

  const allLazyImages = document.querySelectorAll("img[data-src]");

  const imageCallback = function (entries, observer) {
    const [entry] = entries;

    // console.log(entry);
    if (!entry.isIntersecting) return;

    // replacing the low quality image with the good one
    entry.target.src = entry.target.dataset.src;

    // making sure that the new image is full loaded

    entry.target.addEventListener("load", function () {
      entry.target.classList.remove("lazy-img");
    });

    observer.unobserve(entry.target);
  };
  const imageObserver = new IntersectionObserver(imageCallback, {
    root: null,
    threshold: 0,
    rootMargin: "300px",
  });

  allLazyImages.forEach((img) => imageObserver.observe(img));

  // slide part

  const allSlides = document.querySelectorAll(".slide");

  let currentSlide = 0;

  const switchSlide = function (currSlide) {
    allSlides.forEach((slide, i) => {
      slide.style.transform = `translateX(${100 * (i - currentSlide)}%)`;
    });
  };

  switchSlide(0);

  setTimeout(() => {
    allSlides.forEach((slide) => {
      if (slide.classList.contains("slide--hidden")) {
        slide.classList.remove("slide--hidden");
      }
    });
  }, 5);

  rightBtnSlide.addEventListener("click", function () {
    if (currentSlide === allSlides.length - 1) {
      return;
    } else {
      currentSlide++;
    }
    switchSlide(currentSlide);
  });

  leftBtnSlide.addEventListener("click", function () {
    if (currentSlide === 0) {
      return;
    } else {
      currentSlide--;
    }
    switchSlide(currentSlide);
  });

  // sign in

  const loginForm = document.querySelector(".login--form");
  const loginError = document.getElementById("loginError");

  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(loginForm);

    fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      body: formData,
    })
      .then((resp) => resp.json())
      .then((data) => {
        if (!data.success) {
          loginError.textContent = data.message;
          loginError.style.display = "block";
        } else {
          window.location.href = "/app";
        }
      })
      .catch((error) => console.error("Error:", error));
  });

  const forgotPassBtn = document.querySelector(".login__forgot");

  forgotPassBtn.addEventListener("click", function (e) {
    e.preventDefault();
    console.log("hi");

    closeModal2();
    openModal4();
  });

  // sign up

  const signupForm = document.querySelector(".signup--form");
  const signupError = document.getElementById("signupError");
  signupForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(signupForm);

    fetch("http://127.0.0.1:5000/signup", {
      method: "POST",
      body: formData,
    })
      .then((resp) => resp.json())
      .then((data) => {
        if (!data.success) {
          signupError.textContent = data.message;
          signupError.style.display = "block";
        } else {
          closeModal();
          modal3.classList.remove("hidden");
          overlay.classList.remove("hidden");
          //focus the first input which index is 0 on window load
          window.addEventListener("load", () => inputs[0].focus());
        }
      })
      .catch((error) => console.error("Error:", error));
  });

  // verfication code form

  // iterate over all inputs
  inputs.forEach((input, index1) => {
    input.addEventListener("keyup", (e) => {
      const currentInput = input,
        nextInput = input.nextElementSibling,
        prevInput = input.previousElementSibling;

      // if the value has more than one character then clear it
      if (currentInput.value.length > 1) {
        currentInput.value = currentInput.value.charAt(0);
        //   return;
      }

      // updateCombinedNumber();

      // if the next input is disabled and the current value is not empty
      //  enable the next input and focus on it
      if (
        nextInput &&
        nextInput.hasAttribute("disabled") &&
        currentInput.value !== ""
      ) {
        nextInput.removeAttribute("disabled");
        nextInput.focus();
      }
      // console.log("index1", index1);
      console.log(currentInput.value);
      // if the backspace key is pressed
      if (e.key === "Backspace") {
        if (prevInput) {
          currentInput.setAttribute("disabled", true);
          currentInput.value = "";
          prevInput.focus();
        }
      }

      checkAllFilled();
    });
  });

  // Updating the combinedNumber variable based on input values
  // function updateCombinedNumber() {
  //   combinedNumber = Array.from(inputs)
  //     .map((input) => input.value)
  //     .join("");
  //   console.log("Combined Number:", combinedNumber);
  // }

  // Checking if all inputs are filled and then update the verifyCodeButton class
  function checkAllFilled() {
    const allFilled = Array.from(inputs).every((input) => input.value !== "");
    verifyCodeButton.classList.toggle("active", allFilled);
  }

  // send verification code

  verifyCodeButton.addEventListener("click", (e) => {
    e.preventDefault();

    const csrfToken = document.querySelector(".token_csrf").value;
    const combinedNumber1 = Array.from(document.querySelectorAll(".code"))
      .map((input) => input.value)
      .join("");

    fetch("http://127.0.0.1:5000/verification", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken,
      },
      body: JSON.stringify({ code: combinedNumber1 }),
    })
      .then((resp) => {
        if (!resp.ok) {
          throw new Error("Network response problem" + resp.statusText);
        }
        return resp.json();
      })
      .then((data) => {
        if (data.success) {
          closeModal3();
          modal2.classList.remove("hidden");
          overlay.classList.remove("hidden");
          loginError.textContent = "User registered successfully!";
          loginError.style.display = "block";
          loginError.style.color = "green";
        } else {
          if (data.status === "expired") {
            verificationMsg.textContent = "Verification Code is Expired";
          } else {
            verificationMsg.textContent = "Wrong verification Code";
          }
          verificationMsg.style.display = "block";
        }
        console.log("Success:", data);
      })
      .catch((err) => {
        console.error("Error", err);
      });
  });

  // forgot password part

  const forgotPassForm = document.querySelector(".forgot--pass--form");
  const forgotPassErr = document.getElementById("forgot-pass-err");
  const forgotEmail = document.getElementById("forgot-email");
  forgotPassForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(forgotPassForm);

    fetch("http://127.0.0.1:5000/forgot-password", {
      method: "POST",
      body: formData,
    })
      .then((resp) => resp.json())
      .then((data) => {
        if (!data.success) {
          forgotPassErr.textContent = "Email doesn't exist";
          forgotPassErr.style.display = "block";
          forgotPassErr.style.color = "red";
        } else {
          forgotPassErr.textContent =
            "Email was sent to you please check your inbox";
          forgotPassErr.style.display = "block";
          forgotPassErr.style.color = "green";
        }
      })
      .catch((error) => console.error("Error:", error));
  });
  // const verifyCodeForm = document.querySelector(".code__form");
  // verifyCodeForm.addEventListener("submit", (e) => {
  //   e.preventDefault();
  //   // const formData = new FormData(verifyCodeForm);
  //   const csrfToken = document.querySelector(".token_csrf").value;
  //   const combinedNumber1 = Array.from(document.querySelectorAll(".code"))
  //     .map((input) => input.value)
  //     .join("");
  //   console.log("Sending Code:", combinedNumber1); // Check what you send

  //   // const payload = JSON.stringify({ code: combinedNumber1 });
  //   // console.log(payload);
  //   fetch("/verification", {
  //     method: "POST",
  //     headers: {
  //       "Content-Type": "application/json",
  //       "X-CSRF-Token": csrfToken,
  //     },
  //     body: JSON.stringify({ code: combinedNumber1 }),
  //     // body: formData,
  //   })
  //     .then((resp) => {
  //       if (!resp.ok) {
  //         throw new Error("Network response was not ok " + resp.statusText);
  //       }
  //       return resp.json();
  //     })
  //     .then((data) => {
  //       console.log("Success:", data);
  //     })
  //     .catch((err) => {
  //       console.error("Error", err);
  //     });
  // });
});
