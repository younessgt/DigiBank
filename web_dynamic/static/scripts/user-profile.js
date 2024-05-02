"use strict";
document.addEventListener("DOMContentLoaded", function () {
  const textError = document.getElementById("textError");
  document.getElementById("btnAccount").addEventListener("click", function () {
    document.getElementById("accountForm").style.display = "block";
    document.getElementById("settingsForm").style.display = "none";
  });

  document.getElementById("btnSettings").addEventListener("click", function () {
    document.getElementById("accountForm").style.display = "none";
    document.getElementById("settingsForm").style.display = "block";
  });

  const account = {
    profileImagePath: "",
  };

  let file;
  // changing photo
  document.getElementById("profileImage").onchange = function (event) {
    textError.style.display = "none";
    file = event.target.files[0];
    // console.log(file);

    if (event.target.files && file) {
      // Update the profile image in the sidebar.
      const fileType = file.type;
      if (!fileType.match("image/*")) {
        textError.textContent = "Please Select Image Format";
        textError.style.display = "block";
        return;
      }

      if (file.size > 2097152) {
        textError.textContent = "File size exceeds 2MB";
        textError.style.display = "block";
        textError.style.color = "red";
        return;
      }
      let reader = new FileReader();
      reader.onload = function (e) {
        // console.log(e);
        document.querySelector(".profile-image-container img").src =
          e.target.result;
        document.querySelector(".profile img").src = e.target.result;
      };
      reader.readAsDataURL(event.target.files[0]);
    }
  };

  const accountForm = document.getElementById("accountForm");

  accountForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    if (file) {
      if (file.size > 2097152) {
        textError.textContent = "File size exceeds 2MB";
        textError.style.display = "block";
        textError.style.color = "red";
        return;
      }
    }

    const oldPassword = document.getElementById("oldPassword").value;
    const newPassword = document.getElementById("newPassword").value;

    if ((oldPassword && !newPassword) || (!oldPassword && newPassword)) {
      textError.textContent =
        "Old and new passwords are required to update your password.";
      textError.style.display = "block";
      return;
    }

    const formData = new FormData(accountForm);
    try {
      const resp = await fetch("http://127.0.0.1:5001/api/v1/update-profile", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      if (resp.status === 200) {
        textError.style.color = "green";
        textError.textContent = "Update successful";
        textError.style.display = "block";
      } else {
        textError.style.color = "red";
        textError.textContent = "Uups Something goes Wrong";
        textError.style.display = "block";
      }
    } catch (error) {
      console.error("Error:", error);
    }
  });

  const displayProfileImg = function (acc) {
    const profileImg = document.querySelector(".profile img");
    const profileImgContainer = document.querySelector(
      ".profile-image-container img"
    );
    if (profileImg) {
      profileImg.setAttribute("src", `${acc.profileImagePath}`);
    }

    if (profileImgContainer) {
      profileImgContainer.setAttribute("src", `${acc.profileImagePath}`);
    }

    // console.log(profileImg);
  };

  // update UI
  const updateUI = function (acc) {
    // Display Profile Image
    displayProfileImg(acc);
  };

  async function fetchProfileImage() {
    return fetch("http://127.0.0.1:5001/api/v1/some/infos", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        if (data) {
          // console.log(data);

          account.profileImagePath = data.profile_img_path;

          // console.log(account);
          updateUI(account);
        }
      })
      .catch((error) => console.error("problem with fetch operation:", error));
  }

  fetchProfileImage();

  /* bank statement part */

  const notifications = document.querySelector(".notifications");
  const checkButton = document.getElementById("checkButton");

  const toastDetails = {
    timer: 3000,
    success: {
      icon: "fa-circle-check",
      // text: "Success: This is a success toast.",
    },
    error: {
      icon: "fa-circle-xmark",
      // text: "Error: Please select an end date.",
    },
    warning: {
      icon: "fa-triangle-exclamation",
      // text: "Warning: This is a warning toast.",
    },
    info: {
      icon: "fa-circle-info",
      // text: "Info: This is an information toast.",
    },
  };

  const removeToast = (toast) => {
    toast.classList.add("hide");
    if (toast.timeoutId) clearTimeout(toast.timeoutId);
    setTimeout(() => toast.remove(), 500);
  };
  let closeNotification;
  const createToast = (type, msg) => {
    const { icon, text } = toastDetails[type];
    const toast = document.createElement("li");
    toast.className = `toast ${type}`;
    toast.innerHTML = `<div class="column">
                         <i class="fa-solid ${icon}"></i>
                         <span>${msg}</span>
                      </div>
                      <i class="fa-solid fa-xmark" id="close-notification"></i>`;
    notifications.appendChild(toast);
    closeNotification = document.getElementById("close-notification");
    closeNotification.addEventListener("click", (e) => {
      removeToast(e.target.parentElement);
    });
    // console.log(closeNotification);
    toast.timeoutId = setTimeout(() => removeToast(toast), toastDetails.timer);
    console.log(toast);
  };
  document.getElementById("startDate").addEventListener("change", function () {
    const startDate = document.getElementById("startDate").value;
    const endDateInput = document.getElementById("endDate");

    if (startDate) {
      endDateInput.min = startDate;
    }
  });

  document.getElementById("endDate").addEventListener("change", function () {
    const startDateInput = document.getElementById("startDate");
    const endDate = document.getElementById("endDate").value;

    if (endDate) {
      startDateInput.max = endDate;
    }
  });

  // check button
  checkButton.addEventListener("click", function (e) {
    e.preventDefault();
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;

    if (!startDate) {
      createToast("warning", "Warning: Please select a start date.");

      return;
    }
    if (!endDate) {
      createToast("warning", "Warning: Please select an end date.");

      return;
    }

    fetch("http://127.0.0.1:5001/api/v1/check-movements-date", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ start_date: startDate, end_date: endDate }),
    })
      .then((resp) => {
        if (!resp.ok) {
          throw new Error("Network response was not ok");
        }
        return resp.json();
      })
      .then((data) => {
        if (data.success && data.movements) {
          document.getElementById("downloadButton").style.display = "block";
          createToast("success", "Success: Bank statement PDF available.");
          console.log(data);
        }
        if (data.success && !data.movements) {
          document.getElementById("downloadButton").style.display = "none";
          createToast("info", "Info: No movements found in this date range");
        }
      })
      .catch((error) => console.error("problem with fetch operation:", error));
  });

  // download pdf button
  document
    .getElementById("downloadButton")
    .addEventListener("click", function () {
      const startDate = document.getElementById("startDate").value;
      const endDate = document.getElementById("endDate").value;

      // alert(`Downloading bank statement from ${startDate} to ${endDate}`);
      // // Simulate download (This should be replaced with actual file download logic)
      // window.open("path/to/download/statement.pdf"); // Link to the generated PDF file

      fetch("http://127.0.0.1:5001/api/v1/download-statement-pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ start_date: startDate, end_date: endDate }),
      })
        .then((resp) => {
          if (!resp.ok) {
            throw new Error("Network response was not ok");
          }
          return resp.blob();
        })
        .then((blob) => {
          // Create a URL for the blob object
          const url = window.URL.createObjectURL(blob);
          // Create a new anchor element
          const a = document.createElement("a");
          a.href = url;
          a.download = "bank_statement.pdf"; // Specify the file name for download
          document.body.appendChild(a);
          a.click(); // Start the download

          // Cleanup: remove the anchor element and revoke the URL
          a.remove();
          window.URL.revokeObjectURL(url);
        })
        .catch((error) =>
          console.error("problem with fetch operation:", error)
        );
    });
});
