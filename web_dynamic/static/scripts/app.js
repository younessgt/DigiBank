"use strict";

// Elements
document.addEventListener("DOMContentLoaded", function () {
  const labelDate = document.querySelector(".date");
  const labelBalance = document.querySelector(".balance__value");
  const labelSumIn = document.querySelector(".summary__value--in");
  const labelSumOut = document.querySelector(".summary__value--out");
  const labelSumInterest = document.querySelector(".summary__value--interest");
  const labelTimer = document.querySelector(".timer");
  const labelLogout = document.querySelector(".logout-timer");

  const containerMovements = document.querySelector(".movements");

  const inputTransferTo = document.querySelector(".form__input--to");
  const inputTransferAmount = document.querySelector(".form__input--amount");
  const inputLoanAmount = document.querySelector(".form__input--loan-amount");

  const userName = document.querySelector(".user__name");
  const formTransfer = document.querySelector(".form--transfer");
  const formLoan = document.querySelector(".form--loan");
  const formClose = document.querySelector(".form--close");

  const account = {
    username: "",
    movements: [],
    movementDates: [],
    sender_receiver: [],
    balance: 0,
    locale: "",
    status: "",
    currency: "",
  };

  // dop-down menu
  const profile = document.querySelector(".profile");
  const menu = document.querySelector(".menu");

  profile.addEventListener("click", function (e) {
    menu.classList.toggle("active");
    e.stopPropagation();
  });

  const closeMenu = function () {
    if (menu.classList.contains("active")) {
      menu.classList.remove("active");
    }
  };

  document.body.addEventListener("click", closeMenu);

  // formating date
  const formatMovementDate = function (fullDay, locale) {
    const calcDays = (day1, day2) =>
      Math.round(Math.abs(day2 - day1) / (1000 * 60 * 60 * 24));

    const daysPassed = calcDays(new Date(), fullDay);

    if (daysPassed === 0) return "Today";
    if (daysPassed === 1) return "Yesterday";
    if (daysPassed <= 7) return `${daysPassed} days ago`;
    // internalization dates
    return new Intl.DateTimeFormat(locale).format(fullDay);
  };

  // formatting movements values
  const formatCur = function (acc, mov) {
    const formattedMov = new Intl.NumberFormat(acc.locale, {
      style: "currency",
      currency: acc.currency,
    }).format(mov);
    return formattedMov;
  };
  let user = true;
  // display movements
  const displayMovements = function (acc, sort = false) {
    containerMovements.innerHTML = "";

    const currentDay = new Date();
    const options = {
      hour: "numeric",
      minute: "numeric",
      day: "numeric",
      month: "numeric",
      year: "numeric",
    };
    labelDate.textContent = new Intl.DateTimeFormat(acc.locale, options).format(
      currentDay
    );
    if (user) {
      userName.insertAdjacentHTML(
        "afterbegin",
        `${acc.username}<br><span>Welcome Back</span>`
      );
      user = false;
    }

    acc.movements.forEach(function (mov, i) {
      const type = mov > 0 ? "deposit" : "withdrawal";
      const fullDay = new Date(acc.movementDates[i]);
      let sendReceiver = acc.sender_receiver[i];

      const displayDay = formatMovementDate(fullDay, acc.locale);
      // console.log(typeof displayDay);
      const formattedMov = formatCur(acc, mov);
      const html = `
            <div class="movements__row">
              <div class="movements__type movements__type--${type}">${type}</div>
              <div class="movements__date">${displayDay}</div>
              <div class="movements__sendReceiver">${sendReceiver}</div>
              <div class="movements__value">${formattedMov}</div>
            </div>
          `;

      containerMovements.insertAdjacentHTML("beforeend", html);
    });
  };

  const calcDisplayBalance = function (acc) {
    const formattedMov = formatCur(acc, acc.balance);
    labelBalance.textContent = `${formattedMov}`;
  };

  const calcDisplaySummary = function (acc) {
    // console.log(acc);
    const incomes = acc.movements
      .filter((mov) => mov > 0)
      .reduce((acc, mov) => acc + mov, 0);

    const formattedMov1 = formatCur(acc, incomes);
    labelSumIn.textContent = `${formattedMov1}`;

    // console.log(acc.movements);
    const out = acc.movements
      .filter((mov) => mov < 0)
      .reduce((acc, mov) => acc + mov, 0);

    console.log(out);
    const formattedMov2 = formatCur(acc, Math.abs(out));
    labelSumOut.textContent = `${formattedMov2}`;

    const interest = acc.movements
      .filter((mov) => mov > 0)
      .map((deposit) => (deposit * 1.2) / 100)
      .filter((int, i, arr) => {
        // console.log(arr);
        return int >= 1;
      })
      .reduce((acc, int) => acc + int, 0);

    const formattedMov3 = formatCur(acc, interest);
    labelSumInterest.textContent = `${formattedMov3}`;
  };

  // display UI
  const updateUI = function (acc) {
    // Display movements
    displayMovements(acc);

    // Display balance
    calcDisplayBalance(acc);

    // Display summary
    calcDisplaySummary(acc);
  };

  // getting the user info to setup the movement part

  async function fetchMouvement() {
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
          account.movements = [];
          account.movementDates = [];
          account.sender_receiver = [];
          const movements_array = data.movements;
          account.currency = data.currency;
          account.username = data.username;
          account.balance = data.account.balance;
          account.status = data.account.status;
          account.locale = account.currency === "USD" ? "en-US" : "fr-FR";

          movements_array.forEach((movement) => {
            account.movements.push(movement.amount);
            account.movementDates.push(movement.date);
            if (movement.type === "deposit" && movement.sender) {
              account.sender_receiver.push(movement.sender);
            } else if (movement.type === "withdrawal" && movement.receiver) {
              account.sender_receiver.push(movement.receiver);
            } else {
              account.sender_receiver.push("Unknown");
            }
          });
          // console.log(account);
          updateUI(account);
        }
      })
      .catch((error) => console.error("problem with fetch operation:", error));
  }

  fetchMouvement();

  // performing transfer operation

  const transferError = document.getElementById("transferError");

  formTransfer.addEventListener("submit", async function (e) {
    e.preventDefault();
    // console.log(Number(inputTransferAmount.value));
    // console.log(typeof Number(inputTransferAmount.value));
    if (Number(inputTransferAmount.value) > account.balance) {
      transferError.textContent = "Not enough funds";
      transferError.style.display = "block";
      return;
    }
    const formData = new FormData(formTransfer);
    try {
      const resp = await fetch("http://127.0.0.1:5001/api/v1/transfer", {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      const data = await resp.json();
      if (resp.status === 200) {
        await fetchMouvement();
        inputTransferAmount.value = "";
        inputTransferTo.value = "";
      } else if (resp.status === 401 && data.user === false) {
        transferError.textContent = "Email not found";
        transferError.style.display = "block";
      } else if (resp.status === 401 && data.user === true) {
        transferError.textContent = "Transfer not allowed to your account";
        transferError.style.display = "block";
      }
    } catch (error) {
      console.error("Error:", error);
    }
  });

  // performing Loan operation

  const loanError = document.getElementById("loanError");
  formLoan.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(formLoan);
    try {
      const resp = await fetch("http://127.0.0.1:5001/api/v1/loan", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      if (resp.status === 200) {
        await fetchMouvement();
        inputLoanAmount.value = "";
      } else {
        loanError.textContent = "Problem occurred please try again";
        loanError.style.display = "block";
      }
    } catch (error) {
      console.error("Error:", error);
    }
  });

  async function deleteUser() {
    const resp = await fetch("http://127.0.0.1:5000/logout", {
      method: "GET",
      credentials: "include",
    });
    if (resp.redirected) {
      window.location.href = resp.url;
    }
    return resp;
  }

  const closeError = document.getElementById("closeError");
  formClose.addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(formClose);
    try {
      const resp = await fetch("http://127.0.0.1:5001/api/v1/delete", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      if (resp.status === 200) {
        await deleteUser();
      } else {
        closeError.textContent = "Invalid username or password";
        closeError.style.display = "block";
      }
    } catch (error) {
      console.error("Error:", error);
    }
  });

  let timer, displayTimerId;
  // TimeLogout
  const calcTimeLogout = function () {
    let time = 20;

    const tick = async function () {
      const min = String(Math.trunc(time / 60)).padStart(2, 0);
      const sec = String(time % 60).padStart(2, 0);
      labelTimer.textContent = `${min}:${sec}`;
      // console.log(20);

      if (time === 0) {
        // console.log(timer);
        clearInterval(timer);
        const resp = await fetch("http://127.0.0.1:5000/logout", {
          method: "GET",
          credentials: "include",
        });
        if (resp.redirected) {
          window.location.href = resp.url;
        }
        return resp;
      }
      time--;
    };

    tick();
    timer = setInterval(tick, 1000);
    // return timer;
  };

  // resetting the time once the user move the mouse or click on the body
  const resetTimer = function () {
    labelLogout.style.display = "none";

    clearTimeout(displayTimerId);
    if (timer) clearInterval(timer);
    displayTimerId = setTimeout(function () {
      calcTimeLogout();

      labelLogout.style.display = "block";
    }, 5000);
  };

  // when a user is login we attach an eventListner to the body after 1 second to controle the activity of the user
  setTimeout(() => {
    // console.log(10);
    document.body.addEventListener("mousemove", resetTimer);
    document.body.addEventListener("click", resetTimer);
  }, 1000);
  resetTimer();
});
