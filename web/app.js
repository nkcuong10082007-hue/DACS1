let movies = [];
let bookingMovie = null;
let bookingCinema = "";
let selectedSeats = [];
let bookedSeats = [];
let appInitialized = false;
let currentUser = JSON.parse(localStorage.getItem("cinego_user") || "null");
let authMode = "login";
let contentItems = [];
let currentContentCategory = "offer";
let editingContentId = null;
let editingMovieId = null;
let hotMovies = [];
let currentHeroIndex = 0;
let heroTimer = null;
let paymentCheckTimer = null;
let waitingBankPayment = false;
let currentMovieList = [];
let visibleMovieCount = 10;
const MOVIES_PER_PAGE = 10;
const BANK_CONFIG = {
  bankId: "BIDV",
  bankName: "BIDV",
  accountNo: "96247CINEGO",
  accountName: "NGUYEN KHAC CUONG",
  template: "compact2"
};
function formatMoney(value) {
  return Number(value || 0).toLocaleString("vi-VN") + " VNĐ";
}
function getBookingTotal() {
    return Math.round(selectedSeats.length * Number(bookingMovie?.price || 0));
}

function getSelectedPaymentMethod() {
  return document.querySelector('input[name="paymentMethod"]:checked')?.value || "cash";
}

function paymentMethodLabel(method) {
  return method === "bank" ? "Chuyển khoản ngân hàng" : "Tiền mặt";
}

function getTransferNote() {
  const movieId = bookingMovie?.id || "PHIM";
  const seatsText = selectedSeats.length ? selectedSeats.join("-") : "GHE";
  return `CINEGO${movieId}${seatsText}`.replace(/[^A-Z0-9]/gi, "").toUpperCase();
}

function createBankQrUrl(amount) {
  const note = getTransferNote();

  return `https://img.vietqr.io/image/${BANK_CONFIG.bankId}-${BANK_CONFIG.accountNo}-${BANK_CONFIG.template}.png` +
    `?amount=${amount}` +
    `&addInfo=${encodeURIComponent(note)}` +
    `&accountName=${encodeURIComponent(BANK_CONFIG.accountName)}`;
}

function updatePaymentBox() {
  const bankBox = document.getElementById("bankTransferBox");
  const qrImage = document.getElementById("bankQrImage");
  const transferAmount = document.getElementById("transferAmount");
  const transferAccount = document.getElementById("transferAccount");
  const transferNote = document.getElementById("transferNote");

  if (!bankBox || !qrImage || !transferAmount || !transferAccount || !transferNote) return;

  const method = getSelectedPaymentMethod();
  const total = getBookingTotal();
  const note = getTransferNote();

  bankBox.classList.toggle("hidden", method !== "bank");

  transferAmount.textContent = formatMoney(total);
  transferAccount.textContent = `${BANK_CONFIG.bankName} - ${BANK_CONFIG.accountNo} - ${BANK_CONFIG.accountName}`;
  transferNote.textContent = `Nội dung chuyển khoản: ${note}`;

  if (method === "bank" && total > 0) {
    qrImage.src = createBankQrUrl(total);
  } else {
    qrImage.removeAttribute("src");
  }
}
function setBankWaiting(isWaiting) {
  waitingBankPayment = isWaiting;

  const btn = document.getElementById("continuePaymentBtn");
  const waitingText = document.getElementById("paymentWaitingText");

  if (btn) {
    btn.disabled = isWaiting;
    btn.textContent = isWaiting ? "Đang chờ chuyển khoản..." : "Tiếp tục thanh toán";
  }

  if (waitingText) {
    waitingText.textContent = isWaiting
      ? "Đang chờ SePay xác nhận giao dịch. Vui lòng không tắt cửa sổ này."
      : "Quét QR bằng app ngân hàng để chuyển khoản.";
  }
}

function stopPaymentPolling() {
  if (paymentCheckTimer) {
    clearInterval(paymentCheckTimer);
    paymentCheckTimer = null;
  }

  setBankWaiting(false);
}

async function completeBookingAfterPayment(method) {
  const showDate = document.getElementById("bookingDate").value;
  const showTime = document.getElementById("bookingTime").value;
  const total = getBookingTotal();

  const result = await window.pywebview.api.create_booking({
    user_id: currentUser.id,
    movie_name: bookingMovie.name,
    cinema: bookingCinema || "CineGO Hà Nội",
    show_date: showDate,
    show_time: showTime,
    seats: selectedSeats,
    total,
    method
  });

  if (!result.ok) {
    alert(result.message || "Không thể đặt vé");
    await loadBookedSeats();
    renderSeats();
    updateBookingTotal();
    return;
  }

  alert(`Thanh toán thành công!\nMã vé: ${result.ticket_code}`);

  selectedSeats = [];
  await loadBookedSeats();
  renderSeats();
  updateBookingTotal();
}

async function checkPaymentOnce() {
  const total = getBookingTotal();
  const paymentCode = getTransferNote();

  const waitingText = document.getElementById("paymentWaitingText");
  if (waitingText) {
    waitingText.textContent = `Đang kiểm tra giao dịch ${paymentCode}...`;
  }

  const result = await window.pywebview.api.check_bank_payment(paymentCode, total);

  if (!result.ok) {
    if (waitingText) {
      waitingText.textContent = result.message || "Đang chờ SePay xác nhận giao dịch...";
    }
    return false;
  }

  stopPaymentPolling();
  await completeBookingAfterPayment("Chuyển khoản ngân hàng");
  return true;
}

function startPaymentPolling() {
  stopPaymentPolling();
  setBankWaiting(true);

  checkPaymentOnce();

  paymentCheckTimer = setInterval(async () => {
    try {
      await checkPaymentOnce();
    } catch (error) {
      console.error("Lỗi kiểm tra thanh toán:", error);

      const waitingText = document.getElementById("paymentWaitingText");
      if (waitingText) {
        waitingText.textContent = `Lỗi kiểm tra thanh toán: ${error}`;
      }
    }
  }, 2000);
}
function getMovieById(id) {
  return movies.find((item) => Number(item.id) === Number(id));
}

