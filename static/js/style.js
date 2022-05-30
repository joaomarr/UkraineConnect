const textHeader = document.querySelector(".log-in-animated");
const dropdowns = document.querySelectorAll(".dropdown");
const img = document.querySelector(".img");
const imgCrop = document.querySelector("#img");
const photoInput = document.querySelector(".photo-input");
const photoSubmit = document.querySelector(".photo-submit");
const fadeEditText = document.querySelector(".fade-edit-text");
const imgIcon = document.querySelector(".editPhotoIcon");
const modal = document.querySelector(".modals");
const overlay = document.querySelector(".overlay");
const btnCloseModal = document.querySelector(".btn--close-modal");
const btnsOpenModal = document.querySelectorAll(".btn--show-modal");

if (message) {
  const messageAlert = `
        <div class="alert alert-${message.category} fade in alert-dismissible position-fixed" style="
        z-index: 10;
        left: 1%;
        bottom: 1%;
        ">
            <a href="#" class="close" data-dismiss="alert" aria-label="close" title="close">×</a>
            <strong>${message.text}</strong>
        </div>
    `;
  document.querySelector("main").insertAdjacentHTML("afterbegin", messageAlert);
}

if (dropdowns) {
  dropdowns.forEach((dropdown) => {
    dropdown.addEventListener("click", function (event) {
      const dropdownMenu = event.target
        .closest(".dropdown")
        .querySelector(".dropdown-menu");
      dropdownMenu.classList.toggle("show");
    });
  });
}

if (textHeader) {
  let strText = textHeader.textContent;

  let timer = setInterval(fadeTranslate, 2500);

  function fadeTranslate() {
    textHeader.classList.add("fade");
    setTimeout(() => {
      if (textHeader.textContent === "Увійти") {
        textHeader.textContent = "Sign In";
        textHeader.classList.remove("fade");
      } else if (textHeader.textContent === "Sign In") {
        textHeader.textContent = "Увійти";
        textHeader.classList.remove("fade");
      } else if (textHeader.textContent === "Зареєструватися") {
        textHeader.textContent = "Register";
        textHeader.classList.remove("fade");
      } else if (textHeader.textContent === "Register") {
        textHeader.textContent = "Зареєструватися";
        textHeader.classList.remove("fade");
      } else {
        return;
      }
    }, "300");
  }
}

if (modal) {
  const openModal = function (e) {
    e.preventDefault();
    modal.classList.remove("hidden");
    overlay.classList.remove("hidden");
  };

  const closeModal = function () {
    modal.classList.add("hidden");
    overlay.classList.add("hidden");
  };

  btnsOpenModal.forEach((btn) => btn.addEventListener("click", openModal));
  img.addEventListener("mouseenter", function () {
    imgIcon.classList.remove("hidden");
    fadeEditText.classList.remove("fade");
  });
  img.addEventListener("mouseleave", function () {
    imgIcon.classList.add("hidden");
    fadeEditText.classList.add("fade");
  });
  btnCloseModal.addEventListener("click", closeModal);
  overlay.addEventListener("click", closeModal);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });

  const selectedFile = { value: "" };
  const imgSrc = { value: "" };
  const fileReader = new FileReader();
  let cropper;

  fileReader.addEventListener("load", function (e) {
    if (cropper) {
      cropper.destroy();
    }
    imgSrc.value = e.target.result;
    $("#img").attr("src", imgSrc.value);
    cropper = new Cropper(imgCrop, {
      aspectRatio: 1,
      viewMode: 2,
      responsive: false,
      zoomOnWheel: false,
    });
  });
  photoInput.addEventListener("change", function (e) {
    files = e.target.files || e.dataTransfer.files;
    if (files.length) {
      selectedFile.value = files[0];
      fileReader.readAsDataURL(selectedFile.value);
    }
  });
  photoSubmit.addEventListener("click", function (e) {
    e.preventDefault();
    if (!cropper) {
      return;
    }
    const canvasData = cropper.getCroppedCanvas();
    canvasData.toBlob(function (blob) {
      url = URL.createObjectURL(blob);
      let file = fetch(url)
        .then((r) => r.blob())
        .then((file) => {
          const data = new FormData();
          data.append("file", file, "file");
          return data;
        })
        .then((d) => {
          fetch("/profile", {
            method: "POST",
            body: d,
          });
        })
        .then(() => document.location.reload());
    });
  });
}
