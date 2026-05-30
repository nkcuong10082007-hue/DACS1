import os
import shutil
import sqlite3

BASE_DIR = r"C:\Users\Admin\PycharmProjects\PythonProject1"
DB_PATH = os.path.join(BASE_DIR, "movie.db")
POSTER_DIR = os.path.join(BASE_DIR, "assets", "posters")

MOVIE_NAME = "AVENGERS: ENDGAME"
SOURCE_POSTER = r"C:\Users\Admin\Downloads\tải xuống (3).jpg"


os.makedirs(POSTER_DIR, exist_ok=True)

filename = os.path.basename(SOURCE_POSTER)
name, ext = os.path.splitext(filename)
target_path = os.path.join(POSTER_DIR, filename)

count = 1
while os.path.exists(target_path):
    target_path = os.path.join(POSTER_DIR, f"{name}_{count}{ext}")
    count += 1

shutil.copy2(SOURCE_POSTER, target_path)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(
    "UPDATE movies SET image = ? WHERE name = ?",
    (target_path, MOVIE_NAME)
)

conn.commit()
conn.close()

print("Đã cập nhật poster:", target_path)
