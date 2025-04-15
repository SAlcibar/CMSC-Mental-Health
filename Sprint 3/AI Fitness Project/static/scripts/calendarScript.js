let display = document.querySelector(".display");
let previous = document.querySelector(".left");
let next = document.querySelector(".right");
let days = document.querySelector(".days");
let selected = document.querySelector(".selected");

let today = new Date();
let date = new Date(today);
let year = date.getFullYear();
let month = date.getMonth();


function calendarDisplay() {
  days.innerHTML = '';

  let formattedDate = date.toLocaleString("en-US", {
    month: "long",
    year: "numeric",
  });
  display.innerHTML = formattedDate;

  const firstDay = new Date(year, month, 1);
  const firstDayIndex = firstDay.getDay();

  const lastDay = new Date(year, month + 1, 0);
  const numberOfDays = lastDay.getDate();

  for (let x = 1; x <= firstDayIndex; x++) {
    let div = document.createElement("div");
    div.classList.add("days");
    div.innerHTML = "";
    days.appendChild(div);
  }
  for (let i = 1; i <= numberOfDays; i++) {
    let div = document.createElement("div");
    div.classList.add("day");

    let dayNum = document.createElement("div");
    dayNum.classList.add("days");
    dayNum.textContent = i;
    div.appendChild(dayNum);

    let plusButton = document.createElement("button");
    plusButton.classList.add("plus-button");
    plusButton.textContent = "+";

    div.appendChild(plusButton);

    days.appendChild(div);


    let currentDate = new Date(year, month, i);
    if (
      currentDate.getFullYear() === new Date().getFullYear() &&
      currentDate.getMonth() === new Date().getMonth() &&
      currentDate.getDate() === new Date().getDate()
    ) {
      div.classList.add("current-date");
    }
  } 
  displaySelectedDate();
  displaySelectedPlus();
}

function displaySelectedPlus(){
  const dayElements = document.querySelectorAll(".day");
    dayElements.forEach((day) => {
    day.addEventListener("click", (e) => {
      e.stopPropagation(); 
       createPage();
    });
  });
}

function createPage(){
  const bottomPage = document.createElement("div");
  bottomPage.classList.add("bottom-page");
  bottomPage.innerHTML = `
    <div class="bottom-page" id="bottomPage">
  <button class="close-button" >✕</button>
  <h2>FITNESS LOG INFO TO BE PLACED HERE</h2>
</div>
`;
document.body.appendChild(bottomPage);

bottomPage.querySelector(".close-button").addEventListener("click", () => {
  bottomPage.remove();
});
}

function displaySelectedDate() {
  const plusElement = document.querySelectorAll(".plus-button");
  plusElement.forEach((plusButton)=> {
      plusButton.addEventListener("click", (e) => {
       openPopup();
      });
    });
  }
function openPopup(){
  const popup = document.createElement("div");
  popup.classList.add("popup-container");

  popup.innerHTML = `
  <div class="popup">
    <button class="cardio">Cardio</button>
     <button class="muscular">Muscular</button>
      <button class="removeButton">✕</button>
  </div>
  `;

  document.body.appendChild(popup);

  popup.querySelector(".removeButton").addEventListener("click", () => {
    popup.remove();
  });
  popup.querySelector(".cardio").addEventListener("click", cardioLink);
  popup.querySelector(".muscular").addEventListener("click", muscularLink);
}

function cardioLink() {
  window.open("/cardio-log", "_blank");
}

function muscularLink() {
  window.open("/Sprint 3/AI Fitness Project/templates/workout-log.html", "_blank");
}

previous.addEventListener("click", () => {
  month--;
  if (month < 0) {
    month = 11;
    year--;
  }
  date.setFullYear(year, month);
  calendarDisplay();
});

next.addEventListener("click", () => {
  month++;
  if (month > 11) {
    month = 0;
    year++;
  }
  date.setFullYear(year, month);
  calendarDisplay();
});

calendarDisplay();
