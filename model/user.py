import bcrypt
from model.base_model import BaseModel


class User(BaseModel):
    """
    Đại diện cho một tài khoản người dùng.

    Dùng bcrypt thay SHA256 vì bcrypt tự thêm salt ngẫu nhiên:
    - SHA256("admin123") → luôn cùng 1 chuỗi → dễ bị rainbow table
    - bcrypt("admin123") → chuỗi khác nhau mỗi lần → an toàn hơn
    """

    def __init__(self, id, username, password_hash, role, email, phone):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role or "user"
        self.email = email
        self.phone = phone

    @staticmethod
    def hash_password(plain_password):
        """Hash mật khẩu bằng bcrypt. Trả về string để lưu SQLite."""
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password, password_hash):
        """Kiểm tra mật khẩu có khớp hash không."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    @classmethod
    def create(cls, username, plain_password, email=None, phone=None):
        """
        Tạo tài khoản mới. Trả về True nếu thành công, False nếu trùng.
        """
        username = (username or "").strip()
        email = (email or "").strip() or None
        phone = (phone or "").strip() or None

        if not username or not plain_password:
            return False

        if cls.query_one("SELECT id FROM users WHERE username=?", (username,)):
            return False

        if email and cls.query_one("SELECT id FROM users WHERE email=?", (email,)):
            return False

        if phone and cls.query_one("SELECT id FROM users WHERE phone=?", (phone,)):
            return False

        cls.execute("""
            INSERT INTO users (username, password, role, email, phone)
            VALUES (?, ?, 'user', ?, ?)
        """, (username, cls.hash_password(plain_password), email, phone))

        return True

    @classmethod
    def authenticate(cls, username, plain_password):
        """
        Kiểm tra đăng nhập.
        Lý do không dùng WHERE password=? trong SQL:
        bcrypt hash khác nhau mỗi lần, phải lấy về rồi verify thủ công.
        Trả về User object nếu đúng, None nếu sai.
        """
        row = cls.query_one(
            "SELECT * FROM users WHERE username=?",
            (username.strip(),)
        )

        if not row:
            return None

        if not cls.verify_password(plain_password, row["password"]):
            return None

        return cls._from_row(row)

    @classmethod
    def get_by_username(cls, username):
        """Tìm user theo username. Trả về User object hoặc None."""
        row = cls.query_one(
            "SELECT * FROM users WHERE username=?",
            (username.strip(),)
        )
        return cls._from_row(row) if row else None

    @classmethod
    def update_password(cls, username, new_plain_password):
        """Đổi mật khẩu. Trả về True nếu thành công."""
        if not username or not new_plain_password:
            return False
        cls.execute(
            "UPDATE users SET password=? WHERE username=?",
            (cls.hash_password(new_plain_password), username.strip())
        )
        return True

    def to_dict(self):
        """Trả về dict an toàn — KHÔNG bao gồm password_hash."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "email": self.email,
            "phone": self.phone,
        }

    def is_admin(self):
        return self.role == "admin"

    @classmethod
    def _from_row(cls, row):
        keys = row.keys()
        return cls(
            id=row["id"],
            username=row["username"],
            password_hash=row["password"],
            role=row["role"] if "role" in keys else "user",
            email=row["email"] if "email" in keys else None,
            phone=row["phone"] if "phone" in keys else None,
        )

    @staticmethod
    def mask_email(email):
        email = email.strip()
        if "@" not in email:
            return email
        name, domain = email.split("@", 1)
        masked = name[:2] + "..." if len(name) > 2 else name[0] + "..."
        return f"{masked}@{domain}"

    @staticmethod
    def mask_phone(phone):
        phone = phone.strip()
        if len(phone) <= 6:
            return phone[:2] + "..." + phone[-1:]
        return phone[:3] + "...." + phone[-3:]