import customtkinter as ctk
from tkinter import messagebox

import session
from database.db import get_payments


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = "#F5F6FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
PRIMARY = "#E50914"
BORDER = "#E5E7EB"
GREEN = "#00A86B"

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

def my_tickets_screen(parent=None):
    if not session.is_logged_in():
        messagebox.showwarning("Thông báo", "Vui lòng đăng nhập để xem vé")
        return

    win = ctk.CTkToplevel(parent)
    open_on_top(win)
    win.title("Vé của tôi")
    win.geometry("940x740")
    win.configure(fg_color=BG)
    open_on_top(win)

    header = ctk.CTkFrame(win, fg_color="transparent")
    header.pack(fill="x", padx=28, pady=(24, 12))

    ctk.CTkLabel(
        header,
        text="VÉ ĐÃ MUA",
        text_color=PRIMARY,
        font=("Arial", 28, "bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        header,
        text="Danh sách vé và lịch chiếu của bạn",
        text_color=MUTED,
        font=("Arial", 12)
    ).pack(anchor="w", pady=(4, 0))

    main = ctk.CTkScrollableFrame(
        win,
        fg_color=BG,
        scrollbar_button_color="#D1D5DB",
        scrollbar_button_hover_color="#9CA3AF"
    )
    main.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    payments = get_payments(session.current_user[0])

    if not payments:
        empty_card = ctk.CTkFrame(
            main,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )
        empty_card.pack(fill="x", padx=8, pady=30)

        ctk.CTkLabel(
            empty_card,
            text="Bạn chưa có vé nào",
            text_color=TEXT,
            font=("Arial", 18, "bold")
        ).pack(pady=(32, 6))

        ctk.CTkLabel(
            empty_card,
            text="Hãy chọn một bộ phim yêu thích và đặt vé để bắt đầu.",
            text_color=MUTED,
            font=("Arial", 12)
        ).pack(pady=(0, 32))
        return

    def safe_text(value, fallback="Chưa có"):
        return value if value not in (None, "") else fallback

    for pay in payments:
        ticket_code = pay[9] if len(pay) > 9 and pay[9] else f"TICKET-{pay[0]}"
        show_time = pay[8] if len(pay) > 8 and pay[8] else "Chưa có"
        status = pay[10] if len(pay) > 10 and pay[10] else "Đã thanh toán"
        created_at = pay[7] if len(pay) > 7 and pay[7] else ""

        try:
            total_display = f"{int(pay[5]):,} VNĐ"
        except Exception:
            total_display = f"{pay[5]} VNĐ"

        card = ctk.CTkFrame(
            main,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )
        card.pack(fill="x", padx=8, pady=10)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 8))

        left_top = ctk.CTkFrame(top, fg_color="transparent")
        left_top.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_top,
            text=safe_text(pay[2]),
            text_color=PRIMARY,
            font=("Arial", 18, "bold"),
            wraplength=620,
            justify="left"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_top,
            text=f"Mã vé: {ticket_code}",
            text_color="#F59E0B",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(4, 0))

        status_badge = ctk.CTkFrame(
            top,
            fg_color="#DCFCE7" if status == "Đã thanh toán" else "#F3F4F6",
            corner_radius=999
        )
        status_badge.pack(side="right", padx=(12, 0), anchor="n")

        ctk.CTkLabel(
            status_badge,
            text=status,
            text_color=GREEN if status == "Đã thanh toán" else MUTED,
            font=("Arial", 11, "bold")
        ).pack(padx=12, pady=6)

        ctk.CTkFrame(card, fg_color=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 10))

        detail = ctk.CTkFrame(card, fg_color="transparent")
        detail.pack(fill="x", padx=20, pady=(0, 16))

        def detail_row(parent, label, value, color=TEXT):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row,
                text=label,
                text_color=MUTED,
                font=("Arial", 12, "bold"),
                width=105,
                anchor="w"
            ).pack(side="left", anchor="n")

            ctk.CTkLabel(
                row,
                text=value,
                text_color=color,
                font=("Arial", 12),
                anchor="w",
                wraplength=700,
                justify="left"
            ).pack(side="left", fill="x", expand=True, anchor="n")

        detail_row(detail, "Ngày chiếu:", safe_text(pay[3]))
        detail_row(detail, "Suất chiếu:", safe_text(show_time))
        detail_row(detail, "Ghế:", safe_text(pay[4]))
        detail_row(detail, "Tổng tiền:", total_display, PRIMARY)
        detail_row(detail, "Thanh toán:", safe_text(pay[6]), GREEN)

        if created_at:
            detail_row(detail, "Thời gian:", created_at, MUTED)
