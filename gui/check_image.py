import sqlite3
from PIL import Image

conn = sqlite3.connect(r"C:\Users\Admin\PycharmProjects\PythonProject1\movie.db")
cursor = conn.cursor()

for row in cursor.execute("SELECT id, name, image FROM movies"):
    print(row)

print("\nKiểm tra riêng Avengers:")
cursor.execute("SELECT id, name, image FROM movies WHERE name LIKE ?", ("%AVENGERS%",))
movie = cursor.fetchone()
print(movie)

if movie:
    img = Image.open(movie[2])
    print("Kích thước ảnh DB đang dùng:", img.size)

conn.close()
