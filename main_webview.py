import os
import webview
import subprocess
import json
import urllib.error
import urllib.parse
import urllib.request
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --- Thay toàn bộ import từ database.db bằng các class model mới ---
from model.movie import Movie
from model.user import User
from model.booking import Booking
from database.db import (
    create_tables,
    get_content_items,
    add_content_item,
    update_content_item,
    delete_content_item,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
WEBHOOK_HOST = "127.0.0.1"
from hide.config import SEPAY_API_TOKEN, SEPAY_WEBHOOK_TOKEN, FILE_SERVER_PORT, WEBHOOK_PORT
SEPAY_API_URL = "https://userapi.sepay.vn/v2/transactions"
received_bank_transactions = []


def image_to_url(path):
    if not path:
        return ""
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)
    if not os.path.exists(path):
        return ""
    rel_path = os.path.relpath(path, BASE_DIR).replace("\\", "/")
    mtime = int(os.path.getmtime(path))
    return f"http://127.0.0.1:{FILE_SERVER_PORT}/{rel_path}?v={mtime}"

def movie_to_dict(movie: Movie):
    d = movie.to_dict()
    d["image"] = image_to_url(movie.image)
    d["banner_image"] = image_to_url(movie.banner_image)
    return d


def content_to_dict(item):
    return {
        "id": item[0],
        "category": item[1],
        "title": item[2],
        "subtitle": item[3],
        "description": item[4],
        "image": image_to_url(item[5]),
        "image_path": item[5],
        "status": item[6],
        "created_at": item[7],
    }


class SePayWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/sepay-webhook":
            self.send_response(404)
            self.end_headers()
            return

        if SEPAY_WEBHOOK_TOKEN:
            auth_header = self.headers.get("Authorization", "")
            if auth_header != SEPAY_WEBHOOK_TOKEN and auth_header != f"Bearer {SEPAY_WEBHOOK_TOKEN}":
                self.send_response(401)
                self.end_headers()
                return

        length = int(self.headers.get("Content-Length", 0))

        try:
            raw_body = self.rfile.read(length).decode("utf-8")
            data = json.loads(raw_body or "{}")
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        transfer_type = str(data.get("transferType") or "").lower()
        amount = int(float(data.get("transferAmount") or 0))
        content = str(data.get("content") or "").upper()
        reference_code = str(data.get("referenceCode") or data.get("id") or "")

        if transfer_type == "in" and amount > 0:
            received_bank_transactions.append({
                "reference_code": reference_code,
                "amount": amount,
                "content": content,
                "raw": data,
                "used": False
            })

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"success": true}')

    def log_message(self, format, *args):
        return


def start_sepay_webhook_server():
    server = ThreadingHTTPServer((WEBHOOK_HOST, WEBHOOK_PORT), SePayWebhookHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"SePay webhook server running at http://{WEBHOOK_HOST}:{WEBHOOK_PORT}/sepay-webhook")

def start_file_server():
    """
    HTTP server nhỏ serve file tĩnh từ BASE_DIR.
    Dùng SimpleHTTPRequestHandler có sẵn trong Python,
    không cần cài thêm thư viện gì.
    """
    import http.server

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=BASE_DIR, **kwargs)

        def log_message(self, format, *args):
            return  # tắt log để console không bị spam

    server = ThreadingHTTPServer(("127.0.0.1", FILE_SERVER_PORT), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"File server running at http://127.0.0.1:{FILE_SERVER_PORT}")
