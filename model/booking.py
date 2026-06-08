import uuid
from model.base_model import BaseModel


class Booking(BaseModel):
    """
    Xử lý việc đặt ghế và thanh toán.
    Gộp 2 bảng bookings + payments vào 1 class vì chúng liên quan chặt.
    """

    @classmethod
    def get_booked_seats(cls, movie_name, show_date, show_time, cinema=None):
        """
        Lấy danh sách ghế đã bị đặt cho 1 suất chiếu.
        Trả về list string, ví dụ: ["A1", "A2", "B3"]
        """
        if cinema:
            rows = cls.query("""
                SELECT seat FROM bookings
                WHERE movie_name=? AND show_date=? AND show_time=? AND cinema=?
            """, (movie_name, show_date, show_time, cinema))
        else:
            rows = cls.query("""
                SELECT seat FROM bookings
                WHERE movie_name=? AND show_date=? AND show_time=?
            """, (movie_name, show_date, show_time))

        return [row["seat"] for row in rows]

    @classmethod
    def add_seat(cls, user_id, movie_name, show_date, show_time, seat, cinema=""):
        """Lưu 1 ghế vào bảng bookings."""
        cls.execute("""
            INSERT INTO bookings (user_id, movie_name, show_date, show_time, seat, cinema)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, movie_name, show_date, show_time, seat, cinema))

    @classmethod
    def create_payment(cls, user_id, movie_name, show_date, show_time,
                       seats, total, method, cinema=""):
        """
        Tạo bản ghi thanh toán và tự sinh ticket_code duy nhất.
        uuid4().hex[:8] tạo chuỗi hex 8 ký tự ngẫu nhiên.
        Trả về ticket_code để hiển thị cho người dùng.
        """
        ticket_code = "TICKET-" + uuid.uuid4().hex[:8].upper()

        cls.execute("""
            INSERT INTO payments
            (user_id, movie_name, show_date, seats, total, method,
             created_at, show_time, ticket_code, status, cinema)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, 'Đã thanh toán', ?)
        """, (user_id, movie_name, show_date, seats, total, method,
              show_time, ticket_code, cinema))

        return ticket_code

    @classmethod
    def get_tickets_by_user(cls, user_id):
        """
        Lấy toàn bộ vé đã mua của 1 user.
        Trả về list dict để trả thẳng về frontend.
        """
        rows = cls.query("""
            SELECT * FROM payments
            WHERE user_id=?
            ORDER BY id DESC
        """, (user_id,))

        tickets = []
        for row in rows:
            tickets.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "movie_name": row["movie_name"],
                "show_date": row["show_date"],
                "seats": row["seats"],
                "total": row["total"],
                "method": row["method"],
                "created_at": row["created_at"] or "",
                "show_time": row["show_time"] or "",
                "ticket_code": row["ticket_code"] or f"TICKET-{row['id']}",
                "status": row["status"] or "Đã thanh toán",
                "cinema": row["cinema"] or "Chưa chọn rạp",
            })

        return tickets