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
    @staticmethod
    def _ticket_count(seats_text):
        seats = [seat.strip() for seat in str(seats_text or "").split(",") if seat.strip()]
        return len(seats) if seats else 1

    @classmethod
    def get_statistics(cls):
        """Tổng hợp số liệu bán vé cho màn hình admin."""
        rows = cls.query("""
            SELECT movie_name, show_date, show_time, seats, total, method, cinema, created_at
            FROM payments
            ORDER BY id DESC
        """)

        movie_stats = {}
        time_stats = {}
        date_stats = {}
        cinema_stats = {}
        recent_payments = []
        total_orders = len(rows)
        total_tickets = 0
        total_revenue = 0

        def add_group(store, label, tickets, revenue):
            key = label or "Chưa rõ"
            item = store.setdefault(key, {
                "label": key,
                "orders": 0,
                "tickets": 0,
                "revenue": 0
            })
            item["orders"] += 1
            item["tickets"] += tickets
            item["revenue"] += revenue

        for row in rows:
            movie_name = row["movie_name"] or "Chưa rõ phim"
            show_date = row["show_date"] or "Chưa rõ ngày"
            show_time = row["show_time"] or "Chưa rõ suất"
            cinema = row["cinema"] or "Chưa rõ rạp"
            tickets = cls._ticket_count(row["seats"])
            revenue = int(row["total"] or 0)

            total_tickets += tickets
            total_revenue += revenue

            add_group(movie_stats, movie_name, tickets, revenue)
            add_group(time_stats, show_time, tickets, revenue)
            add_group(date_stats, show_date, tickets, revenue)
            add_group(cinema_stats, cinema, tickets, revenue)

            if len(recent_payments) < 8:
                recent_payments.append({
                    "movie_name": movie_name,
                    "show_date": show_date,
                    "show_time": show_time,
                    "cinema": cinema,
                    "tickets": tickets,
                    "total": revenue,
                    "method": row["method"] or "",
                    "created_at": row["created_at"] or ""
                })

        def sort_group(store):
            return sorted(
                store.values(),
                key=lambda item: (item["tickets"], item["orders"], item["revenue"]),
                reverse=True
            )

        movies = sort_group(movie_stats)
        times = sort_group(time_stats)
        dates = sort_group(date_stats)
        cinemas = sort_group(cinema_stats)

        return {
            "summary": {
                "total_orders": total_orders,
                "total_tickets": total_tickets,
                "total_revenue": total_revenue,
                "top_movie": movies[0] if movies else None,
                "top_time": times[0] if times else None,
                "top_cinema": cinemas[0] if cinemas else None
            },
            "movies": movies,
            "times": times,
            "dates": dates,
            "cinemas": cinemas,
            "recent_payments": recent_payments
        }
