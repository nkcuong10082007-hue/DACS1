import os
import base64
import mimetypes
import webview
from database.db import (
    create_tables,
    get_movies,
    search_movies,
    get_booked_seats,
    add_booking,
    add_payment,
    get_payments,
    add_user,
    check_login,
    get_content_items,
    add_content_item,
    update_content_item,
    delete_content_item,
    add_movie,
    update_movie,
    delete_movie,

)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")


def image_to_data_url(path):
    if not path:
        return ""

    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)

    if not os.path.exists(path):
        return ""

    mime, _ = mimetypes.guess_type(path)
    mime = mime or "image/jpeg"

    with open(path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


def movie_to_dict(movie):
    return {
        "id": movie[0],
        "name": movie[1],
        "genre": movie[2],
        "duration": movie[3],
        "director": movie[4],
        "actors": movie[5],
        "description": movie[6],
        "image": image_to_data_url(movie[7]),
        "image_path": movie[7],
        "show_dates": movie[8],
        "show_times": movie[9] if len(movie) > 9 else "",
        "price": movie[10] if len(movie) > 10 and movie[10] else 90000,
        "movie_status": movie[11] if len(movie) > 11 and movie[11] else "now_showing",
        "is_hot": movie[12] if len(movie) > 12 else 0,
        "banner_image": image_to_data_url(movie[13]) if len(movie) > 13 else "",
        "banner_image_path": movie[13] if len(movie) > 13 else "",
    }


def content_to_dict(item):
    return {
        "id": item[0],
        "category": item[1],
        "title": item[2],
        "subtitle": item[3],
        "description": item[4],
        "image": image_to_data_url(item[5]),
        "image_path": item[5],
        "status": item[6],
        "created_at": item[7],
    }


class Api:
    def get_movies(self):
        data = [movie_to_dict(movie) for movie in get_movies()]

        return data

    def get_content_items(self, category=None):
        return [content_to_dict(item) for item in get_content_items(category)]

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
            return {
                "ok": False,
                "message": "Vui lòng nhập đầy đủ tên phim, thể loại, thời lượng, ngày chiếu, suất chiếu và giá vé"
            }

        try:
            duration = int(duration)
            price = int(price)

            if duration <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            return {
                "ok": False,
                "message": "Thời lượng và giá vé phải là số nguyên dương"
            }

        add_movie(
            name,
            genre,
            duration,
            director,
            actors,
            description,
            image_path,
            show_dates,
            show_times,
            price,
            data.get("movie_status") or "now_showing",
            1 if data.get("is_hot") else 0,
            data.get("banner_image_path") or ""
        )

        return {
            "ok": True,
            "message": "Đã thêm phim"
        }

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
            return {
                "ok": False,
                "message": "Thiếu ID phim"
            }

        if not name or not genre or not duration or not show_dates or not show_times or not price:
            return {
                "ok": False,
                "message": "Vui lòng nhập đầy đủ tên phim, thể loại, thời lượng, ngày chiếu, suất chiếu và giá vé"
            }

        try:
            duration = int(duration)
            price = int(price)

            if duration <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            return {
                "ok": False,
                "message": "Thời lượng và giá vé phải là số nguyên dương"
            }

        update_movie(
            movie_id,
            name,
            genre,
            duration,
            director,
            actors,
            description,
            image_path,
            show_dates,
            show_times,
            price,
            data.get("movie_status") or "now_showing",
            1 if data.get("is_hot") else 0,
            data.get("banner_image_path") or ""
        )

        return {
            "ok": True,
            "message": "Đã cập nhật phim"
        }

    def delete_movie(self, movie_id):
        delete_movie(movie_id)

        return {
            "ok": True,
            "message": "Đã xóa phim"
        }

    def add_content_item(self, data):
        title = (data.get("title") or "").strip()
        category = (data.get("category") or "").strip()

        if not title or not category:
            return {
                "ok": False,
                "message": "Vui lòng nhập tiêu đề và loại nội dung"
            }

        add_content_item(
            category,
            title,
            data.get("subtitle") or "",
            data.get("description") or "",
            data.get("image_path") or "",
            data.get("status") or "active"
        )

        return {
            "ok": True,
            "message": "Đã thêm nội dung"
        }

    def update_content_item(self, data):
        item_id = data.get("id")
        title = (data.get("title") or "").strip()
        category = (data.get("category") or "").strip()

        if not item_id:
            return {
                "ok": False,
                "message": "Thiếu ID nội dung"
            }

        if not title or not category:
            return {
                "ok": False,
                "message": "Vui lòng nhập tiêu đề và loại nội dung"
            }

        update_content_item(
            item_id,
            category,
            title,
            data.get("subtitle") or "",
            data.get("description") or "",
            data.get("image_path") or "",
            data.get("status") or "active"
        )

        return {
            "ok": True,
            "message": "Đã cập nhật nội dung"
        }

    def delete_content_item(self, item_id):
        delete_content_item(item_id)

        return {
            "ok": True,
            "message": "Đã xóa nội dung"
        }

    def search_movies(self, keyword):
        return [movie_to_dict(movie) for movie in search_movies(keyword)]

    def login(self, username, password):
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            return {
                "ok": False,
                "message": "Vui lòng nhập tài khoản và mật khẩu"
            }

        user = check_login(username, password)

        if not user:
            return {
                "ok": False,
                "message": "Sai tài khoản hoặc mật khẩu"
            }

        return {
            "ok": True,
            "user": {
                "id": user[0],
                "username": user[1],
                "role": user[3] if len(user) > 3 else "user"
            }
        }

    def register(self, data):
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()

        if not username or not password:
            return {
                "ok": False,
                "message": "Vui lòng nhập tài khoản và mật khẩu"
            }

        if len(password) < 6:
            return {
                "ok": False,
                "message": "Mật khẩu tối thiểu 6 ký tự"
            }

        if email and phone:
            return {
                "ok": False,
                "message": "Chỉ nhập email hoặc số điện thoại"
            }

        if not email and not phone:
            return {
                "ok": False,
                "message": "Vui lòng nhập email hoặc số điện thoại"
            }

        if add_user(username, password, email or None, phone or None):
            return {
                "ok": True,
                "message": "Đăng ký thành công"
            }

        return {
            "ok": False,
            "message": "Tên tài khoản đã tồn tại"
        }

    def get_booked_seats(self, movie_name, show_date, show_time):
        return get_booked_seats(movie_name, show_date, show_time)

    def get_my_tickets(self, user_id=1):
        tickets = []

        for pay in get_payments(user_id):
            tickets.append({
                "id": pay[0],
                "user_id": pay[1],
                "movie_name": pay[2],
                "show_date": pay[3],
                "seats": pay[4],
                "total": pay[5],
                "method": pay[6],
                "created_at": pay[7] if len(pay) > 7 else "",
                "show_time": pay[8] if len(pay) > 8 else "",
                "ticket_code": pay[9] if len(pay) > 9 else f"TICKET-{pay[0]}",
                "status": pay[10] if len(pay) > 10 else "Đã thanh toán",
            })

        return tickets

    def create_booking(self, data):
        user_id = data.get("user_id") or 1
        movie_name = data.get("movie_name")
        show_date = data.get("show_date")
        show_time = data.get("show_time")
        seats = data.get("seats") or []
        total = data.get("total") or 0
        method = data.get("method") or "Demo"

        if not movie_name or not show_date or not show_time or not seats:
            return {
                "ok": False,
                "message": "Thiếu thông tin đặt vé"
            }

        booked = get_booked_seats(movie_name, show_date, show_time)
        duplicated = [seat for seat in seats if seat in booked]

        if duplicated:
            return {
                "ok": False,
                "message": "Ghế đã được đặt: " + ", ".join(duplicated)
            }

        ticket_code = add_payment(
            user_id,
            movie_name,
            show_date,
            show_time,
            ", ".join(seats),
            total,
            method
        )

        for seat in seats:
            add_booking(user_id, movie_name, show_date, show_time, seat)

        return {
            "ok": True,
            "ticket_code": ticket_code
        }


if __name__ == "__main__":
    create_tables()

    api = Api()
    index_path = os.path.join(WEB_DIR, "index.html")

    webview.create_window(
        "Movie App",
        index_path,
        js_api=api,
        width=1366,
        height=768,
        min_size=(1100, 700),
    )

    webview.start(debug=True)