function fakeRating(movie) {
  const seed = Number(movie.id || 1);
  const rating = 7 + ((seed * 7) % 26) / 10;
  return Math.min(rating, 9.6).toFixed(1);
}

function fakeAgeLabel(movie) {
  const genre = (movie.genre || "").toLowerCase();

  if (genre.includes("kinh") || genre.includes("ma") || genre.includes("hành")) {
    return "T18";
  }

  if (genre.includes("tình") || genre.includes("tâm")) {
    return "T16";
  }

  return "T13";
}

function movieCard(movie) {
  return `
    <article class="movie-card">
      <div class="poster" onclick="showDetail(${movie.id})">
        ${
          movie.image
            ? `<img src="${movie.image}" alt="${movie.name}">`
            : `<div></div>`
        }

        <div class="rating-badge">★ ${fakeRating(movie)}</div>
        <div class="age-badge">${fakeAgeLabel(movie)}</div>
      </div>

      <div class="movie-info">
        <h3 onclick="showDetail(${movie.id})">${movie.name}</h3>
      </div>
    </article>
  `;
}

function renderMovies(data, resetVisible = true) {
  const grid = document.getElementById("movieGrid");
  currentMovieList = Array.isArray(data) ? data : [];

  if (resetVisible) {
    visibleMovieCount = MOVIES_PER_PAGE;
  }

  if (!currentMovieList.length) {
    grid.innerHTML = "<p>Không tìm thấy phim phù hợp.</p>";
    updateLoadMoreButton();
    return;
  }

  const visibleMovies = currentMovieList.slice(0, visibleMovieCount);
  grid.innerHTML = visibleMovies.map(movieCard).join("");

  updateLoadMoreButton();
}

function updateLoadMoreButton() {
  const btn = document.getElementById("loadMoreMoviesBtn");
  if (!btn) return;

  btn.classList.toggle("hidden", currentMovieList.length <= visibleMovieCount);
}

function showMoreMovies() {
  visibleMovieCount += MOVIES_PER_PAGE;
  renderMovies(currentMovieList, false);
}

function fillQuickBooking(data) {
  const quickMovie = document.getElementById("quickMovie");
  quickMovie.innerHTML = `<option value="">1 Chọn phim</option>`;

  data.forEach((movie) => {
    const option = document.createElement("option");
    option.value = movie.id;
    option.textContent = movie.name;
    quickMovie.appendChild(option);
  });
}

