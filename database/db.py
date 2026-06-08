import os
import sqlite3
import hashlib
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "movie.db")


def connect_db():
    return sqlite3.connect(DB_PATH)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def add_column_if_missing(cursor, table, column, column_type):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]

    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        email TEXT,
        phone TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        genre TEXT,
        duration INTEGER,
        director TEXT,
        actors TEXT,
        description TEXT,
        image TEXT,
        show_dates TEXT,
        show_times TEXT,
        price INTEGER DEFAULT 90000
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        movie_name TEXT,
        show_date TEXT,
        seat TEXT,
        show_time TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            subtitle TEXT,
            description TEXT,
            image_path TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        movie_name TEXT,
        show_date TEXT,
        seats TEXT,
        total INTEGER,
        method TEXT,
        created_at TEXT,
        show_time TEXT,
        ticket_code TEXT,
        status TEXT DEFAULT 'Đã thanh toán',
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    add_column_if_missing(cursor, "users", "email", "TEXT")
    add_column_if_missing(cursor, "users", "phone", "TEXT")

    add_column_if_missing(cursor, "movies", "show_times", "TEXT")
    add_column_if_missing(cursor, "movies", "price", "INTEGER DEFAULT 90000")
    add_column_if_missing(cursor, "bookings", "cinema", "TEXT")
    add_column_if_missing(cursor, "payments", "cinema", "TEXT")
    add_column_if_missing(cursor, "bookings", "show_time", "TEXT")

    add_column_if_missing(cursor, "payments", "created_at", "TEXT")
    add_column_if_missing(cursor, "payments", "show_time", "TEXT")
    add_column_if_missing(cursor, "payments", "ticket_code", "TEXT")
    add_column_if_missing(cursor, "payments", "status", "TEXT DEFAULT 'Đã thanh toán'")
    add_column_if_missing(cursor, "movies", "movie_status", "TEXT DEFAULT 'now_showing'")
    add_column_if_missing(cursor, "movies", "is_hot", "INTEGER DEFAULT 0")
    add_column_if_missing(cursor, "movies", "banner_image", "TEXT")
    cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (username, password, role, email, phone) VALUES (?, ?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "admin", "admin@gmail.com", None)
        )

    conn.commit()
    conn.close()


def normalize_text(value):
    value = (value or "").strip()
    return value if value else None


def add_user(username, password, email=None, phone=None):
    username = normalize_text(username)
    email = normalize_text(email)
    phone = normalize_text(phone)

    if not username or not password:
        return False

    if bool(email) == bool(phone):
        return False

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False

        if email:
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return False

        if phone:
            cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
            if cursor.fetchone():
                return False

        cursor.execute("""
        INSERT INTO users (username, password, role, email, phone)
        VALUES (?, ?, ?, ?, ?)
        """, (username, hash_password(password), "user", email, phone))

        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def check_login(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username.strip(), hash_password(password))
    )

    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_username(username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    user = cursor.fetchone()

    conn.close()
    return user


def get_reset_contact(username):
    user = get_user_by_username(username)

    if not user:
        return None

    email = user[4] if len(user) > 4 else None
    phone = user[5] if len(user) > 5 else None

    if email:
        return {
            "type": "email",
            "value": email,
            "masked": mask_email(email)
        }

    if phone:
        return {
            "type": "phone",
            "value": phone,
            "masked": mask_phone(phone)
        }

    return None


def mask_email(email):
    email = email.strip()

    if "@" not in email:
        return email

    name, domain = email.split("@", 1)

    if len(name) <= 2:
        masked_name = name[0] + "..."
    else:
        masked_name = name[:2] + "..."

    return f"{masked_name}@{domain}"


def mask_phone(phone):
    phone = phone.strip()

    if len(phone) <= 6:
        return phone[:2] + "..." + phone[-1:]

    return phone[:3] + "...." + phone[-3:]


def verify_reset_contact(username, contact_value):
    user = get_user_by_username(username)

    if not user:
        return False

    email = user[4] if len(user) > 4 else None
    phone = user[5] if len(user) > 5 else None

    contact_value = contact_value.strip()

    if email and contact_value.lower() == email.lower():
        return True

    if phone and contact_value == phone:
        return True

    return False


def update_password(username, new_password):
    if not username or not new_password:
        return False

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (hash_password(new_password), username.strip())
    )

    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def add_movie(
    name,
    genre,
    duration,
    director,
    actors,
    description,
    image,
    show_dates,
    show_times,
    price,
    movie_status="now_showing",
    is_hot=0,
banner_image=""
):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movies
        (name, genre, duration, director, actors, description, image, show_dates, show_times, price, movie_status, is_hot,banner_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        genre,
        duration,
        director,
        actors,
        description,
        image,
        show_dates,
        show_times,
        price,
        movie_status,
        is_hot,
        banner_image
    ))
    conn.commit()
    conn.close()


