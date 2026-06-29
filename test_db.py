import sqlite3

conn = sqlite3.connect("../movie.db")

print("Kết nối database thành công")

conn.close()