function fillQuickDates(movie) {
  const quickDate = document.getElementById("quickDate");
  const dates = (movie?.show_dates || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  quickDate.innerHTML = `<option value="">3 Chọn ngày</option>`;

  dates.forEach((date) => {
    const option = document.createElement("option");
    option.value = date;
    option.textContent = date;
    quickDate.appendChild(option);
  });
}

function fillQuickTimes(movie) {
  const quickTime = document.getElementById("quickTime");
  const times = (movie?.show_times || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  quickTime.innerHTML = `<option value="">4 Chọn suất</option>`;

  times.forEach((time) => {
    const option = document.createElement("option");
    option.value = time;
    option.textContent = time;
    quickTime.appendChild(option);
  });
}

async function loadMovies() {
  try {
    movies = await window.pywebview.api.get_movies();
    renderMovies(movies);
    fillQuickBooking(movies);
  } catch (error) {
    console.error("Lỗi loadMovies:", error);

    document.getElementById("movieGrid").innerHTML =
      `<p style="color:red">Không tải được danh sách phim: ${error}</p>`;
  }
}

async function doSearch() {
  const keyword = document.getElementById("searchInput").value.trim();

  if (!keyword) {
    renderMovies(movies);
    return;
  }

  const result = await window.pywebview.api.search_movies(keyword);
  renderMovies(result);
}

function resetSearch() {
  document.getElementById("searchInput").value = "";
  renderMovies(movies);
}

function showDetail(id) {
  const movie = getMovieById(id);
  if (!movie) return;

  document.getElementById("detailImage").src = movie.image || "";
  document.getElementById("detailTitle").textContent = movie.name;
  document.getElementById("detailGenre").textContent = movie.genre || "Chưa cập nhật";
  document.getElementById("detailDuration").textContent = `${movie.duration || 0} phút`;
  document.getElementById("detailDirector").textContent = movie.director || "Chưa cập nhật";
  document.getElementById("detailActors").textContent = movie.actors || "Chưa cập nhật";
  document.getElementById("detailTimes").textContent = movie.show_times || "Chưa có";
  document.getElementById("detailPrice").textContent = formatMoney(movie.price);
  document.getElementById("detailDescription").textContent = movie.description || "Chưa có mô tả.";

  const dates = (movie.show_dates || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  const dateBox = document.getElementById("detailDates");

  if (!dates.length) {
    dateBox.innerHTML = `<span class="date-pill">Chưa có lịch chiếu</span>`;
  } else {
    dateBox.innerHTML = dates
      .map((date) => `<span class="date-pill">${date}</span>`)
      .join("");
  }

  document.getElementById("detailBuyBtn").onclick = () => startBooking(movie.id);
  document.getElementById("detailModal").classList.remove("hidden");
}

function closeDetail() {
  document.getElementById("detailModal").classList.add("hidden");
}

async function loadBookedSeats() {
  if (!bookingMovie) {
    bookedSeats = [];
    return;
  }

  const showDate = document.getElementById("bookingDate").value;
  const showTime = document.getElementById("bookingTime").value;

  if (!showDate || !showTime) {
    bookedSeats = [];
    return;
  }

  bookedSeats = await window.pywebview.api.get_booked_seats(
  bookingMovie.name,
  showDate,
  showTime,
  bookingCinema || "CineGO Hà Nội"
  );
}

async function startBooking(id, preset = {}) {
   if (!requireLogin()) return;

  const movie = getMovieById(id);
  if (!movie) return;

  bookingMovie = movie;
selectedSeats = [];

const cashPayment = document.querySelector('input[name="paymentMethod"][value="cash"]');
if (cashPayment) {
  cashPayment.checked = true;
}
  bookingCinema =
  preset.cinema ||
  document.getElementById("quickCinema")?.value ||
  "CineGO Hà Nội";
  document.getElementById("bookingTitle").textContent = `Đặt vé - ${movie.name}`;
  document.getElementById("bookingSub").textContent =
  `${bookingCinema} • ${movie.genre || "Phim"} • ${movie.duration || 0} phút • ${formatMoney(movie.price)}`;

  fillBookingSelects(movie);
  if (preset.showDate) {
  document.getElementById("bookingDate").value = preset.showDate;
}

if (preset.showTime) {
  document.getElementById("bookingTime").value = preset.showTime;
}
  await loadBookedSeats();
  renderSeats();
  updateBookingTotal();

  closeDetail();
  document.getElementById("bookingModal").classList.remove("hidden");
}

function closeBooking() {
  document.getElementById("bookingModal").classList.add("hidden");
}

function fillBookingSelects(movie) {
  const dateSelect = document.getElementById("bookingDate");
  const timeSelect = document.getElementById("bookingTime");

  const dates = (movie.show_dates || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  const times = (movie.show_times || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  dateSelect.innerHTML = dates.length
    ? dates.map((date) => `<option value="${date}">${date}</option>`).join("")
    : `<option value="">Chưa có ngày chiếu</option>`;

  timeSelect.innerHTML = times.length
    ? times.map((time) => `<option value="${time}">${time}</option>`).join("")
    : `<option value="">Chưa có suất chiếu</option>`;
}

function renderSeats() {
  const grid = document.getElementById("seatGrid");
  grid.innerHTML = "";

  for (let row = 0; row < 5; row++) {
    const rowName = String.fromCharCode(65 + row);

    const rowLabel = document.createElement("div");
    rowLabel.className = "row-label";
    rowLabel.textContent = rowName;
    grid.appendChild(rowLabel);

    for (let col = 1; col <= 8; col++) {
      const seatCode = `${rowName}${col}`;
      const btn = document.createElement("button");

      btn.className = "seat";
      btn.textContent = seatCode;

      if (bookedSeats.includes(seatCode)) {
        btn.classList.add("is-booked");
        btn.disabled = true;
      } else {
        btn.addEventListener("click", () => toggleSeat(seatCode, btn));
      }

      grid.appendChild(btn);
    }
  }
}

function toggleSeat(seatCode, button) {
  if (selectedSeats.includes(seatCode)) {
    selectedSeats = selectedSeats.filter((seat) => seat !== seatCode);
    button.classList.remove("is-selected");
  } else {
    selectedSeats.push(seatCode);
    button.classList.add("is-selected");
  }

  updateBookingTotal();
}

function updateBookingTotal() {
  const total = getBookingTotal();
  document.getElementById("bookingTotal").textContent = formatMoney(total);
  updatePaymentBox();
}

function scrollToMovies() {
  document.getElementById("movieSection").scrollIntoView({ behavior: "smooth" });
}

function bindClick(id, handler) {
  const el = document.getElementById(id);
  if (el) el.addEventListener("click", handler);
}

function bindChange(id, handler) {
  const el = document.getElementById(id);
  if (el) el.addEventListener("change", handler);
}

function bindEvents() {
  bindClick("loadMoreMoviesBtn", showMoreMovies);
  bindClick("searchBtn", doSearch);
  bindClick("resetBtn", resetSearch);
  bindClick("moviesBtn", scrollToMovies);
  bindClick("loginOpenBtn", openLogin);
  bindClick("logoutBtn", logout);
  bindClick("submitAuthBtn", submitAuth);
  bindClick("contentAdminBtn", openContentAdmin);
  bindClick("newContentBtn", clearContentForm);
  bindClick("clearContentFormBtn", clearContentForm);
  bindClick("movieAdminBtn", openMovieAdmin);
  bindClick("newMovieBtn", clearMovieForm);
  bindClick("clearMovieFormBtn", clearMovieForm);

  bindClick("reviewTabBtn", () => setCinemaCornerTab("article_review"));
  bindClick("blogTabBtn", () => setCinemaCornerTab("article_blog"));

  bindClick("heroNextBtn", () => {
    nextHeroSlide();
    restartHeroTimer();
  });

  bindClick("heroPrevBtn", () => {
    prevHeroSlide();
    restartHeroTimer();
  });

  document.querySelectorAll('input[name="paymentMethod"]').forEach((input) => {
    input.addEventListener("change", updatePaymentBox);
  });

  const movieForm = document.getElementById("movieForm");
  if (movieForm) {
    movieForm.addEventListener("submit", saveMovie);
  }

  const movieIsHot = document.getElementById("movieIsHot");
  if (movieIsHot) {
    movieIsHot.addEventListener("change", () => {
      document.getElementById("movieBannerField").classList.toggle(
        "hidden",
        !movieIsHot.checked
      );
    });
  }

  document.querySelectorAll(".content-tab").forEach((tab) => {
    tab.addEventListener("click", () => setContentCategory(tab.dataset.category));
  });

  const contentForm = document.getElementById("contentForm");
  if (contentForm) {
    contentForm.addEventListener("submit", saveContentItem);
  }

  bindClick("switchAuthBtn", () => {
    setAuthMode(authMode === "login" ? "register" : "login");
  });

  bindClick("focusSearchBtn", () => {
    document.getElementById("searchInput").focus();
  });

  bindClick("buyTicketBtn", () => {
    document.querySelector(".quick-booking").scrollIntoView({
      behavior: "smooth",
      block: "center"
    });
  });

  bindChange("quickMovie", (event) => {
    const movie = getMovieById(event.target.value);
    fillQuickDates(movie);
    fillQuickTimes(movie);
  });

  bindClick("quickBuyBtn", () => {
    const movieId = document.getElementById("quickMovie").value;
    const cinema = document.getElementById("quickCinema").value;
    const showDate = document.getElementById("quickDate").value;
    const showTime = document.getElementById("quickTime").value;

    if (!movieId) {
      alert("Vui lòng chọn phim trước.");
      return;
    }

    if (!cinema) {
      alert("Vui lòng chọn rạp.");
      return;
    }

    if (!showDate) {
      alert("Vui lòng chọn ngày chiếu.");
      return;
    }

    if (!showTime) {
      alert("Vui lòng chọn suất chiếu.");
      return;
    }

    startBooking(movieId, {
      cinema,
      showDate,
      showTime
    });
  });

  bindClick("offersBtn", () => openContentView("offer"));
  bindClick("cinemaBtn", () => openContentView("cinema"));
  bindClick("specialBtn", () => openContentView("special"));

  bindChange("bookingDate", async () => {
    selectedSeats = [];
    await loadBookedSeats();
    renderSeats();
    updateBookingTotal();
  });

  bindChange("bookingTime", async () => {
    selectedSeats = [];
    await loadBookedSeats();
    renderSeats();
    updateBookingTotal();
  });

  bindClick("continuePaymentBtn", async () => {
  if (!bookingMovie) return;

  if (!selectedSeats.length) {
    alert("Vui lòng chọn ghế trước khi thanh toán.");
    return;
  }

  const paymentMethod = getSelectedPaymentMethod();
  const method = paymentMethodLabel(paymentMethod);

  if (paymentMethod === "bank") {
    startPaymentPolling();
    return;
  }

  await completeBookingAfterPayment(method);
});
}

async function initApp() {
  if (appInitialized) return;
  appInitialized = true;
  updateAccountUI();

  let tries = 0;

  while ((!window.pywebview || !window.pywebview.api) && tries < 20) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    tries++;
  }

  bindEvents();
  await loadMovies();
  renderHero();
  restartHeroTimer();
  await renderHomePromos();
  await renderCinemaCorner();
}
window.addEventListener("pywebviewready", initApp);
loadCinemaCorner("article_review");
document.addEventListener("DOMContentLoaded", initApp);
setTimeout(initApp, 1000);
async function openTickets() {
  const list = document.getElementById("ticketsList");
  list.innerHTML = `<p>Đang tải vé...</p>`;

  document.getElementById("ticketsModal").classList.remove("hidden");

  try {
    if (!requireLogin()) return;

    const tickets = await window.pywebview.api.get_my_tickets(currentUser.id);


    if (!tickets.length) {
      list.innerHTML = `<p>Bạn chưa có vé nào.</p>`;
      return;
    }

    list.innerHTML = tickets.map((ticket) => `
      <article class="ticket-card">
        <div>
          <span class="ticket-code">${ticket.ticket_code}</span>
          <h3>${ticket.movie_name}</h3>
          <p>Rạp: <strong>${ticket.cinema || "Chưa chọn rạp"}</strong></p>
          <p>Ngày chiếu: <strong>${ticket.show_date}</strong></p>
          <p>Suất chiếu: <strong>${ticket.show_time || "Chưa có"}</strong></p>
          <p>Ghế: <strong>${ticket.seats}</strong></p>
          <p>Thanh toán: <strong>${ticket.method}</strong></p>
          <p>Trạng thái: <strong>${ticket.status}</strong></p>
        </div>

        <div class="ticket-price">
          <span>Tổng tiền</span>
          <strong>${formatMoney(ticket.total)}</strong>
          <small>${ticket.created_at || ""}</small>
        </div>
      </article>
    `).join("");
  } catch (error) {
    list.innerHTML = `<p style="color:red">Không tải được vé: ${error}</p>`;
  }
}

function closeTickets() {
  document.getElementById("ticketsModal").classList.add("hidden");
}
function updateAccountUI() {
  const name = document.getElementById("accountName");
  const sub = document.getElementById("accountSub");
  const loginBtn = document.getElementById("loginOpenBtn");
  const logoutBtn = document.getElementById("logoutBtn");

  if (!name || !sub) return;

  if (currentUser) {
    name.textContent = currentUser.username;
    sub.textContent = currentUser.role === "admin" ? "Admin" : "0 Stars";
    loginBtn.classList.add("hidden");
    logoutBtn.classList.remove("hidden");
  } else {
    name.textContent = "Khách";
    sub.textContent = "0 Stars";
    loginBtn.classList.remove("hidden");
    logoutBtn.classList.add("hidden");
  }
    const adminBtn = document.getElementById("contentAdminBtn");

  if (adminBtn) {
    adminBtn.classList.toggle(
      "hidden",
      !currentUser || currentUser.role !== "admin"
    );
  }
    const movieAdminBtn = document.getElementById("movieAdminBtn");

  if (movieAdminBtn) {
    movieAdminBtn.classList.toggle(
      "hidden",
      !currentUser || currentUser.role !== "admin"
    );
  }

}

function openLogin() {
  document.getElementById("loginModal").classList.remove("hidden");
}

function closeLogin() {
  document.getElementById("loginModal").classList.add("hidden");
}

function setAuthMode(mode) {
  authMode = mode;

  const isRegister = authMode === "register";

  document.getElementById("authTitle").textContent = isRegister ? "Đăng ký" : "Đăng nhập";
  document.getElementById("authSubtitle").textContent = isRegister
    ? "Tạo tài khoản để đặt vé."
    : "Đăng nhập để đặt vé và xem vé đã mua.";

  document.getElementById("registerExtra").classList.toggle("hidden", !isRegister);
  document.getElementById("submitAuthBtn").textContent = isRegister ? "Đăng ký" : "Đăng nhập";
  document.getElementById("switchAuthBtn").textContent = isRegister
    ? "Đã có tài khoản? Đăng nhập"
    : "Chưa có tài khoản? Đăng ký";

  document.getElementById("authMessage").textContent = "";
}

async function submitAuth() {
  const username = document.getElementById("authUsername").value.trim();
  const password = document.getElementById("authPassword").value.trim();
  const email = document.getElementById("authEmail").value.trim();
  const phone = document.getElementById("authPhone").value.trim();
  const msg = document.getElementById("authMessage");

  if (authMode === "login") {
    const result = await window.pywebview.api.login(username, password);

    if (!result.ok) {
      msg.textContent = result.message;
      return;
    }

    currentUser = result.user;
    localStorage.setItem("cinego_user", JSON.stringify(currentUser));

    updateAccountUI();
    closeLogin();
    return;
  }

  const result = await window.pywebview.api.register({
    username,
    password,
    email,
    phone
  });

  if (!result.ok) {
    msg.textContent = result.message;
    return;
  }

  alert("Đăng ký thành công. Hãy đăng nhập.");
  setAuthMode("login");
}
// ------------------------------------------------------------------ //
//  Góc điện ảnh — load từ database thay vì hardcode
// ------------------------------------------------------------------ //

let currentArticleCategory = "article_review";

async function loadCinemaCorner(category) {
    currentArticleCategory = category;

    const featured = document.getElementById("featuredArticle");
    const featuredImg = document.getElementById("featuredArticleImg");
    const featuredTitle = document.getElementById("featuredArticleTitle");
    const featuredDesc = document.getElementById("featuredArticleDesc");
    const articleList = document.getElementById("articleList");

    if (!featured || !articleList) return;

    // Hiện trạng thái loading
    featuredTitle.textContent = "Đang tải...";
    articleList.innerHTML = "";

    try {
        const items = await window.pywebview.api.get_content_items(category);

        if (!items || items.length === 0) {
            featuredTitle.textContent = "Chưa có bài viết nào.";
            featuredImg.style.backgroundImage = "";
            featuredDesc.textContent = "";
            return;
        }

        // Bài đầu tiên làm featured
        const first = items[0];
        featuredTitle.textContent = first.title || "";
        featuredDesc.textContent = first.subtitle || first.description || "";
        if (first.image) {
            featuredImg.style.backgroundImage = `url('${first.image}')`;
            featuredImg.style.backgroundSize = "cover";
            featuredImg.style.backgroundPosition = "center";
        } else {
            featuredImg.style.backgroundImage = "";
        }

        // Các bài còn lại hiện trong danh sách
        articleList.innerHTML = "";
        items.slice(1).forEach((item, index) => {
            const article = document.createElement("article");

            const thumb = document.createElement("div");
            thumb.className = `thumb thumb-${index + 1}`;
            if (item.image) {
                thumb.style.backgroundImage = `url('${item.image}')`;
                thumb.style.backgroundSize = "cover";
                thumb.style.backgroundPosition = "center";
            }

            const info = document.createElement("div");

            const title = document.createElement("h3");
            title.textContent = item.title || "";

            const desc = document.createElement("span");
            desc.textContent = item.subtitle || item.description || "";

            info.appendChild(title);
            info.appendChild(desc);
            article.appendChild(thumb);
            article.appendChild(info);
            articleList.appendChild(article);
        });

    } catch (err) {
        featuredTitle.textContent = "Không thể tải bài viết.";
        console.error("loadCinemaCorner error:", err);
    }
}

// Gắn sự kiện cho 2 tab Bình luận / Blog
bindClick("reviewTabBtn", () => {
    document.getElementById("reviewTabBtn").classList.add("active");
    document.getElementById("blogTabBtn").classList.remove("active");
    loadCinemaCorner("article_review");
});

bindClick("blogTabBtn", () => {
    document.getElementById("blogTabBtn").classList.add("active");
    document.getElementById("reviewTabBtn").classList.remove("active");
    loadCinemaCorner("article_blog");
});
function logout() {
    currentUser = null;
    localStorage.removeItem("cinego_user");
    // Thêm 2 dòng này để xóa form đăng nhập
    document.getElementById("authUsername").value = "";
    document.getElementById("authPassword").value = "";
    updateAccountUI();
}
function requireLogin() {
  if (currentUser) return true;

  openLogin();
  return false;
}

bindClick("myTicketsBtn", openTickets);
function categoryName(category) {
  const names = {
    offer: "Ưu đãi",
    event: "Sự kiện",
    cinema: "Rạp phim",
    special: "Rạp đặc biệt",
    article_review: "Bình luận phim",
    article_blog: "Blog điện ảnh"
  };

  return names[category] || "Nội dung";
}

async function loadContentItems(category = null) {
  contentItems = await window.pywebview.api.get_content_items(category);
  return contentItems;
}

async function renderHomePromos() {
  const grid = document.getElementById("promoGrid");
  if (!grid) return;

  const offers = await window.pywebview.api.get_content_items("offer");
  const activeOffers = offers.filter((item) => item.status !== "hidden");

  if (!activeOffers.length) {
    grid.innerHTML = `
      <article class="promo-card blue">
        <h3>Thứ Ba vui vẻ</h3>
        <p>Vé chỉ từ 45K cho thành viên.</p>
      </article>

      <article class="promo-card navy">
        <h3>Quyền lợi thành viên</h3>
        <p>Tích điểm đổi quà, nhận ưu đãi riêng.</p>
      </article>

      <article class="promo-card lime">
        <h3>Combo bắp nước</h3>
        <p>Ưu đãi combo khi đặt vé online.</p>
      </article>

      <article class="promo-card mint">
        <h3>Thanh toán online</h3>
        <p>Đặt vé nhanh, không cần xếp hàng.</p>
      </article>
    `;
    return;
  }

  grid.innerHTML = activeOffers.slice(0, 4).map((item) => `
    <article class="promo-card promo-card-dynamic" onclick="openContentDetail(${item.id}, 'offer')">
      ${
        item.image
          ? `<img class="promo-thumb" src="${item.image}" alt="${item.title}">`
          : `<div class="promo-thumb-placeholder"></div>`
      }

      <div class="promo-card-body">
        <h3>${item.title}</h3>
        <p>${item.subtitle || "Xem chi tiết ưu đãi"}</p>
      </div>
    </article>
  `).join("");
}
function openContentAdmin() {
  if (!currentUser || currentUser.role !== "admin") {
    alert("Chỉ admin mới được dùng chức năng này.");
    return;
  }

  document.getElementById("contentAdminModal").classList.remove("hidden");
  setContentCategory(currentContentCategory);
}

function closeContentAdmin() {
  document.getElementById("contentAdminModal").classList.add("hidden");
}

async function setContentCategory(category) {
  currentContentCategory = category;

  document.querySelectorAll(".content-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.category === category);
  });

  document.getElementById("contentCategory").value = category;

  await renderAdminContentList();
}

async function renderAdminContentList() {
  const list = document.getElementById("adminContentList");
  list.innerHTML = `<p>Đang tải...</p>`;

  const items = await window.pywebview.api.get_content_items(currentContentCategory);

  if (!items.length) {
    list.innerHTML = `<p>Chưa có ${categoryName(currentContentCategory).toLowerCase()} nào.</p>`;
    return;
  }

  list.innerHTML = items.map((item) => `
    <article class="admin-content-card">
      ${
        item.image
          ? `<img src="${item.image}" alt="${item.title}">`
          : `<img alt="">`
      }

      <div>
        <h4>${item.title}</h4>
        <p>${item.subtitle || "Không có dòng phụ"}</p>
        <p>Trạng thái: ${item.status === "hidden" ? "Ẩn" : "Hiển thị"}</p>
      </div>

      <div class="admin-content-actions">
        <button class="edit-content-btn" onclick="editContentItem(${item.id})">Sửa</button>
        <button class="delete-content-btn" onclick="removeContentItem(${item.id})">Xóa</button>
      </div>
    </article>
  `).join("");
}

async function editContentItem(id) {
  const items = await window.pywebview.api.get_content_items(currentContentCategory);
  const item = items.find((content) => Number(content.id) === Number(id));

  if (!item) return;

  editingContentId = item.id;

  document.getElementById("contentFormTitle").textContent = "Sửa nội dung";
  document.getElementById("contentCategory").value = item.category;
  document.getElementById("contentTitle").value = item.title || "";
  document.getElementById("contentSubtitle").value = item.subtitle || "";
  document.getElementById("contentImagePath").value = item.image_path || "";
  document.getElementById("contentStatus").value = item.status || "active";
  document.getElementById("contentDescription").value = item.description || "";
  document.getElementById("contentMessage").textContent = "";
}

function clearContentForm() {
  editingContentId = null;

  document.getElementById("contentFormTitle").textContent = "Thêm nội dung";
  document.getElementById("contentCategory").value = currentContentCategory;
  document.getElementById("contentTitle").value = "";
  document.getElementById("contentSubtitle").value = "";
  document.getElementById("contentImagePath").value = "";
  document.getElementById("contentStatus").value = "active";
  document.getElementById("contentDescription").value = "";
  document.getElementById("contentMessage").textContent = "";
}

async function saveContentItem(event) {
  event.preventDefault();

  const data = {
    id: editingContentId,
    category: document.getElementById("contentCategory").value,
    title: document.getElementById("contentTitle").value.trim(),
    subtitle: document.getElementById("contentSubtitle").value.trim(),
    image_path: document.getElementById("contentImagePath").value.trim(),
    status: document.getElementById("contentStatus").value,
    description: document.getElementById("contentDescription").value.trim()
  };

  const msg = document.getElementById("contentMessage");

  const result = editingContentId
    ? await window.pywebview.api.update_content_item(data)
    : await window.pywebview.api.add_content_item(data);

  if (!result.ok) {
    msg.textContent = result.message || "Không thể lưu nội dung";
    return;
  }

  currentContentCategory = data.category;
  clearContentForm();
  await setContentCategory(currentContentCategory);
  await renderHomePromos();
}

async function removeContentItem(id) {
  if (!confirm("Bạn chắc chắn muốn xóa nội dung này?")) return;

  const result = await window.pywebview.api.delete_content_item(id);

  if (!result.ok) {
    alert(result.message || "Không thể xóa nội dung");
    return;
  }

  clearContentForm();
  await renderAdminContentList();
  await renderHomePromos();
}

async function openContentView(category) {
  const list = document.getElementById("contentViewList");
  const title = document.getElementById("contentViewTitle");
  const sub = document.getElementById("contentViewSub");

  title.textContent = categoryName(category);
  sub.textContent = `Danh sách ${categoryName(category).toLowerCase()} đang hiển thị.`;
  list.innerHTML = `<p>Đang tải...</p>`;

  document.getElementById("contentViewModal").classList.remove("hidden");

  const items = await window.pywebview.api.get_content_items(category);
  const activeItems = items.filter((item) => item.status !== "hidden");

  if (!activeItems.length) {
    list.innerHTML = `<p>Chưa có nội dung nào.</p>`;
    return;
  }

  list.innerHTML = activeItems.map((item) => `
    <button class="content-list-row" onclick="openContentDetail(${item.id}, '${category}')">
      ${
        item.image
          ? `<img src="${item.image}" alt="${item.title}">`
          : `<span class="content-row-placeholder"></span>`
      }

      <span>${item.title}</span>
    </button>
  `).join("");
}
async function openContentDetail(id, category) {
  const list = document.getElementById("contentViewList");
  const title = document.getElementById("contentViewTitle");
  const sub = document.getElementById("contentViewSub");
  document.getElementById("contentViewModal").classList.remove("hidden");
  const items = await window.pywebview.api.get_content_items(category);
  const item = items.find((content) => Number(content.id) === Number(id));

  if (!item) return;

  title.textContent = item.title;
  sub.textContent = item.subtitle || categoryName(category);

  list.innerHTML = `
    <article class="content-detail-page">
      ${
        item.image
          ? `<img src="${item.image}" alt="${item.title}">`
          : `<div class="content-detail-placeholder"></div>`
      }

      <div class="content-detail-body">
        <h3>${item.title}</h3>
        ${
          item.subtitle
            ? `<p class="content-detail-subtitle">${item.subtitle}</p>`
            : ""
        }
        <p class="content-detail-description">${item.description || "Chưa có mô tả chi tiết."}</p>


        <button class="outline-btn" onclick="openContentView('${category}')">← Quay lại</button>
      </div>
    </article>
  `;
}

function closeContentView() {
  document.getElementById("contentViewModal").classList.add("hidden");
}
function openMovieAdmin() {
  if (!currentUser || currentUser.role !== "admin") {
    alert("Chỉ admin mới được dùng chức năng này.");
    return;
  }

  document.getElementById("movieAdminModal").classList.remove("hidden");
  renderAdminMovieList();
}

function closeMovieAdmin() {
  document.getElementById("movieAdminModal").classList.add("hidden");
}

function renderAdminMovieList() {
  const list = document.getElementById("adminMovieList");

  if (!movies.length) {
    list.innerHTML = `<p>Chưa có phim nào.</p>`;
    return;
  }

  list.innerHTML = movies.map((movie) => `
    <article class="admin-movie-card">
      ${
        movie.image
          ? `<img src="${movie.image}" alt="${movie.name}">`
          : `<img alt="">`
      }

      <div>
        <h4>${movie.name}</h4>
        <p>${movie.genre || "Chưa có thể loại"}</p>
        <p>${movie.duration || 0} phút • ${formatMoney(movie.price)}</p>
        <p>Ngày: ${movie.show_dates || "Chưa có"}</p>
        <p>Suất: ${movie.show_times || "Chưa có"}</p>
        <p>Loại: ${movieStatusName(movie.movie_status)} ${Number(movie.is_hot || 0) === 1 ? "• Hot banner" : ""}</p>
      </div>

      <div class="admin-movie-actions">
        <button class="edit-movie-btn" onclick="editMovie(${movie.id})">Sửa</button>
        <button class="delete-movie-btn" onclick="removeMovie(${movie.id})">Xóa</button>
      </div>
    </article>
  `).join("");
}

function clearMovieForm() {
  editingMovieId = null;

  document.getElementById("movieFormTitle").textContent = "Thêm phim";
  document.getElementById("movieId").value = "";
  document.getElementById("movieName").value = "";
  document.getElementById("movieGenre").value = "";
  document.getElementById("movieDuration").value = "";
  document.getElementById("moviePrice").value = "";
  document.getElementById("movieDirector").value = "";
  document.getElementById("movieActors").value = "";
  document.getElementById("movieDates").value = "";
  document.getElementById("movieTimes").value = "";
  document.getElementById("movieStatus").value = "now_showing";
document.getElementById("movieIsHot").checked = false;
  document.getElementById("movieImagePath").value = "";
  document.getElementById("movieDescription").value = "";
  document.getElementById("movieMessage").textContent = "";
  document.getElementById("movieBannerImagePath").value = "";
document.getElementById("movieBannerField").classList.add("hidden");
}

function editMovie(id) {
  const movie = getMovieById(id);
  if (!movie) return;

  editingMovieId = movie.id;

  document.getElementById("movieFormTitle").textContent = "Sửa phim";
  document.getElementById("movieId").value = movie.id;
  document.getElementById("movieName").value = movie.name || "";
  document.getElementById("movieGenre").value = movie.genre || "";
  document.getElementById("movieDuration").value = movie.duration || "";
  document.getElementById("moviePrice").value = movie.price || "";
  document.getElementById("movieDirector").value = movie.director || "";
  document.getElementById("movieActors").value = movie.actors || "";
  document.getElementById("movieDates").value = movie.show_dates || "";
  document.getElementById("movieTimes").value = movie.show_times || "";
  document.getElementById("movieStatus").value = movie.movie_status || "now_showing";
document.getElementById("movieIsHot").checked = Number(movie.is_hot || 0) === 1;
  document.getElementById("movieImagePath").value = movie.image_path || "";
  document.getElementById("movieDescription").value = movie.description || "";
  document.getElementById("movieMessage").textContent = "";
  document.getElementById("movieBannerImagePath").value = movie.banner_image_path || "";
document.getElementById("movieBannerField").classList.toggle(
  "hidden",
  Number(movie.is_hot || 0) !== 1
);
}

async function saveMovie(event) {
  event.preventDefault();

  const data = {
    id: editingMovieId,
    name: document.getElementById("movieName").value.trim(),
    genre: document.getElementById("movieGenre").value.trim(),
    duration: document.getElementById("movieDuration").value.trim(),
    price: document.getElementById("moviePrice").value.trim(),
    director: document.getElementById("movieDirector").value.trim(),
    actors: document.getElementById("movieActors").value.trim(),
    show_dates: document.getElementById("movieDates").value.trim(),
    show_times: document.getElementById("movieTimes").value.trim(),
    image_path: document.getElementById("movieImagePath").value.trim(),
    description: document.getElementById("movieDescription").value.trim(),
    movie_status: document.getElementById("movieStatus").value,
    banner_image_path: document.getElementById("movieBannerImagePath").value.trim(),
is_hot: document.getElementById("movieIsHot").checked
  };

  const msg = document.getElementById("movieMessage");

  const result = editingMovieId
    ? await window.pywebview.api.update_movie(data)
    : await window.pywebview.api.add_movie(data);

  if (!result.ok) {
    msg.textContent = result.message || "Không thể lưu phim";
    return;
  }

  clearMovieForm();
  await loadMovies();
  renderAdminMovieList();
  renderHero();
restartHeroTimer();
}

async function removeMovie(id) {
  if (!confirm("Bạn chắc chắn muốn xóa phim này?")) return;

  const result = await window.pywebview.api.delete_movie(id);

  if (!result.ok) {
    alert(result.message || "Không thể xóa phim");
    return;
  }

  clearMovieForm();
  await loadMovies();
  renderAdminMovieList();
  renderHero();
restartHeroTimer();
}
function movieStatusName(status) {
  const names = {
    now_showing: "Đang chiếu",
    coming_soon: "Sắp chiếu",
    imax: "Phim IMAX"
  };

  return names[status] || "Đang chiếu";
}
function renderHero() {
  const hero = document.getElementById("heroBanner");
  const dots = document.getElementById("heroDots");

  if (!hero || !dots) return;

  hotMovies = movies.filter((movie) => Number(movie.is_hot || 0) === 1);

  if (!hotMovies.length) {
    hotMovies = movies.slice(0, 5);
  }

  if (!hotMovies.length) {
    dots.innerHTML = "";
    return;
  }

  if (currentHeroIndex >= hotMovies.length) {
    currentHeroIndex = 0;
  }

  const movie = hotMovies[currentHeroIndex];
  const bannerImage = movie.banner_image || movie.image || "";

  if (bannerImage) {
    hero.style.backgroundImage = `url("${bannerImage}")`;
  }

  hero.onclick = () => showDetail(movie.id);

  dots.innerHTML = hotMovies.map((item, index) => `
    <i class="${index === currentHeroIndex ? "active" : ""}" onclick="setHeroSlide(${index})"></i>
  `).join("");
}
function setHeroSlide(index) {
  currentHeroIndex = index;
  renderHero();
  restartHeroTimer();
}

function nextHeroSlide() {
  if (!hotMovies.length) return;

  currentHeroIndex = (currentHeroIndex + 1) % hotMovies.length;
  renderHero();
}

function prevHeroSlide() {
  if (!hotMovies.length) return;

  currentHeroIndex = (currentHeroIndex - 1 + hotMovies.length) % hotMovies.length;
  renderHero();
}

function restartHeroTimer() {
  if (heroTimer) {
    clearInterval(heroTimer);
  }

  heroTimer = setInterval(nextHeroSlide, 4500);
}
async function renderCinemaCorner(category = "article_review") {
  const layout = document.getElementById("articleLayout");
  if (!layout) return;

  const items = await window.pywebview.api.get_content_items(category);
  const activeItems = items.filter((item) => item.status !== "hidden");

  if (!activeItems.length) {
    layout.innerHTML = `
      <article class="featured-article">
        <div class="article-image article-main-img"></div>
        <h3>Chưa có bài viết nào</h3>
        <div class="article-stats">
          <span>Admin có thể thêm bài trong mục Quản lý nội dung.</span>
        </div>
      </article>
    `;
    return;
  }

  const first = activeItems[0];
  const others = activeItems.slice(1, 4);

  layout.innerHTML = `
    <article class="featured-article article-clickable" onclick="openContentDetail(${first.id}, '${category}')">
      ${
        first.image
          ? `<img class="article-main-img" src="${first.image}" alt="${first.title}">`
          : `<div class="article-image article-main-img"></div>`
      }

      <h3>${first.title}</h3>

      <div class="article-stats">
        <span>👍 Thích</span>
        <span>👁 ${28 + Number(first.id || 0)}</span>
      </div>
    </article>

    <div class="article-list">
      ${others.map((item) => `
        <article class="article-clickable" onclick="openContentDetail(${item.id}, '${category}')">
          ${
            item.image
              ? `<img class="thumb" src="${item.image}" alt="${item.title}">`
              : `<div class="thumb"></div>`
          }

          <div>
            <h3>${item.title}</h3>
            <span>👁 ${90 + Number(item.id || 0)}</span>
          </div>
        </article>
      `).join("")}
    </div>
  `;
}

function setCinemaCornerTab(category) {
  document.getElementById("reviewTabBtn").classList.toggle("active", category === "article_review");
  document.getElementById("blogTabBtn").classList.toggle("active", category === "article_blog");

  renderCinemaCorner(category);
}
function openFooterPage(type) {
  const pages = {
    about: {
      title: "Về chúng tôi",
      body: "CineGo là ứng dụng đặt vé xem phim desktop, hỗ trợ xem phim đang chiếu, chọn suất chiếu, chọn ghế, thanh toán demo và quản lý vé đã mua."
    },
    terms: {
      title: "Thoả thuận sử dụng",
      body: "Người dùng cần cung cấp thông tin chính xác khi đăng ký, đặt vé và thanh toán. Dữ liệu trong đồ án được sử dụng cho mục đích mô phỏng hệ thống đặt vé xem phim."
    },
    privacy: {
      title: "Chính sách bảo mật",
      body: "CineGo lưu thông tin tài khoản, vé đã mua và lịch sử thanh toán trong cơ sở dữ liệu SQLite cục bộ. Mật khẩu và dữ liệu người dùng chỉ phục vụ cho đồ án demo."
    },
    feedback: {
      title: "Góp ý",
      body: "Người dùng có thể gửi góp ý về giao diện, chức năng đặt vé, thanh toán và trải nghiệm sử dụng để hệ thống được hoàn thiện hơn."
    },
    faq: {
      title: "FAQ",
      body: "Câu hỏi thường gặp:\n\n1. Có cần đăng nhập để đặt vé không?\nCó, người dùng cần đăng nhập trước khi đặt vé.\n\n2. Vé đã mua xem ở đâu?\nVào mục Vé của tôi.\n\n3. Thanh toán có phải thật không?\nHiện tại là thanh toán demo phục vụ đồ án."
    }
  };

  const page = pages[type];
  if (!page) return;

  document.getElementById("contentViewTitle").textContent = page.title;
  document.getElementById("contentViewSub").textContent = "Thông tin hệ thống CineGo";
  document.getElementById("contentViewList").innerHTML = `
    <article class="footer-page-content">
      <p>${page.body}</p>
    </article>
  `;

  document.getElementById("contentViewModal").classList.remove("hidden");
}