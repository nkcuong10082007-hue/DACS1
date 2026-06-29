import random
import customtkinter as ctk
from tkinter import messagebox

from hide import session
from database.db import (
    add_user,
    check_login,
    get_reset_contact,
    verify_reset_contact,
    update_password,
)


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = "#F5F6FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
PRIMARY = "#F58220"
PRIMARY_HOVER = "#E66F00"
BLUE = "#005BAC"
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


def login_screen(parent, on_success=None):
    win = ctk.CTkToplevel(parent)
    win.title("Đăng nhập")
    win.configure(fg_color=BG)
    win.grab_set()
    open_on_top(win)

    mode = ctk.StringVar(value="login")

    page = ctk.CTkScrollableFrame(
        win,
        fg_color=BG,
        scrollbar_button_color="#D1D5DB",
        scrollbar_button_hover_color="#9CA3AF"
    )
    page.pack(fill="both", expand=True)

    container = ctk.CTkFrame(page, fg_color="transparent")
    container.pack(pady=60)

    ctk.CTkLabel(
        container,
        text="MOVIE APP",
        text_color=BLUE,
        font=("Arial", 34, "bold")
    ).pack()

    subtitle = ctk.CTkLabel(
        container,
        text="Đăng nhập để tiếp tục",
        text_color=MUTED,
        font=("Arial", 14)
    )
    subtitle.pack(pady=(6, 24))

    form_frame = ctk.CTkFrame(
        container,
        fg_color=CARD,
        corner_radius=20,
        border_width=1,
        border_color=BORDER
    )
    form_frame.pack(padx=34, pady=(0, 26))

    title_label = ctk.CTkLabel(
        form_frame,
        text="Đăng nhập",
        text_color=TEXT,
        font=("Arial", 22, "bold")
    )
    title_label.pack(padx=52, pady=(28, 20))

    def field_label(text):
        ctk.CTkLabel(
            form_frame,
            text=text,
            text_color=MUTED,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=52)

    field_label("Tài khoản")
    entry_user = ctk.CTkEntry(
        form_frame,
        width=420,
        height=42,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập tài khoản",
        placeholder_text_color="#9CA3AF",
        font=("Arial", 13)
    )
    entry_user.pack(padx=52, pady=(5, 14))

    field_label("Mật khẩu")
    entry_pass = ctk.CTkEntry(
        form_frame,
        width=420,
        height=42,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập mật khẩu",
        placeholder_text_color="#9CA3AF",
        show="*",
        font=("Arial", 13)
    )
    entry_pass.pack(padx=52, pady=(5, 12))

    register_extra = ctk.CTkFrame(form_frame, fg_color="transparent")

    ctk.CTkLabel(
        register_extra,
        text="Email",
        text_color=MUTED,
        font=("Arial", 12, "bold")
    ).pack(anchor="w", padx=52)

    email_entry = ctk.CTkEntry(
        register_extra,
        width=420,
        height=42,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập email nếu dùng email để khôi phục",
        placeholder_text_color="#9CA3AF",
        font=("Arial", 13)
    )
    email_entry.pack(padx=52, pady=(5, 12))

    ctk.CTkLabel(
        register_extra,
        text="Số điện thoại",
        text_color=MUTED,
        font=("Arial", 12, "bold")
    ).pack(anchor="w", padx=52)

    phone_entry = ctk.CTkEntry(
        register_extra,
        width=420,
        height=42,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập số điện thoại nếu dùng SĐT để khôi phục",
        placeholder_text_color="#9CA3AF",
        font=("Arial", 13)
    )
    phone_entry.pack(padx=52, pady=(5, 8))

    msg_label = ctk.CTkLabel(
        form_frame,
        text="",
        text_color="#DC2626",
        font=("Arial", 12),
        wraplength=420
    )
    msg_label.pack(padx=52, pady=(0, 8))

    def clear_entries():
        entry_user.delete(0, "end")
        entry_pass.delete(0, "end")
        email_entry.delete(0, "end")
        phone_entry.delete(0, "end")

    def submit():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()

        if not username or not password:
            msg_label.configure(text="Vui lòng nhập tài khoản và mật khẩu")
            return

        if mode.get() == "login":
            user = check_login(username, password)

            if user:
                session.login(user)
                win.destroy()
                if on_success:
                    on_success()
            else:
                msg_label.configure(text="Sai tài khoản hoặc mật khẩu")
            return

        email = email_entry.get().strip()
        phone = phone_entry.get().strip()

        if len(password) < 6:
            msg_label.configure(text="Mật khẩu tối thiểu 6 ký tự")
            return

        if bool(email) == bool(phone):
            msg_label.configure(text="Chỉ được nhập email hoặc số điện thoại, không nhập cả hai")
            return

        if add_user(username, password, email=email or None, phone=phone or None):
            messagebox.showinfo("Thành công", "Đăng ký thành công. Hãy đăng nhập.")
            toggle_mode()
        else:
            msg_label.configure(text="Tài khoản/email/số điện thoại đã tồn tại hoặc không hợp lệ")

    btn_submit = ctk.CTkButton(
        form_frame,
        text="ĐĂNG NHẬP",
        width=420,
        height=44,
        corner_radius=12,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="white",
        font=("Arial", 13, "bold"),
        command=submit
    )
    btn_submit.pack(padx=52, pady=(4, 10))

    forgot_btn = ctk.CTkButton(
        form_frame,
        text="Quên mật khẩu?",
        fg_color="transparent",
        hover_color="#F3F4F6",
        text_color=BLUE,
        font=("Arial", 12, "bold"),
        command=lambda: forgot_password_screen(win)
    )
    forgot_btn.pack(padx=52, pady=(0, 6))

    def toggle_mode():
        msg_label.configure(text="")
        clear_entries()

        if mode.get() == "login":
            mode.set("register")
            title_label.configure(text="Đăng ký")
            subtitle.configure(text="Tạo tài khoản mới")
            btn_submit.configure(text="ĐĂNG KÝ")
            toggle_btn.configure(text="Đã có tài khoản? Đăng nhập")
            forgot_btn.pack_forget()
            register_extra.pack(before=msg_label, fill="x")
        else:
            mode.set("login")
            title_label.configure(text="Đăng nhập")
            subtitle.configure(text="Đăng nhập để tiếp tục")
            btn_submit.configure(text="ĐĂNG NHẬP")
            toggle_btn.configure(text="Chưa có tài khoản? Đăng ký")
            register_extra.pack_forget()
            forgot_btn.pack(after=btn_submit, padx=52, pady=(0, 6))

    toggle_btn = ctk.CTkButton(
        form_frame,
        text="Chưa có tài khoản? Đăng ký",
        fg_color="transparent",
        hover_color="#F3F4F6",
        text_color=BLUE,
        font=("Arial", 12),
        command=toggle_mode
    )
    toggle_btn.pack(padx=52, pady=(0, 24))

    win.bind("<Return>", lambda e: submit())