class Api:
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #

    def get_movies(self):
        return [movie_to_dict(m) for m in Movie.get_all()]

    def search_movies(self, keyword):
        # Trước: [movie_to_dict(m) for m in search_movies(keyword)]
        return [movie_to_dict(m) for m in Movie.search(keyword)]

    def add_movie(self, data):
        name = (data.get("name") or "").strip()
        genre = (data.get("genre") or "").strip()
        duration = data.get("duration")
        director = (data.get("director") or "").strip()
        actors = (data.get("actors") or "").strip()
        description = (data.get("description") or "").strip()
        image_path = (data.get("image_path") or "").strip()
        show_dates = (data.get("show_dates") or "").strip()
        show_times = (data.get("show_times") or "").strip()
        price = data.get("price")

        if not name or not genre or not duration or not show_dates or not show_times or not price:
            return {"ok": False, "message": "Vui lòng nhập đầy đủ tên phim, thể loại, thời lượng, ngày chiếu, suất chiếu và giá vé"}

        try:
            duration = int(duration)
            price = int(price)
            if duration <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            return {"ok": False, "message": "Thời lượng và giá vé phải là số nguyên dương"}

        # Trước: add_movie(name, genre, ...)
        # Sau:   Movie.create(name, genre, ...)
        Movie.create(
            name, genre, duration, director, actors, description,
            image_path, show_dates, show_times, price,
            data.get("movie_status") or "now_showing",
            1 if data.get("is_hot") else 0,
            data.get("banner_image_path") or ""
        )
        return {"ok": True, "message": "Đã thêm phim"}

    def update_movie(self, data):
        movie_id = data.get("id")
        name = (data.get("name") or "").strip()
        genre = (data.get("genre") or "").strip()
        duration = data.get("duration")
        director = (data.get("director") or "").strip()
        actors = (data.get("actors") or "").strip()
        description = (data.get("description") or "").strip()
        image_path = (data.get("image_path") or "").strip()
        show_dates = (data.get("show_dates") or "").strip()
        show_times = (data.get("show_times") or "").strip()
        price = data.get("price")

        if not movie_id:
            return {"ok": False, "message": "Thiếu ID phim"}

        if not name or not genre or not duration or not show_dates or not show_times or not price:
            return {"ok": False, "message": "Vui lòng nhập đầy đủ tên phim, thể loại, thời lượng, ngày chiếu, suất chiếu và giá vé"}

        try:
            duration = int(duration)
            price = int(price)
            if duration <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            return {"ok": False, "message": "Thời lượng và giá vé phải là số nguyên dương"}

        # Trước: update_movie(movie_id, name, genre, ...)
        # Sau:   Movie.update(movie_id, name, genre, ...)
        Movie.update(
            movie_id, name, genre, duration, director, actors, description,
            image_path, show_dates, show_times, price,
            data.get("movie_status") or "now_showing",
            1 if data.get("is_hot") else 0,
            data.get("banner_image_path") or ""
        )
        return {"ok": True, "message": "Đã cập nhật phim"}

    def delete_movie(self, movie_id):
        # Trước: delete_movie(movie_id)
        # Sau:   Movie.delete(movie_id)
        Movie.delete(movie_id)
        return {"ok": True, "message": "Đã xóa phim"}

    # ------------------------------------------------------------------ #
    #  Tài khoản — dùng User class thay vì hàm cũ
    # ------------------------------------------------------------------ #

    def login(self, username, password):
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            return {"ok": False, "message": "Vui lòng nhập tài khoản và mật khẩu"}

        # Trước: user = check_login(username, password) → so sánh SHA256 trong SQL
        # Sau:   User.authenticate() lấy user về rồi verify bcrypt
        user = User.authenticate(username, password)

        if not user:
            return {"ok": False, "message": "Sai tài khoản hoặc mật khẩu"}

        return {
            "ok": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }

    def register(self, data):
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()

        if not username or not password:
            return {"ok": False, "message": "Vui lòng nhập tài khoản và mật khẩu"}

        if len(password) < 6:
            return {"ok": False, "message": "Mật khẩu tối thiểu 6 ký tự"}

        if email and phone:
            return {"ok": False, "message": "Chỉ nhập email hoặc số điện thoại"}

        if not email and not phone:
            return {"ok": False, "message": "Vui lòng nhập email hoặc số điện thoại"}

        # Trước: add_user(username, password, email, phone)
        # Sau:   User.create(username, password, email, phone)
        if User.create(username, password, email or None, phone or None):
            return {"ok": True, "message": "Đăng ký thành công"}

        return {"ok": False, "message": "Tên tài khoản đã tồn tại"}

    # ------------------------------------------------------------------ #
    #  Đặt vé — dùng Booking class thay vì hàm cũ
    # ------------------------------------------------------------------ #

    def get_booked_seats(self, movie_name, show_date, show_time, cinema=None):
        # Trước: get_booked_seats(movie_name, show_date, show_time, cinema)
        return Booking.get_booked_seats(movie_name, show_date, show_time, cinema)

    def get_my_tickets(self, user_id=1):
        # Trước: get_payments(user_id) trả về tuple → phải truy cập pay[0], pay[1]...
        # Sau:   Booking.get_tickets_by_user() trả về list dict sẵn
        return Booking.get_tickets_by_user(user_id)

    def create_booking(self, data):
        user_id = data.get("user_id") or 1
        movie_name = data.get("movie_name")
        cinema = data.get("cinema") or "CineGO Hà Nội"
        show_date = data.get("show_date")
        show_time = data.get("show_time")
        seats = data.get("seats") or []
        total = data.get("total") or 0
        method = data.get("method") or "Demo"

        if not movie_name or not cinema or not show_date or not show_time or not seats:
            return {"ok": False, "message": "Thiếu thông tin đặt vé"}

        # Kiểm tra ghế đã bị đặt chưa
        booked = Booking.get_booked_seats(movie_name, show_date, show_time, cinema)
        duplicated = [seat for seat in seats if seat in booked]

        if duplicated:
            return {"ok": False, "message": "Ghế đã được đặt: " + ", ".join(duplicated)}

        # Trước: add_payment(...) rồi vòng for add_booking(...)
        # Sau:   Booking.create_payment() và Booking.add_seat()
        ticket_code = Booking.create_payment(
            user_id, movie_name, show_date, show_time,
            ", ".join(seats), total, method, cinema
        )

        for seat in seats:
            Booking.add_seat(user_id, movie_name, show_date, show_time, seat, cinema)

        return {"ok": True, "ticket_code": ticket_code}

    def get_admin_statistics(self):
        return Booking.get_statistics()

    def open_email_draft(self, subject, body, to=""):
        gmail_url = "https://mail.google.com/mail/?view=cm&fs=1"
        if to:
            gmail_url += "&to=" + urllib.parse.quote(to)
        gmail_url += "&su=" + urllib.parse.quote(subject or "")
        gmail_url += "&body=" + urllib.parse.quote(body or "")
        webbrowser.open(gmail_url)
        return {"ok": True, "message": "Đã mở Gmail để gửi vé"}
    # ------------------------------------------------------------------ #
    #  Thanh toán SePay — giữ nguyên, không liên quan OOP
    # ------------------------------------------------------------------ #

    def check_bank_payment(self, payment_code, total):
        payment_code = str(payment_code or "").upper().strip()
        total = int(total or 0)
        token = str(SEPAY_API_TOKEN or "").strip()

        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "", 1).strip()

        if not token:
            return {"ok": False, "message": "Chưa nhập SePay API token"}

        url = "https://userapi.sepay.vn/v2/transactions?per_page=20"

        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError:
            try:
                output = subprocess.check_output(
                    ["curl", "-s", "-X", "GET", url,
                     "-H", f"Authorization: Bearer {token}",
                     "-H", "Accept: application/json"],
                    text=True, timeout=10
                )
                data = json.loads(output)
            except Exception as error:
                return {"ok": False, "message": f"Lỗi gọi SePay bằng curl: {error}"}
        except Exception as error:
            return {"ok": False, "message": f"Lỗi gọi SePay API: {error}"}

        transactions = data.get("data", [])

        for transaction in transactions:
            amount = int(float(transaction.get("amount_in") or 0))
            content = str(
                transaction.get("transaction_content") or
                transaction.get("content") or ""
            ).upper()
            account_number = str(transaction.get("account_number") or "").upper()
            sub_account = str(
                transaction.get("sub_account") or
                transaction.get("subAccount") or ""
            ).upper()

            same_amount = amount == total
            same_code = payment_code in content
            same_account = (
                "96247CINEGO" in account_number or
                "96247CINEGO" in sub_account or
                "96247CINEGO" in content
            )

            # Bắt buộc khớp đúng nội dung chuyển khoản của vé hiện tại.
            # Không xác nhận chỉ vì giao dịch cũ cùng số tiền vào đúng tài khoản.
            if same_amount and same_code and same_account:
                return {"ok": True, "message": "Đã nhận thanh toán", "transaction": transaction}

        return {
            "ok": False,
            "message": f"Chưa thấy giao dịch {format(total, ',')}đ với nội dung {payment_code}"
        }

    # ------------------------------------------------------------------ #
    #  Nội dung (content_items) — giữ nguyên dùng hàm cũ từ db.py
    # ------------------------------------------------------------------ #

    def get_content_items(self, category=None):
        return [content_to_dict(item) for item in get_content_items(category)]

    def add_content_item(self, data):
        title = (data.get("title") or "").strip()
        category = (data.get("category") or "").strip()

        if not title or not category:
            return {"ok": False, "message": "Vui lòng nhập tiêu đề và loại nội dung"}

        add_content_item(
            category, title,
            data.get("subtitle") or "",
            data.get("description") or "",
            data.get("image_path") or "",
            data.get("status") or "active"
        )
        return {"ok": True, "message": "Đã thêm nội dung"}

    def update_content_item(self, data):
        item_id = data.get("id")
        title = (data.get("title") or "").strip()
        category = (data.get("category") or "").strip()

        if not item_id:
            return {"ok": False, "message": "Thiếu ID nội dung"}

        if not title or not category:
            return {"ok": False, "message": "Vui lòng nhập tiêu đề và loại nội dung"}

        update_content_item(
            item_id, category, title,
            data.get("subtitle") or "",
            data.get("description") or "",
            data.get("image_path") or "",
            data.get("status") or "active"
        )
        return {"ok": True, "message": "Đã cập nhật nội dung"}

    def delete_content_item(self, item_id):
        delete_content_item(item_id)
        return {"ok": True, "message": "Đã xóa nội dung"}


if __name__ == "__main__":
    create_tables()
    start_sepay_webhook_server()
    start_file_server()
    api = Api()
    index_path = os.path.join(WEB_DIR, "index.html")

    webview.create_window(
        "CineGO",
        index_path,
        js_api=api,
        width=1366,
        height=768,
        min_size=(1100, 700),
    )

    webview.start(debug=False)