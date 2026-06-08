import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "movie.db")


class BaseModel:
    """
    Class cha cho tất cả các model.
    Chứa logic kết nối database dùng chung,
    tránh lặp code ở mỗi class con.
    """

    db_path = DB_PATH

    @classmethod
    def get_connection(cls):
        conn = sqlite3.connect(cls.db_path, timeout=10)
        # timeout=10 nghĩa là nếu DB đang bị lock, chờ tối đa 10 giây
        # thay vì báo lỗi ngay lập tức
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def execute(cls, sql, params=()):
        """
        Chạy câu lệnh INSERT / UPDATE / DELETE.
        Tự động commit và đóng connection.
        Trả về lastrowid (id của dòng vừa insert).
        """
        conn = cls.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def query(cls, sql, params=()):
        """
        Chạy câu lệnh SELECT, trả về danh sách kết quả.
        Mỗi phần tử là sqlite3.Row — truy cập được theo tên cột.
        """
        conn = cls.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def query_one(cls, sql, params=()):
        """
        Giống query() nhưng chỉ trả về 1 dòng (hoặc None nếu không có).
        """
        conn = cls.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            conn.close()

    def __repr__(self):
        """
        Hiển thị đẹp khi print() object — hữu ích khi debug.
        Ví dụ: print(movie) → <Movie id=1 name='Avengers'>
        """
        class_name = self.__class__.__name__
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"<{class_name} {attrs}>"