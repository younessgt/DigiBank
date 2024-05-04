"use strict";

document.addEventListener("DOMContentLoaded", function () {
  const resetForm = document.querySelector(".reset--form");
  const resetError = document.getElementById("resetError");
  const paragraphText = document.querySelector(".text");
  resetForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const newPassword = document.getElementById("new_password").value;
    const confirmPassword = document.getElementById("confirm_password").value;

    console.log(newPassword);
    console.log(confirmPassword);

    if (newPassword !== confirmPassword) {
      console.log("yes");
      resetError.textContent = "Passwords do not match";
      resetError.style.display = "block";
      resetError.style.color = "red";
      return;
    }

    resetError.style.display = "none";
    const token = window.location.pathname.split("/").pop();

    console.log(token);
    const resetPasswordUrl = `http://127.0.0.1:5000/reset-password/${token}`;
    const formData = new FormData(resetForm);
    fetch(resetPasswordUrl, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        if (data.success) {
          resetError.textContent = "Passwords updated successfully";
          resetError.style.display = "block";
          resetError.style.color = "green";
          paragraphText.textContent =
            "You will be redirected to the home page in 5 seconds";
          paragraphText.style.display = "block";
          setTimeout(() => {
            window.location.href = "/";
          }, 5000);
        }
      })
      .catch((error) => console.error("problem with fetch operation:", error));
  });
});
