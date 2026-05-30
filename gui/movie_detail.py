import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageOps

import session
from database.db import get_booked_seats
from gui.book_ticket import book_ticket_screen


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = "#F5F6FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
PRIMARY = "#E50914"
PRIMARY_HOVER = "#B20710"
BORDER = "#E5E7EB"
YELLOW = "#F59E0B"


def maximize_window(win):
    try:
        win.state("zoomed")
    except Exception:
        width = win.winfo_screenwidth()
        height = win.winfo_screenheight()
        win.geometry(f"{width}x{height}+0+0")


def open_on_top(win):
    maximize_window(win)
    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.after(700, lambda: win.attributes("-topmost", False))


def poster_image(path, size):
    img = Image.open(path).convert("RGB")
    img = ImageOps.contain(img, size)
    canvas = Image.new("RGB", size, "#F3F4F6")
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def show_detail(movie):
    win = ctk.CTkToplevel()
    win.title("Chi tiết phim")
    win.configure(fg_color=BG)
    open_on_top(win)

    price = movie[10] if len(movie) > 10 and movie[10] else 90000
    show_times = movie[9] if len(movie) > 9 and movie[9] else "10:00, 12:00, 19:30"

    try:
        price = int(price)
    except Exception:
        price = 90000

    dates = [d.strip() for d in (movie[8] or "").split(",") if d.strip()]
    times = [t.strip() for t in show_times.split(",") if t.strip()]

    container = ctk.CTkScrollableFrame(
        win,
        fg_color=BG,
        scrollbar_button_color="#D1D5DB",
        scrollbar_button_hover_color="#9CA3AF"
    )
    container.pack(fill="both", expand=True, padx=28, pady=24)

    main = ctk.CTkFrame(container, fg_color="transparent")
    main.pack(fill="both", expand=True)

    left = ctk.CTkFrame(main, fg_color="transparent", width=420)
    left.pack(side="left", padx=(0, 34), pady=4, anchor="n")

    poster_card = ctk.CTkFrame(
        left,
        fg_color=CARD,
        corner_radius=18,
        border_width=1,
        border_color=BORDER
    )
    poster_card.pack(fill="x", pady=(0, 16))

    try:
        raw_img = Image.open(movie[7]).convert("RGB")
        raw_img = raw_img.resize((300, 450), Image.Resampling.LANCZOS)

        poster = ctk.CTkImage(
            light_image=raw_img,
            dark_image=raw_img,
            size=(300, 450)
        )

        poster_label = ctk.CTkLabel(poster_card, image=poster, text="")
        poster_label.image = poster
        poster_label.pack(padx=12, pady=12)

    except Exception as e:
        placeholder = ctk.CTkFrame(
            poster_card,
            fg_color="#F3F4F6",
            corner_radius=14,
            width=300,
            height=450
        )
        placeholder.pack(padx=12, pady=12)
        placeholder.pack_propagate(False)

        ctk.CTkLabel(
            placeholder,
            text=f"KHÔNG CÓ ẢNH\n{e}",
            text_color=MUTED,
            font=("Arial", 13, "bold"),
            wraplength=260,
            justify="center"
        ).pack(expand=True)

    price_card = ctk.CTkFrame(
        left,
        fg_color=CARD,
        corner_radius=18,
        border_width=1,
        border_color=BORDER
    )
    price_card.pack(fill="x")

    ctk.CTkLabel(
        price_card,
        text="Giá vé",
        text_color=MUTED,
        font=("Arial", 13)
    ).pack(anchor="w", padx=18, pady=(16, 3))

    ctk.CTkLabel(
        price_card,
        text=f"{price:,} VNĐ",
        text_color=PRIMARY,
        font=("Arial", 24, "bold")
    ).pack(anchor="w", padx=18, pady=(0, 16))

    right = ctk.CTkFrame(main, fg_color="transparent")
    right.pack(side="left", fill="both", expand=True, pady=4)

    ctk.CTkLabel(
        right,
        text=movie[1],
        text_color=PRIMARY,
        font=("Arial", 34, "bold"),
        wraplength=920,
        justify="left"
    ).pack(anchor="w", pady=(0, 18))

    info = ctk.CTkFrame(
        right,
        fg_color=CARD,
        corner_radius=18,
        border_width=1,
        border_color=BORDER
    )
    info.pack(fill="x", pady=(0, 20))

    info_inner = ctk.CTkFrame(info, fg_color="transparent")
    info_inner.pack(fill="x", padx=24, pady=20)

    rows = [
        ("Thể loại", movie[2]),
        ("Thời lượng", f"{movie[3]} phút"),
        ("Đạo diễn", movie[4]),
        ("Diễn viên", movie[5]),
        ("Suất chiếu", show_times),
    ]

    for label, value in rows:
        row = ctk.CTkFrame(info_inner, fg_color="transparent")
        row.pack(fill="x", pady=6)

        ctk.CTkLabel(
            row,
            text=f"{label}:",
            text_color=MUTED,
            font=("Arial", 13, "bold"),
            width=110,
            anchor="w"
        ).pack(side="left", anchor="n")

        ctk.CTkLabel(
            row,
            text=value or "Chưa cập nhật",
            text_color=TEXT,
            font=("Arial", 13),
            wraplength=760,
            justify="left",
            anchor="w"
        ).pack(side="left", fill="x", expand=True, anchor="n")

    ctk.CTkLabel(
        info_inner,
        text="Ngày chiếu",
        text_color=YELLOW,
        font=("Arial", 17, "bold")
    ).pack(anchor="w", pady=(18, 8))

    date_grid = ctk.CTkFrame(info_inner, fg_color="transparent")
    date_grid.pack(fill="x", anchor="w")

    if dates and times:
        first_time = times[0]

        for idx, date in enumerate(dates):
            remain = 40 - len(get_booked_seats(movie[1], date, first_time))
            row, col = divmod(idx, 2)

            badge = ctk.CTkFrame(
                date_grid,
                fg_color="#F3F4F6",
                corner_radius=12,
                border_width=1,
                border_color=BORDER
            )
            badge.grid(row=row, column=col, padx=(0, 10), pady=6, sticky="ew")

            ctk.CTkLabel(
                badge,
                text=f"{date} • còn khoảng {remain} ghế • suất {first_time}",
                text_color=TEXT,
                font=("Arial", 12),
                wraplength=380,
                justify="left"
            ).pack(anchor="w", padx=14, pady=9)

        date_grid.grid_columnconfigure(0, weight=1)
        date_grid.grid_columnconfigure(1, weight=1)
    else:
        badge = ctk.CTkFrame(
            date_grid,
            fg_color="#F3F4F6",
            corner_radius=12,
            border_width=1,
            border_color=BORDER
        )
        badge.pack(anchor="w", pady=6)

        ctk.CTkLabel(
            badge,
            text="Chưa có lịch chiếu",
            text_color=TEXT,
            font=("Arial", 12)
        ).pack(padx=14, pady=9)

    ctk.CTkLabel(
        right,
        text="Nội dung phim",
        text_color=YELLOW,
        font=("Arial", 21, "bold")
    ).pack(anchor="w", pady=(6, 10))

    desc_card = ctk.CTkFrame(
        right,
        fg_color=CARD,
        corner_radius=18,
        border_width=1,
        border_color=BORDER
    )
    desc_card.pack(fill="x", pady=(0, 24))

    desc_box = ctk.CTkTextbox(
        desc_card,
        height=260,
        fg_color=CARD,
        text_color=TEXT,
        border_width=0,
        font=("Arial", 13),
        wrap="word"
    )
    desc_box.pack(fill="x", padx=18, pady=18)
    desc_box.insert("1.0", movie[6] or "Chưa có mô tả.")
    desc_box.configure(state="disabled")

    buttons = ctk.CTkFrame(right, fg_color="transparent")
    buttons.pack(anchor="w", pady=(8, 30))

    def open_booking():
        if not session.is_logged_in():
            messagebox.showwarning("Thông báo", "Vui lòng đăng nhập để đặt vé")
            return

        if not dates or not times:
            messagebox.showwarning("Thông báo", "Phim này chưa có lịch chiếu")
            return

        book_ticket_screen(movie[1], movie[8], show_times, price)

    ctk.CTkButton(
        buttons,
        text="Đặt vé ngay",
        width=170,
        height=48,
        corner_radius=14,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="white",
        font=("Arial", 14, "bold"),
        command=open_booking
    ).pack(side="left", padx=(0, 12))

    ctk.CTkButton(
        buttons,
        text="Đóng",
        width=120,
        height=48,
        corner_radius=14,
        fg_color="#E5E7EB",
        hover_color="#D1D5DB",
        text_color=TEXT,
        font=("Arial", 14, "bold"),
        command=win.destroy
    ).pack(side="left")
