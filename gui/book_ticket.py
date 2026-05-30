import customtkinter as ctk
from tkinter import messagebox

import session
from database.db import add_booking, get_booked_seats
from gui.payment import payment_screen


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = "#F5F6FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
PRIMARY = "#E50914"
PRIMARY_HOVER = "#B20710"
BORDER = "#E5E7EB"
GREEN = "#00A86B"
GREEN_HOVER = "#008F5A"

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

def book_ticket_screen(movie_name, movie_dates, movie_times, ticket_price):
    win = ctk.CTkToplevel()
    open_on_top(win)
    win.title("Đặt vé")
    win.geometry("940x760")
    win.configure(fg_color=BG)
    win.transient()
    win.grab_set()
    open_on_top(win)

    dates = [d.strip() for d in movie_dates.split(",") if d.strip()]
    times = [t.strip() for t in movie_times.split(",") if t.strip()]

    if not dates or not times:
        messagebox.showwarning("Thông báo", "Phim này chưa có lịch chiếu")
        win.destroy()
        return

    try:
        ticket_price = int(ticket_price)
    except Exception:
        ticket_price = 90000

    selected_date = ctk.StringVar(value=dates[0])
    selected_time = ctk.StringVar(value=times[0])
    selected = []

    ctk.CTkLabel(
        win,
        text=f"Đặt vé - {movie_name}",
        text_color=PRIMARY,
        font=("Arial", 26, "bold"),
        wraplength=820
    ).pack(pady=(24, 8))

    ctk.CTkLabel(
        win,
        text=f"Giá vé: {ticket_price:,} VNĐ / ghế",
        text_color=PRIMARY,
        font=("Arial", 14, "bold")
    ).pack(pady=(0, 14))

    option_frame = ctk.CTkFrame(win, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
    option_frame.pack(padx=28, pady=(0, 16), fill="x")

    ctk.CTkLabel(
        option_frame,
        text="Ngày chiếu",
        text_color=MUTED,
        font=("Arial", 12, "bold")
    ).grid(row=0, column=0, padx=(22, 8), pady=(18, 6), sticky="w")

    ctk.CTkLabel(
        option_frame,
        text="Suất chiếu",
        text_color=MUTED,
        font=("Arial", 12, "bold")
    ).grid(row=0, column=1, padx=8, pady=(18, 6), sticky="w")

    date_menu = ctk.CTkOptionMenu(
        option_frame,
        variable=selected_date,
        values=dates,
        width=190,
        height=40,
        corner_radius=10,
        fg_color="#F9FAFB",
        button_color=PRIMARY,
        button_hover_color=PRIMARY_HOVER,
        dropdown_fg_color=CARD,
        dropdown_hover_color="#F3F4F6",
        text_color=TEXT,
        font=("Arial", 12),
        command=lambda value: load_seats()
    )
    date_menu.grid(row=1, column=0, padx=(22, 8), pady=(0, 18), sticky="w")

    time_menu = ctk.CTkOptionMenu(
        option_frame,
        variable=selected_time,
        values=times,
        width=190,
        height=40,
        corner_radius=10,
        fg_color="#F9FAFB",
        button_color=PRIMARY,
        button_hover_color=PRIMARY_HOVER,
        dropdown_fg_color=CARD,
        dropdown_hover_color="#F3F4F6",
        text_color=TEXT,
        font=("Arial", 12),
        command=lambda value: load_seats()
    )
    time_menu.grid(row=1, column=1, padx=8, pady=(0, 18), sticky="w")

    summary_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
    summary_frame.grid(row=0, column=2, rowspan=2, padx=(24, 22), pady=14, sticky="e")

    remain_label = ctk.CTkLabel(
        summary_frame,
        text="",
        text_color=MUTED,
        font=("Arial", 14, "bold")
    )
    remain_label.pack(anchor="e", pady=(4, 3))

    total_label = ctk.CTkLabel(
        summary_frame,
        text="Tổng tiền: 0 VNĐ",
        text_color=PRIMARY,
        font=("Arial", 16, "bold")
    )
    total_label.pack(anchor="e", pady=(3, 4))

    option_frame.grid_columnconfigure(2, weight=1)

    screen_frame = ctk.CTkFrame(win, fg_color="transparent")
    screen_frame.pack(fill="x", padx=70, pady=(2, 12))

    ctk.CTkFrame(
        screen_frame,
        fg_color="#D1D5DB",
        corner_radius=18,
        height=38
    ).pack(fill="x")

    ctk.CTkLabel(
        screen_frame,
        text="MÀN HÌNH",
        text_color=MUTED,
        font=("Arial", 11, "bold")
    ).pack(pady=(6, 0))

    seat_container = ctk.CTkFrame(win, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
    seat_container.pack(pady=(4, 12), padx=28)

    seat_frame = ctk.CTkFrame(seat_container, fg_color="transparent")
    seat_frame.pack(padx=22, pady=22)

    legend = ctk.CTkFrame(win, fg_color="transparent")
    legend.pack(pady=(0, 14))

    def legend_item(color, text, text_color=TEXT):
        item = ctk.CTkFrame(legend, fg_color="transparent")
        item.pack(side="left", padx=14)

        ctk.CTkFrame(item, fg_color=color, width=24, height=16, corner_radius=5).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            item,
            text=text,
            text_color=text_color,
            font=("Arial", 11)
        ).pack(side="left")

    legend_item("#E5E7EB", "Còn trống")
    legend_item(GREEN, "Đang chọn")
    legend_item("#9CA3AF", "Đã đặt", MUTED)

    def update_total():
        total_label.configure(text=f"Tổng tiền: {len(selected) * ticket_price:,} VNĐ")

    def load_seats():
        selected.clear()
        update_total()

        for widget in seat_frame.winfo_children():
            widget.destroy()

        booked = get_booked_seats(movie_name, selected_date.get(), selected_time.get())
        total_seats = 40
        remain = total_seats - len(booked)
        remain_label.configure(text=f"Vé còn lại: {remain}/{total_seats}")

        for r in range(5):
            row_label = ctk.CTkLabel(
                seat_frame,
                text=chr(65 + r),
                text_color=MUTED,
                font=("Arial", 12, "bold"),
                width=28
            )
            row_label.grid(row=r, column=0, padx=(0, 8), pady=6)

            for c in range(8):
                seat = f"{chr(65 + r)}{c + 1}"

                btn = ctk.CTkButton(
                    seat_frame,
                    text=seat,
                    width=58,
                    height=38,
                    corner_radius=10,
                    fg_color="#E5E7EB",
                    hover_color="#D1D5DB",
                    text_color=TEXT,
                    font=("Arial", 11, "bold")
                )
                btn.grid(row=r, column=c + 1, padx=5, pady=6)

                if seat in booked:
                    btn.configure(
                        fg_color="#9CA3AF",
                        hover_color="#9CA3AF",
                        text_color="#F9FAFB",
                        state="disabled"
                    )
                else:
                    def choose(button=btn, seat_code=seat):
                        if seat_code in selected:
                            selected.remove(seat_code)
                            button.configure(fg_color="#E5E7EB", hover_color="#D1D5DB", text_color=TEXT)
                        else:
                            selected.append(seat_code)
                            button.configure(fg_color=GREEN, hover_color=GREEN_HOVER, text_color="white")

                        update_total()

                    btn.configure(command=choose)

    def confirm():
        if not session.is_logged_in():
            messagebox.showwarning("Thông báo", "Vui lòng đăng nhập để đặt vé")
            return

        if not selected:
            messagebox.showwarning("Lỗi", "Bạn chưa chọn ghế")
            return

        latest_booked = get_booked_seats(movie_name, selected_date.get(), selected_time.get())
        duplicated = [seat for seat in selected if seat in latest_booked]

        if duplicated:
            messagebox.showwarning(
                "Ghế đã được đặt",
                f"Ghế {', '.join(duplicated)} đã có người đặt"
            )
            load_seats()
            return

        def on_payment_success():
            user_id = session.current_user[0]

            for seat in selected:
                add_booking(user_id, movie_name, selected_date.get(), selected_time.get(), seat)

            messagebox.showinfo("Thành công", "Đặt vé thành công")
            load_seats()

        payment_screen(
            movie_name,
            selected_date.get(),
            selected_time.get(),
            list(selected),
            ticket_price,
            on_success=on_payment_success
        )

    action_frame = ctk.CTkFrame(win, fg_color="transparent")
    action_frame.pack(pady=(0, 22))

    ctk.CTkButton(
        action_frame,
        text="Xác nhận đặt vé",
        width=190,
        height=46,
        corner_radius=14,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="white",
        font=("Arial", 13, "bold"),
        command=confirm
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        action_frame,
        text="Đóng",
        width=110,
        height=46,
        corner_radius=14,
        fg_color="#E5E7EB",
        hover_color="#D1D5DB",
        text_color=TEXT,
        font=("Arial", 13, "bold"),
        command=win.destroy
    ).pack(side="left", padx=8)

    load_seats()
