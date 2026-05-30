import customtkinter as ctk

from database.db import search_movies


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = "#F5F6FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
PRIMARY = "#E50914"
PRIMARY_HOVER = "#B20710"
BORDER = "#E5E7EB"

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


def search_screen():
    win = ctk.CTkToplevel()
    open_on_top(win)
    win.title("Tìm kiếm")
    win.geometry("560x480")
    win.configure(fg_color=BG)
    open_on_top(win)

    ctk.CTkLabel(
        win,
        text="Tìm kiếm phim",
        text_color=PRIMARY,
        font=("Arial", 24, "bold")
    ).pack(pady=(26, 6))

    ctk.CTkLabel(
        win,
        text="Tìm theo tên phim, thể loại, đạo diễn hoặc diễn viên",
        text_color=MUTED,
        font=("Arial", 12)
    ).pack(pady=(0, 18))

    entry = ctk.CTkEntry(
        win,
        width=440,
        height=42,
        corner_radius=12,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập từ khóa tìm kiếm...",
        placeholder_text_color="#9CA3AF",
        font=("Arial", 13)
    )
    entry.pack(pady=(0, 12))

    result_frame = ctk.CTkScrollableFrame(
        win,
        width=460,
        height=240,
        fg_color=CARD,
        corner_radius=16,
        border_width=1,
        border_color=BORDER,
        scrollbar_button_color="#D1D5DB",
        scrollbar_button_hover_color="#9CA3AF"
    )
    result_frame.pack(pady=8)

    def clear_results():
        for widget in result_frame.winfo_children():
            widget.destroy()

    def add_result(movie):
        card = ctk.CTkFrame(
            result_frame,
            fg_color="#F9FAFB",
            corner_radius=12,
            border_width=1,
            border_color=BORDER
        )
        card.pack(fill="x", padx=6, pady=6)

        ctk.CTkLabel(
            card,
            text=movie[1],
            text_color=TEXT,
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            card,
            text=f"{movie[2]} • {movie[3]} phút",
            text_color=PRIMARY,
            font=("Arial", 11, "bold"),
            anchor="w"
        ).pack(fill="x", padx=14, pady=(0, 10))

    def search():
        clear_results()

        keyword = entry.get().strip()
        if not keyword:
            ctk.CTkLabel(
                result_frame,
                text="Vui lòng nhập từ khóa tìm kiếm",
                text_color=MUTED,
                font=("Arial", 12)
            ).pack(pady=30)
            return

        movies = search_movies(keyword)

        if not movies:
            ctk.CTkLabel(
                result_frame,
                text="Không tìm thấy phim phù hợp",
                text_color=MUTED,
                font=("Arial", 12)
            ).pack(pady=30)
            return

        for movie in movies:
            add_result(movie)

    ctk.CTkButton(
        win,
        text="Tìm",
        width=120,
        height=42,
        corner_radius=12,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="white",
        font=("Arial", 12, "bold"),
        command=search
    ).pack(pady=12)

    entry.bind("<Return>", lambda e: search())
