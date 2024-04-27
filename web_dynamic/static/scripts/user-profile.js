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

  // changing photo
  document.getElementById("profileImage").onchange = function (event) {
    textError.style.display = "none";
    const file = event.target.files[0];
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
        textError.textContent = "Uups Something Wrong";
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
});
