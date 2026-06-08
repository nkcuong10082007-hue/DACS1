from model.base_model import BaseModel


class Movie(BaseModel):
    """
    Đại diện cho một bộ phim trong hệ thống.
    Mỗi instance = 1 dòng trong bảng movies.
    """

    def __init__(self, id, name, genre, duration, director, actors,
                 description, image, show_dates, show_times,
                 price, movie_status, is_hot, banner_image):
        self.id = id
        self.name = name
        self.genre = genre
        self.duration = duration
        self.director = director
        self.actors = actors
        self.description = description
        self.image = image
        self.show_dates = show_dates
        self.show_times = show_times
        self.price = price or 90000
        self.movie_status = movie_status or "now_showing"
        self.is_hot = is_hot or 0
        self.banner_image = banner_image

    @classmethod
    def get_all(cls):
        """Lấy toàn bộ phim, sắp xếp mới nhất trước."""
        rows = cls.query("""
            SELECT id, name, genre, duration, director, actors, description,
                   image, show_dates, show_times, price, movie_status, is_hot, banner_image
            FROM movies
            ORDER BY id DESC
        """)
        return [cls._from_row(row) for row in rows]

    @classmethod
    def search(cls, keyword):
        """Tìm kiếm theo tên, thể loại, đạo diễn, diễn viên."""
        like = f"%{keyword}%"
        rows = cls.query("""
            SELECT id, name, genre, duration, director, actors, description,
                   image, show_dates, show_times, price, movie_status, is_hot, banner_image
            FROM movies
            WHERE name LIKE ? OR genre LIKE ? OR director LIKE ? OR actors LIKE ?
            ORDER BY id DESC
        """, (like, like, like, like))
        return [cls._from_row(row) for row in rows]

    @classmethod
    def get_by_id(cls, movie_id):
        """Tìm phim theo ID. Trả về Movie object hoặc None."""
        row = cls.query_one("""
            SELECT id, name, genre, duration, director, actors, description,
                   image, show_dates, show_times, price, movie_status, is_hot, banner_image
            FROM movies WHERE id = ?
        """, (movie_id,))
        return cls._from_row(row) if row else None

    @classmethod
    def create(cls, name, genre, duration, director, actors, description,
               image, show_dates, show_times, price,
               movie_status="now_showing", is_hot=0, banner_image=""):
        """Thêm phim mới. Trả về id vừa tạo."""
        return cls.execute("""
            INSERT INTO movies
            (name, genre, duration, director, actors, description, image,
             show_dates, show_times, price, movie_status, is_hot, banner_image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, genre, duration, director, actors, description, image,
              show_dates, show_times, price, movie_status, is_hot, banner_image))

    @classmethod
    def update(cls, movie_id, name, genre, duration, director, actors,
               description, image, show_dates, show_times, price,
               movie_status="now_showing", is_hot=0, banner_image=""):
        """Cập nhật thông tin phim theo ID."""
        cls.execute("""
            UPDATE movies
            SET name=?, genre=?, duration=?, director=?, actors=?,
                description=?, image=?, show_dates=?, show_times=?,
                price=?, movie_status=?, is_hot=?, banner_image=?
            WHERE id=?
        """, (name, genre, duration, director, actors, description, image,
              show_dates, show_times, price, movie_status, is_hot, banner_image,
              movie_id))

    @classmethod
    def delete(cls, movie_id):
        """
        Xóa phim và toàn bộ booking/payment liên quan.
        Đây là cascade delete thủ công.
        """
        row = cls.query_one("SELECT name FROM movies WHERE id=?", (movie_id,))
        if row:
            movie_name = row["name"]
            cls.execute("DELETE FROM bookings WHERE movie_name=?", (movie_name,))
            cls.execute("DELETE FROM payments WHERE movie_name=?", (movie_name,))
        cls.execute("DELETE FROM movies WHERE id=?", (movie_id,))

    def to_dict(self):
        """Chuyển Movie object thành dict để trả về frontend."""
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre,
            "duration": self.duration,
            "director": self.director,
            "actors": self.actors,
            "description": self.description,
            "image_path": self.image,
            "show_dates": self.show_dates,
            "show_times": self.show_times,
            "price": self.price,
            "movie_status": self.movie_status,
            "is_hot": self.is_hot,
            "banner_image_path": self.banner_image,
        }

    @classmethod
    def _from_row(cls, row):
        """Factory method — tạo Movie object từ sqlite3.Row."""
        return cls(
            id=row["id"],
            name=row["name"],
            genre=row["genre"],
            duration=row["duration"],
            director=row["director"],
            actors=row["actors"],
            description=row["description"],
            image=row["image"],
            show_dates=row["show_dates"],
            show_times=row["show_times"],
            price=row["price"],
            movie_status=row["movie_status"],
            is_hot=row["is_hot"],
            banner_image=row["banner_image"],
        )