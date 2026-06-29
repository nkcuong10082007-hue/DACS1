import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageOps

from hide import session
from database.db import get_movies, delete_movie, search_movies
from gui.movie_detail import show_detail
from gui.my_tickets import my_tickets_screen
from gui.content_pages import show_content_list
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG = "#F5F6FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
PRIMARY = "#F58220"
PRIMARY_HOVER = "#E66F00"
BORDER = "#E5E7EB"
GREEN = "#00A86B"
GREEN_HOVER = "#008F5A"
PURPLE = "#7C3AED"
PURPLE_HOVER = "#6D28D9"


def fit_image(path, size):
    img = Image.open(path).convert("RGB")
    img = ImageOps.contain(img, size)
    canvas = Image.new("RGB", size, "#F3F4F6")
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def home_screen():
    root = ctk.CTk()
    root.title("Movie App")
    root.configure(fg_color=BG)

    def maximize_root():
        try:
            root.state("zoomed")
        except Exception:
            root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

    root.after(100, maximize_root)

    header = ctk.CTkFrame(root, fg_color=CARD, height=78, corner_radius=0, border_width=1, border_color=BORDER)
    header.pack(fill="x")
    header.pack_propagate(False)

    left_header = ctk.CTkFrame(header, fg_color="transparent")
    left_header.pack(side="left", padx=28, pady=13)

    ctk.CTkLabel(
        left_header,
        text="MOVIE APP",
        text_color=PRIMARY,
        font=("Arial", 28, "bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        left_header,
        text="Đặt vé xem phim nhanh chóng",
        text_color=MUTED,
        font=("Arial", 12)
    ).pack(anchor="w", pady=(2, 0))
    nav_frame = ctk.CTkFrame(header, fg_color="transparent")
    nav_frame.pack(side="left", padx=(20, 0), pady=18)

    def nav_button(text, command=None, fg_color="transparent", text_color=TEXT):
        return ctk.CTkButton(
            nav_frame,
            text=text,
            width=105,
            height=38,
            corner_radius=10,
            fg_color=fg_color,
            hover_color="#F3F4F6" if fg_color == "transparent" else PRIMARY_HOVER,
            text_color=text_color,
            font=("Arial", 12, "bold"),
            command=command
        )

    nav_button(
        "🎟 Mua vé",
        command=lambda: messagebox.showinfo("Mua vé", "Màn mua vé sẽ được làm ở bước tiếp theo."),
        fg_color=PRIMARY,
        text_color="white"
    ).pack(side="left", padx=4)
    nav_button(
        "Phim",
        command=lambda: go_to_movies()
    ).pack(side="left", padx=4)
    ctk.CTkButton(
        nav_frame,
        text="Ưu Đãi",
        width=92,
        height=38,
        fg_color="transparent",
        text_color="#111827",
        hover_color="#fff3e8",
        font=("Arial", 13, "bold"),
        command=lambda: show_content_list(
            root,
            "offer",
            "Ưu đãi thành viên",
            "Các ưu đãi đang được lấy trực tiếp từ database."
        )
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        nav_frame,
        text="Rạp",
        width=82,
        height=38,
        fg_color="transparent",
        text_color="#111827",
        hover_color="#fff3e8",
        font=("Arial", 13, "bold"),
        command=lambda: show_content_list(
            root,
            "cinema",
            "Rạp phim",
            "Danh sách rạp phim đang được lấy trực tiếp từ database."
        )
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        nav_frame,
        text="Rạp Đặc Biệt",
        width=120,
        height=38,
        fg_color="transparent",
        text_color="#111827",
        hover_color="#fff3e8",
        font=("Arial", 13, "bold"),
        command=lambda: show_content_list(
            root,
            "special",
            "Rạp đặc biệt",
            "Các phòng chiếu đặc biệt đang được lấy trực tiếp từ database."
        )
    ).pack(side="left", padx=6)
    command = lambda: show_content_list(
        root,
        "offer",
        "Ưu đãi thành viên",
        "Các ưu đãi đang được lấy trực tiếp từ database."
    )
    command = lambda: show_content_list(
        root,
        "cinema",
        "Rạp phim",
        "Danh sách rạp phim đang được lấy trực tiếp từ database."
    )
    command = lambda: show_content_list(
        root,
        "special",
        "Rạp đặc biệt",
        "Các phòng chiếu đặc biệt đang được lấy trực tiếp từ database."
    )

    right_header = ctk.CTkFrame(header, fg_color="transparent")
    right_header.pack(side="right", padx=28, pady=18)

    toolbar = ctk.CTkFrame(root, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
    toolbar.pack(fill="x", padx=24, pady=(18, 16))

    entry_search = ctk.CTkEntry(
        toolbar,
        width=450,
        height=42,
        corner_radius=12,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        placeholder_text="Tìm theo tên phim, thể loại, diễn viên, đạo diễn...",
        placeholder_text_color="#9CA3AF",
        font=("Arial", 13)
    )
    entry_search.pack(side="left", padx=(18, 8), pady=14)

    content = ctk.CTkFrame(root, fg_color=BG, corner_radius=0)
    content.pack(fill="both", expand=True)

    movie_frame = ctk.CTkScrollableFrame(
        content,
        fg_color=BG,
        scrollbar_button_color="#D1D5DB",
        scrollbar_button_hover_color="#9CA3AF"
    )
    movie_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    def go_to_movies():
        entry_search.delete(0, "end")
        load_movies()
        movie_frame._parent_canvas.yview_moveto(0)
        entry_search.focus()

    def delete_and_reload(movie_id):
        if messagebox.askyesno("Xóa phim", "Bạn chắc chắn muốn xóa phim này?"):
            delete_movie(movie_id)
            load_movies()

    def open_edit(movie):
        from gui.edit_movie import edit_movie_screen
        edit_movie_screen(movie, load_movies)

    def get_movie_price(movie):
        if len(movie) > 10 and movie[10]:
            try:
                return f"{int(movie[10]):,} VNĐ"
            except Exception:
                return f"{movie[10]} VNĐ"
        return "90,000 VNĐ"

    def display_movies(movies):
        for widget in movie_frame.winfo_children():
            widget.destroy()

        if not movies:
            empty_box = ctk.CTkFrame(movie_frame, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
            empty_box.pack(fill="x", padx=20, pady=40)

            ctk.CTkLabel(
                empty_box,
                text="Không tìm thấy phim nào",
                text_color=TEXT,
                font=("Arial", 18, "bold")
            ).pack(pady=(30, 6))

            ctk.CTkLabel(
                empty_box,
                text="Thử tìm bằng tên phim, thể loại, đạo diễn hoặc diễn viên khác.",
                text_color=MUTED,
                font=("Arial", 12)
            ).pack(pady=(0, 30))
            return

        grid = ctk.CTkFrame(movie_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=8, pady=8, anchor="nw")

        cols = 5

        for idx, movie in enumerate(movies):
            row, col = divmod(idx, cols)

            card = ctk.CTkFrame(
                grid,
                fg_color=CARD,
                corner_radius=18,
                border_width=1,
                border_color=BORDER,
                width=220,
                height=398
            )
            card.grid(row=row, column=col, padx=12, pady=14, sticky="n")
            card.pack_propagate(False)

            def on_enter(event, c=card):
                c.configure(fg_color="#F9FAFB")

            def on_leave(event, c=card):
                c.configure(fg_color=CARD)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

            try:
                img = fit_image(movie[7], (150, 215))
                poster = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 215))

                poster_label = ctk.CTkLabel(card, image=poster, text="", cursor="hand2")
                poster_label.image = poster
                poster_label.pack(pady=(12, 8))
                poster_label.bind("<Button-1>", lambda e, m=movie: show_detail(m))
            except Exception:
                poster_placeholder = ctk.CTkFrame(
                    card,
                    fg_color="#F3F4F6",
                    corner_radius=12,
                    width=150,
                    height=215
                )
                poster_placeholder.pack(pady=(12, 8))
                poster_placeholder.pack_propagate(False)

                ctk.CTkLabel(
                    poster_placeholder,
                    text="Không có ảnh",
                    text_color=MUTED,
                    font=("Arial", 12, "bold")
                ).pack(expand=True)

            ctk.CTkLabel(
                card,
                text=movie[1],
                text_color=TEXT,
                font=("Arial", 14, "bold"),
                wraplength=180,
                justify="center"
            ).pack(padx=12, pady=(0, 5))

            ctk.CTkLabel(
                card,
                text=f"Thể loại: {movie[2]}",
                text_color=MUTED,
                font=("Arial", 11),
                wraplength=180
            ).pack(padx=12)

            ctk.CTkLabel(
                card,
                text=f"{movie[3]} phút • {get_movie_price(movie)}",
                text_color=PRIMARY,
                font=("Arial", 11, "bold"),
                wraplength=180
            ).pack(padx=12, pady=(3, 8))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(pady=(4, 12))

            ctk.CTkButton(
                btn_frame,
                text="Chi tiết",
                width=78,
                height=32,
                corner_radius=10,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                text_color="white",
                font=("Arial", 11, "bold"),
                command=lambda m=movie: show_detail(m)
            ).pack(side="left", padx=3)

            if session.is_admin():
                ctk.CTkButton(
                    btn_frame,
                    text="Sửa",
                    width=54,
                    height=32,
                    corner_radius=10,
                    fg_color="#2563EB",
                    hover_color="#1D4ED8",
                    text_color="white",
                    font=("Arial", 11, "bold"),
                    command=lambda m=movie: open_edit(m)
                ).pack(side="left", padx=3)

                ctk.CTkButton(
                    btn_frame,
                    text="Xóa",
                    width=54,
                    height=32,
                    corner_radius=10,
                    fg_color="#E5E7EB",
                    hover_color="#D1D5DB",
                    text_color=TEXT,
                    font=("Arial", 11, "bold"),
                    command=lambda mid=movie[0]: delete_and_reload(mid)
                ).pack(side="left", padx=3)

    def load_movies():
        display_movies(get_movies())

    def do_search():
        keyword = entry_search.get().strip()
        if keyword:
            display_movies(search_movies(keyword))
        else:
            load_movies()

    def reset_search():
        entry_search.delete(0, "end")
        load_movies()

    def rebuild_header():
        for widget in right_header.winfo_children():
            widget.destroy()

        for widget in toolbar.winfo_children():
            if widget != entry_search:
                widget.destroy()

        ctk.CTkButton(
            toolbar,
            text="Tìm",
            width=82,
            height=42,
            corner_radius=12,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color="white",
            font=("Arial", 12, "bold"),
            command=do_search
        ).pack(side="left", padx=5, pady=14)

        ctk.CTkButton(
            toolbar,
            text="Reset",
            width=82,
            height=42,
            corner_radius=12,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=TEXT,
            font=("Arial", 12, "bold"),
            command=reset_search
        ).pack(side="left", padx=5, pady=14)

        if session.is_logged_in():
            ctk.CTkLabel(
                right_header,
                text=f"Xin chào, {session.current_user[1]}",
                text_color=TEXT,
                font=("Arial", 13, "bold")
            ).pack(side="left", padx=(0, 12))

            ctk.CTkButton(
                right_header,
                text="Đăng xuất",
                width=100,
                height=36,
                corner_radius=10,
                fg_color="#E5E7EB",
                hover_color="#D1D5DB",
                text_color=TEXT,
                font=("Arial", 12, "bold"),
                command=lambda: (session.logout(), rebuild_header(), load_movies())
            ).pack(side="left")

            ctk.CTkButton(
                toolbar,
                text="Vé của tôi",
                width=110,
                height=42,
                corner_radius=12,
                fg_color=PURPLE,
                hover_color=PURPLE_HOVER,
                text_color="white",
                font=("Arial", 12, "bold"),
                command=lambda: my_tickets_screen(root)
            ).pack(side="left", padx=8, pady=14)

            if session.is_admin():
                def open_add():
                    from gui.add_movie import add_movie_screen
                    add_movie_screen(load_movies)

                ctk.CTkButton(
                    toolbar,
                    text="Thêm phim",
                    width=120,
                    height=42,
                    corner_radius=12,
                    fg_color=GREEN,
                    hover_color=GREEN_HOVER,
                    text_color="white",
                    font=("Arial", 12, "bold"),
                    command=open_add
                ).pack(side="right", padx=18, pady=14)
        else:
            def open_login():
                from gui.login import login_screen
                login_screen(root, on_success=lambda: (rebuild_header(), load_movies()))

            ctk.CTkButton(
                right_header,
                text="Đăng nhập",
                width=110,
                height=38,
                corner_radius=10,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                text_color="white",
                font=("Arial", 12, "bold"),
                command=open_login
            ).pack(side="right")

    entry_search.bind("<Return>", lambda e: do_search())

    rebuild_header()
    load_movies()
    root.mainloop()
