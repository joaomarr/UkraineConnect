class Map {
  map;
  constructor() {
    this._loadMap();
    this._loadMarkers();
  }

  _loaded() {
    const mapDiv = document.querySelector("#mapDiv");
    const spinner = document.querySelector(".loading");
    spinner.classList.add("fade");
    setTimeout(() => {
      mapDiv.removeChild(spinner);
    }, "350");
  }

  _loadMap() {
    const latitude = 49.383022;
    const longitude = 31.1828699;
    const coords = [latitude, longitude];

    this.map = L.map("map").setView(coords, 6);
    this.map.setMaxBounds(this.map.getBounds());
    L.tileLayer(
      "https://api.maptiler.com/maps/toner/256/{z}/{x}/{y}.png?key=yPOIUS64SUXkiGO55yve",
      {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        minZoom: 6,
      }
    ).addTo(this.map);

    const customStyle = {
      stroke: false,
      fillOpacity: 0.3,
    };

    L.geoJson(ukraineGeo, { style: customStyle }).addTo(this.map);
  }

  _formatDate(postDate) {
    const calcDaysPassed = (date1, date2) => {
      const dateUTC = new Date(
        date1.getUTCFullYear(),
        date1.getUTCMonth(),
        date1.getUTCDate(),
        date1.getUTCHours(),
        date1.getUTCMinutes(),
        date1.getUTCSeconds()
      );
      return Math.round(Math.abs(date2 - dateUTC) / (1000 * 60 * 60));
    };

    const hoursPassed = calcDaysPassed(new Date(), postDate);
    let date = [];
    if (hoursPassed <= 24) {
      date[0] = `${hoursPassed} пройшли години`;
      date[1] = `${hoursPassed} hours ago`;
    }
    if (hoursPassed > 24 && hoursPassed < 48) {
      date[0] = "Вчора";
      date[1] = "Yesterday";
    }
    if (hoursPassed >= 48) {
      date[0] = `${Math.round(hoursPassed / 24)} днів тому`;
      date[1] = `${Math.round(hoursPassed / 24)} days ago`;
    }

    return date;
  }

  async _fetchPosts() {
    const params = {
      method: "POST",
    };
    const response = await fetch("/getPosts", params);
    const posts = await response.json();
    return posts;
  }

  async _loadMarkers() {
    await this._fetchPosts()
      .then((posts) => {
        for (let post in posts) {
          const name = posts[post]["userName"];
          const imgPath = posts[post]["userPhotoFilename"];
          const likes = posts[post]["likes"];
          const isLiked = posts[post]["liked"];
          const coords = [posts[post].lat, posts[post].long];
          const title = posts[post].title;
          const text = posts[post].text;
          const postDate = new Date(posts[post].postDate);
          const date = this._formatDate(postDate);
          const postId = posts[post].postId;

          const htmlContent = `
            <div class="card text-white bg-dark post" id=${postId} style="max-width: 18rem;">
              <div class="card-header d-flex flex-column align-items-center">
                <img class="rounded-circle mb-2" width="50rem" height="50rem" src=${
                  imgPath
                    ? imgPath
                    : "https://www.rogowaylaw.com/wp-content/uploads/Blank-Employee.jpg"
                }>
                <h6 class="name ${
                  posts[post]["isFromUser"] ? "text-primary" : "text-secondary"
                }">${name}</h6>
                <div class="d-inline-block">
                  <span class="date">${
                    date[0]
                  } /</span><br><span class="dateEN text-secondary"> ${
            date[1]
          }</span>
                </div>
              </div>
              <div class="card-body">
                <h5 class="card-title">${title}</h5>
                <p class="card-text">${text}</p>
              </div>
              <div class="card-footer d-flex ${
                posts[post]["isFromUser"]
                  ? "justify-content-between"
                  : "justify-content-end"
              }  align-items-center">
                ${
                  posts[post]["isFromUser"]
                    ? `
                <div class="userOptions">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="delete mx-1 bi bi-trash" viewBox="0 0 16 16">
                      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                      <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                  </svg>
                </div>
                `
                    : ""
                }
                <div>
                  <h7 class="likes text-secondary px-2">${
                    likes ? likes : ""
                  }</h7>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star like" viewBox="0 0 16 16">
                    ${
                      isLiked
                        ? `<path class="likePath" d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"></path>`
                        : `<path class="likePath" d="M2.866 14.85c-.078.444.36.791.746.593l4.39-2.256 4.389 2.256c.386.198.824-.149.746-.592l-.83-4.73 3.522-3.356c.33-.314.16-.888-.282-.95l-4.898-.696L8.465.792a.513.513 0 0 0-.927 0L5.354 5.12l-4.898.696c-.441.062-.612.636-.283.95l3.523 3.356-.83 4.73zm4.905-2.767-3.686 1.894.694-3.957a.565.565 0 0 0-.163-.505L1.71 6.745l4.052-.576a.525.525 0 0 0 .393-.288L8 2.223l1.847 3.658a.525.525 0 0 0 .393.288l4.052.575-2.906 2.77a.565.565 0 0 0-.163.506l.694 3.957-3.686-1.894a.503.503 0 0 0-.461 0z"/></path>`
                    }
                  </svg>
                </div>
              </div>
            </div>
            `;

          const goldIcon = new L.Icon({
            iconUrl:
              "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png",
            shadowUrl:
              "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
          });

          const blueIcon = new L.Icon({
            iconUrl:
              "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
            shadowUrl:
              "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
          });

          const markers = {};
          if (posts[post]["isFromUser"]) {
            markers[`${postId}`] = L.marker(coords, { icon: blueIcon });

            markers[`${postId}`]
              .addTo(this.map)
              .bindPopup(htmlContent, {
                className: "popupStyle",
                autoClose: false,
                maxWidth: 400,
                minWidth: 180,
                autoPan: false,
              })
              .openPopup();
          } else {
            markers[`${postId}`] = L.marker(coords, { icon: goldIcon });

            markers[`${postId}`]
              .addTo(this.map)
              .bindPopup(htmlContent, {
                className: "popupStyle",
                autoClose: false,
                maxWidth: 400,
                minWidth: 180,
                autoPan: false,
              })
              .openPopup();
          }
        }
      })
      .then(() => {
        this._loaded();
        this._handleLike();
        this.map.on("popupopen", this._handleLike);
        this._handleDeletePost();
        this.map.on("popupopen", this._handleDeletePost);
      });
  }

  _handleLike() {
    const likeButtons = document.querySelectorAll(".like");
    likeButtons.forEach((likeButton) => {
      likeButton.addEventListener("click", function (event) {
        const id = event.target.closest(".post").id;
        socketio.emit("submitLike", { id: id });
      });
    });
    socketio.on("showLike", ({ id, liked }) => {
      const likeParent = document.getElementById(`${id}`);
      const likeButton = likeParent.querySelector(".like");
      const likeNumber = likeParent.querySelector(".likes");

      let likes = parseInt(likeNumber.textContent)
        ? parseInt(likeNumber.textContent)
        : likeNumber.textContent;

      if (liked === true) {
        likeButton.innerHTML = `<path class="likePath" d="M2.866 14.85c-.078.444.36.791.746.593l4.39-2.256 4.389 2.256c.386.198.824-.149.746-.592l-.83-4.73 3.522-3.356c.33-.314.16-.888-.282-.95l-4.898-.696L8.465.792a.513.513 0 0 0-.927 0L5.354 5.12l-4.898.696c-.441.062-.612.636-.283.95l3.523 3.356-.83 4.73zm4.905-2.767-3.686 1.894.694-3.957a.565.565 0 0 0-.163-.505L1.71 6.745l4.052-.576a.525.525 0 0 0 .393-.288L8 2.223l1.847 3.658a.525.525 0 0 0 .393.288l4.052.575-2.906 2.77a.565.565 0 0 0-.163.506l.694 3.957-3.686-1.894a.503.503 0 0 0-.461 0z"/></path>`;
        if (likes === 1) {
          likes = "";
          likeNumber.textContent = likes;
        } else {
          likes -= 1;
          likeNumber.textContent = likes;
        }
      } else {
        likeButton.innerHTML = `<path class="likePath" d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"></path>`;
        likes += 1;
        likeNumber.textContent = likes;
      }
    });
  }

  _handleDeletePost() {
    const deleteButtons = document.querySelectorAll(".delete");
    deleteButtons.forEach((deleteButton) => {
      deleteButton.addEventListener("click", function (event) {
        const post = event.target.closest(".post");
        const id = post.id;
        if (post.querySelector(".alert")) {
          return;
        }

        post.insertAdjacentHTML(
          "beforeend",
          `
              <div class="alert alert-warning fade in alert-dismissible">
                  <a href="#" class="close" data-dismiss="alert" aria-label="close" title="close">×</a>
                  <span class="btn btn-primary deletePost" onclick="socketio.emit('deletePost', {post_id: ${id}})">Delete Post</span>
              </div>
          `
        );
      });
    });
    socketio.on("postDeleted", () => {
      window.location.reload();
    });
  }
}

const socketio = io("http://127.0.0.1:5000/");
if (document.querySelector("#map")) {
  const app = new Map();
}