def forgot_password_screen(parent):
    win = ctk.CTkToplevel(parent)
    win.title("Quên mật khẩu")
    win.configure(fg_color=BG)
    win.grab_set()
    open_on_top(win)

    otp_code = ctk.StringVar(value="")
    current_username = ctk.StringVar(value="")
    contact_type = ctk.StringVar(value="")

    page = ctk.CTkScrollableFrame(
        win,
        fg_color=BG,
        scrollbar_button_color="#D1D5DB",
        scrollbar_button_hover_color="#9CA3AF"
    )
    page.pack(fill="both", expand=True)

    box = ctk.CTkFrame(
        page,
        fg_color=CARD,
        corner_radius=20,
        border_width=1,
        border_color=BORDER
    )
    box.pack(pady=60)

    ctk.CTkLabel(
        box,
        text="QUÊN MẬT KHẨU",
        text_color=BLUE,
        font=("Arial", 26, "bold")
    ).pack(padx=60, pady=(28, 8))

    ctk.CTkLabel(
        box,
        text="Nhập tài khoản trước, sau đó xác minh email hoặc số điện thoại đã liên kết.",
        text_color=MUTED,
        font=("Arial", 12),
        wraplength=440,
        justify="center"
    ).pack(padx=60, pady=(0, 20))

    ctk.CTkLabel(
        box,
        text="Tên tài khoản",
        text_color=MUTED,
        font=("Arial", 12, "bold")
    ).pack(anchor="w", padx=60)

    username_entry = ctk.CTkEntry(
        box,
        width=440,
        height=42,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập tên tài khoản",
        placeholder_text_color="#9CA3AF",
        font=("Arial", 13)
    )
    username_entry.pack(padx=60, pady=(5, 12))

    msg_label = ctk.CTkLabel(
        box,
        text="",
        text_color="#DC2626",
        font=("Arial", 12),
        wraplength=440
    )
    msg_label.pack(padx=60, pady=(0, 8))

    contact_hint = ctk.CTkLabel(
        box,
        text="",
        text_color=TEXT,
        font=("Arial", 12),
        wraplength=440,
        justify="left"
    )

    contact_entry = ctk.CTkEntry(
        box,
        width=440,
        height=42,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập email hoặc số điện thoại",
        placeholder_text_color="#9CA3AF",
        font=("Arial", 13)
    )

    otp_entry = ctk.CTkEntry(
        box,
        width=440,
        height=42,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập mã OTP",
        placeholder_text_color="#9CA3AF",
        font=("Arial", 13)
    )

    new_pass_entry = ctk.CTkEntry(
        box,
        width=440,
        height=42,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Nhập mật khẩu mới",
        placeholder_text_color="#9CA3AF",
        show="*",
        font=("Arial", 13)
    )

    def check_username():
        username = username_entry.get().strip()

        if not username:
            msg_label.configure(text="Vui lòng nhập tên tài khoản")
            return

        reset_contact = get_reset_contact(username)

        if not reset_contact:
            msg_label.configure(text="Tài khoản không tồn tại hoặc chưa liên kết email/số điện thoại")
            return

        msg_label.configure(text="")
        current_username.set(username)
        contact_type.set(reset_contact["type"])

        username_entry.configure(state="disabled")
        check_user_btn.configure(state="disabled")

        if reset_contact["type"] == "email":
            contact_hint.configure(
                text=f"Vui lòng nhập đúng email {reset_contact['masked']} để đổi mật khẩu"
            )
        else:
            contact_hint.configure(
                text=f"Vui lòng nhập đúng số điện thoại {reset_contact['masked']} để đổi mật khẩu"
            )

        contact_hint.pack(anchor="w", padx=60, pady=(6, 6))
        contact_entry.pack(padx=60, pady=(0, 12))
        verify_contact_btn.pack(padx=60, pady=(0, 10))

    check_user_btn = ctk.CTkButton(
        box,
        text="Xác nhận tài khoản",
        width=440,
        height=42,
        corner_radius=12,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="white",
        font=("Arial", 13, "bold"),
        command=check_username
    )
    check_user_btn.pack(padx=60, pady=(0, 12))

    def verify_contact():
        contact_value = contact_entry.get().strip()

        if not contact_value:
            msg_label.configure(text="Vui lòng nhập thông tin xác minh")
            return

        if not verify_reset_contact(current_username.get(), contact_value):
            msg_label.configure(text="Thông tin xác minh không đúng")
            return

        msg_label.configure(text="")
        contact_entry.configure(state="disabled")
        verify_contact_btn.configure(state="disabled")

        code = str(random.randint(100000, 999999))
        otp_code.set(code)

        messagebox.showinfo("OTP demo", f"Mã OTP demo của bạn là: {code}")

        otp_entry.pack(padx=60, pady=(4, 12))
        new_pass_entry.pack(padx=60, pady=(0, 12))
        reset_btn.pack(padx=60, pady=(0, 12))

    verify_contact_btn = ctk.CTkButton(
        box,
        text="Gửi OTP demo",
        width=440,
        height=42,
        corner_radius=12,
        fg_color=BLUE,
        hover_color="#004A8F",
        text_color="white",
        font=("Arial", 13, "bold"),
        command=verify_contact
    )

    def reset_password():
        otp = otp_entry.get().strip()
        new_password = new_pass_entry.get().strip()

        if otp != otp_code.get():
            msg_label.configure(text="Mã OTP không đúng")
            return

        if len(new_password) < 6:
            msg_label.configure(text="Mật khẩu mới tối thiểu 6 ký tự")
            return

        if update_password(current_username.get(), new_password):
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công. Hãy đăng nhập lại.")
            win.destroy()
        else:
            msg_label.configure(text="Không thể cập nhật mật khẩu")

    reset_btn = ctk.CTkButton(
        box,
        text="Xác nhận đổi mật khẩu",
        width=440,
        height=42,
        corner_radius=12,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="white",
        font=("Arial", 13, "bold"),
        command=reset_password
    )

    ctk.CTkButton(
        box,
        text="Đóng",
        width=120,
        height=38,
        corner_radius=12,
        fg_color="#E5E7EB",
        hover_color="#D1D5DB",
        text_color=TEXT,
        font=("Arial", 12, "bold"),
        command=win.destroy
    ).pack(padx=60, pady=(4, 28))