def get_movies():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, genre, duration, director, actors, description,
               image, show_dates, show_times, price, movie_status, is_hot, banner_image
        FROM movies
        ORDER BY id DESC
    """)

    movies = cursor.fetchall()
    conn.close()
    return movies

def update_movie(
    movie_id,
    name,
    genre,
    duration,
    director,
    actors,
    description,
    image,
    show_dates,
    show_times,
    price,
    movie_status="now_showing",
    is_hot=0,
banner_image=""
):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE movies
        SET name = ?,
            genre = ?,
            duration = ?,
            director = ?,
            actors = ?,
            description = ?,
            image = ?,
            show_dates = ?,
            show_times = ?,
            price = ?,
            movie_status = ?,
            is_hot = ?,
            banner_image = ?
        WHERE id = ?
    """, (
        name,
        genre,
        duration,
        director,
        actors,
        description,
        image,
        show_dates,
        show_times,
        price,
        movie_status,
        is_hot,
        banner_image,
        movie_id

    ))
    conn.commit()
    conn.close()


def delete_movie(movie_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()

    if movie:
        cursor.execute("DELETE FROM bookings WHERE movie_name = ?", (movie[0],))
        cursor.execute("DELETE FROM payments WHERE movie_name = ?", (movie[0],))

    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))

    conn.commit()
    conn.close()


def search_movies(keyword):
    conn = connect_db()
    cursor = conn.cursor()

    keyword = f"%{keyword}%"

    cursor.execute("""
        SELECT id, name, genre, duration, director, actors, description,
               image, show_dates, show_times, price, movie_status, is_hot, banner_image
        FROM movies
        WHERE name LIKE ?
           OR genre LIKE ?
           OR director LIKE ?
           OR actors LIKE ?
        ORDER BY id DESC
    """, (keyword, keyword, keyword, keyword))

    movies = cursor.fetchall()
    conn.close()
    return movies

def add_booking(user_id, movie_name, show_date, show_time, seat, cinema=""):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bookings (user_id, movie_name, show_date, show_time, seat, cinema)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, movie_name, show_date, show_time, seat, cinema))

    conn.commit()
    conn.close()


def get_booked_seats(movie_name, show_date, show_time, cinema=None):
    conn = connect_db()
    cursor = conn.cursor()

    if cinema:
        cursor.execute("""
        SELECT seat FROM bookings
        WHERE movie_name = ? AND show_date = ? AND show_time = ? AND cinema = ?
        """, (movie_name, show_date, show_time, cinema))
    else:
        cursor.execute("""
        SELECT seat FROM bookings
        WHERE movie_name = ? AND show_date = ? AND show_time = ?
        """, (movie_name, show_date, show_time))

    seats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return seats


def add_payment(user_id, movie_name, show_date, show_time, seats, total, method, cinema=""):
    conn = connect_db()
    cursor = conn.cursor()

    ticket_code = "TICKET-" + uuid.uuid4().hex[:8].upper()

    cursor.execute("""
    INSERT INTO payments
    (user_id, movie_name, show_date, seats, total, method, created_at, show_time, ticket_code, status, cinema)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?)
    """, (
        user_id,
        movie_name,
        show_date,
        seats,
        total,
        method,
        show_time,
        ticket_code,
        "Đã thanh toán",
        cinema
    ))

    conn.commit()
    conn.close()
    return ticket_code


def get_payments(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM payments
    WHERE user_id = ?
    ORDER BY id DESC
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data
def get_content_items(category=None):
    conn = connect_db()
    cursor = conn.cursor()

    if category:
        cursor.execute("""
            SELECT id, category, title, subtitle, description, image_path, status, created_at
            FROM content_items
            WHERE category = ?
            ORDER BY id DESC
        """, (category,))
    else:
        cursor.execute("""
            SELECT id, category, title, subtitle, description, image_path, status, created_at
            FROM content_items
            ORDER BY id DESC
        """)

    items = cursor.fetchall()
    conn.close()
    return items


def add_content_item(category, title, subtitle="", description="", image_path="", status="active"):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO content_items (category, title, subtitle, description, image_path, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (category, title, subtitle, description, image_path, status))

    conn.commit()
    conn.close()
    return True


def update_content_item(item_id, category, title, subtitle="", description="", image_path="", status="active"):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE content_items
        SET category = ?, title = ?, subtitle = ?, description = ?, image_path = ?, status = ?
        WHERE id = ?
    """, (category, title, subtitle, description, image_path, status, item_id))

    conn.commit()
    conn.close()
    return True


def delete_content_item(item_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM content_items WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()
    return True
