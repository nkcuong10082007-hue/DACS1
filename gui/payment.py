import customtkinter as ctk
from tkinter import messagebox

import session
from database.db import add_payment


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

def payment_screen(movie_name, show_date, show_time, seats, ticket_price, on_success=None):
    win = ctk.CTkToplevel()
    open_on_top(win)
    win.title("Thanh toán")
    win.geometry("560x660")
    win.resizable(False, False)
    win.configure(fg_color=BG)
    win.grab_set()
    open_on_top(win)

    try:
        ticket_price = int(ticket_price)
    except Exception:
        ticket_price = 90000

    total = len(seats) * ticket_price
    method = ctk.StringVar(value="Tiền mặt")

    ctk.CTkLabel(
        win,
        text="THANH TOÁN",
        text_color=PRIMARY,
        font=("Arial", 28, "bold")
    ).pack(pady=(26, 8))

    ctk.CTkLabel(
        win,
        text="Kiểm tra thông tin vé trước khi xác nhận",
        text_color=MUTED,
        font=("Arial", 12)
    ).pack(pady=(0, 18))

    info_card = ctk.CTkFrame(
        win,
        fg_color=CARD,
        corner_radius=18,
        border_width=1,
        border_color=BORDER
    )
    info_card.pack(padx=30, fill="x")

    def info_row(label, value, value_color=TEXT):
        row = ctk.CTkFrame(info_card, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=5)

        ctk.CTkLabel(
            row,
            text=label,
            text_color=MUTED,
            font=("Arial", 12, "bold"),
            width=95,
            anchor="w"
        ).pack(side="left", anchor="n")

        ctk.CTkLabel(
            row,
            text=value,
            text_color=value_color,
            font=("Arial", 12),
            wraplength=340,
            justify="left",
            anchor="w"
        ).pack(side="left", fill="x", expand=True, anchor="n")

    ctk.CTkLabel(
        info_card,
        text="Thông tin đặt vé",
        text_color=PRIMARY,
        font=("Arial", 16, "bold")
    ).pack(anchor="w", padx=22, pady=(20, 8))

    info_row("Phim:", movie_name)
    info_row("Ngày:", show_date)
    info_row("Suất:", show_time)
    info_row("Ghế:", ", ".join(seats))
    info_row("Giá vé:", f"{ticket_price:,} VNĐ / ghế")
    info_row("Tổng:", f"{total:,} VNĐ", PRIMARY)

    ctk.CTkFrame(info_card, fg_color=BORDER, height=1).pack(fill="x", padx=22, pady=(12, 10))

    ctk.CTkLabel(
        info_card,
        text="Phương thức thanh toán",
        text_color=TEXT,
        font=("Arial", 14, "bold")
    ).pack(anchor="w", padx=22, pady=(0, 8))

    method_frame = ctk.CTkFrame(info_card, fg_color="transparent")
    method_frame.pack(fill="x", padx=18, pady=(0, 20))

    for item in ["Tiền mặt", "Momo", "Ngân hàng"]:
        ctk.CTkRadioButton(
            method_frame,
            text=item,
            variable=method,
            value=item,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            border_color="#9CA3AF",
            text_color=TEXT,
            font=("Arial", 12)
        ).pack(anchor="w", padx=6, pady=5)

    button_frame = ctk.CTkFrame(win, fg_color="transparent")
    button_frame.pack(pady=26)

    def confirm_payment():
        if not session.is_logged_in():
            messagebox.showwarning("Thông báo", "Phiên đăng nhập không hợp lệ")
            win.destroy()
            return

        ticket_code = add_payment(
            session.current_user[0],
            movie_name,
            show_date,
            show_time,
            ", ".join(seats),
            total,
            method.get()
        )

        win.destroy()

        if on_success:
            on_success()

        messagebox.showinfo("Thanh toán thành công", f"Mã vé của bạn: {ticket_code}")

    ctk.CTkButton(
        button_frame,
        text="XÁC NHẬN THANH TOÁN",
        width=245,
        height=46,
        corner_radius=14,
        fg_color=GREEN,
        hover_color=GREEN_HOVER,
        text_color="white",
        font=("Arial", 13, "bold"),
        command=confirm_payment
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        button_frame,
        text="Hủy",
        width=100,
        height=46,
        corner_radius=14,
        fg_color="#E5E7EB",
        hover_color="#D1D5DB",
        text_color=TEXT,
        font=("Arial", 13, "bold"),
        command=win.destroy
    ).pack(side="left", padx=8)
