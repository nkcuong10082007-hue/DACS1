import customtkinter as ctk


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = "#F5F6FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
ORANGE = "#F58220"
BORDER = "#E5E7EB"


def open_on_top(win):
    try:
        win.state("zoomed")
    except Exception:
        win.geometry(f"{win.winfo_screenwidth()}x{win.winfo_screenheight()}+0+0")

    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.after(700, lambda: win.attributes("-topmost", False))


def offers_screen(parent=None):
    win = ctk.CTkToplevel(parent)
    win.title("Ưu đãi")
    win.configure(fg_color=BG)
    open_on_top(win)

    header = ctk.CTkFrame(win, fg_color=CARD, corner_radius=0, border_width=1, border_color=BORDER)
    header.pack(fill="x")

    ctk.CTkLabel(
        header,
        text="ƯU ĐÃI THÀNH VIÊN",
        text_color=ORANGE,
        font=("Arial", 30, "bold")
    ).pack(anchor="w", padx=40, pady=(24, 4))

    ctk.CTkLabel(
        header,
        text="Khu vực quản lý và hiển thị ưu đãi. Nội dung chi tiết sẽ được bổ sung sau.",
        text_color=MUTED,
        font=("Arial", 13)
    ).pack(anchor="w", padx=40, pady=(0, 24))

    body = ctk.CTkFrame(win, fg_color=BG)
    body.pack(fill="both", expand=True, padx=40, pady=36)

    empty_card = ctk.CTkFrame(body, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
    empty_card.pack(fill="both", expand=True)

    ctk.CTkLabel(
        empty_card,
        text="Màn ưu đãi đang chờ thiết kế nội dung",
        text_color=TEXT,
        font=("Arial", 22, "bold")
    ).pack(pady=(120, 10))

    ctk.CTkLabel(
        empty_card,
        text="Sau này có thể thêm ảnh, mô tả ưu đãi, thời gian áp dụng và chức năng admin thêm/sửa/xóa.",
        text_color=MUTED,
        font=("Arial", 13),
        wraplength=620,
        justify="center"
    ).pack()
