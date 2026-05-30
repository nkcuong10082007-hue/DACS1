import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps

from database.db import update_movie


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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTER_DIR = os.path.join(BASE_DIR, "assets", "posters")

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

def fit_image(path, size):
    img = Image.open(path).convert("RGB")
    img = ImageOps.contain(img, size)
    canvas = Image.new("RGB", size, "#F3F4F6")
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def save_poster_to_assets(source_path):
    os.makedirs(POSTER_DIR, exist_ok=True)

    if source_path and os.path.abspath(source_path).startswith(os.path.abspath(POSTER_DIR)):
        return source_path

    filename = os.path.basename(source_path)
    name, ext = os.path.splitext(filename)
    target_path = os.path.join(POSTER_DIR, filename)

    count = 1
    while os.path.exists(target_path):
        target_path = os.path.join(POSTER_DIR, f"{name}_{count}{ext}")
        count += 1

    shutil.copy2(source_path, target_path)
    return target_path


def edit_movie_screen(movie, callback):
    win = ctk.CTkToplevel()
    open_on_top(win)
    win.title("Sửa phim")
    win.geometry("780x860")
    win.configure(fg_color=BG)
    open_on_top(win)

    image_path = ctk.StringVar(value=movie[7] or "")

    header = ctk.CTkFrame(win, fg_color="transparent")
    header.pack(fill="x", padx=28, pady=(24, 10))

    ctk.CTkLabel(
        header,
        text="CHỈNH SỬA PHIM",
        text_color=PRIMARY,
        font=("Arial", 28, "bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        header,
        text="Cập nhật thông tin phim, lịch chiếu và giá vé",
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

    form = ctk.CTkFrame(main, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
    form.pack(fill="x", padx=4, pady=8)

    form_inner = ctk.CTkFrame(form, fg_color="transparent")
    form_inner.pack(fill="x", padx=22, pady=22)

    def create_field(label, default):
        ctk.CTkLabel(
            form_inner,
            text=label,
            text_color=MUTED,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(8, 5))

        entry = ctk.CTkEntry(
            form_inner,
            height=42,
            corner_radius=10,
            fg_color="#F9FAFB",
            border_color=BORDER,
            text_color=TEXT,
            font=("Arial", 13)
        )
        entry.insert(0, "" if default is None else str(default))
        entry.pack(fill="x", pady=(0, 6))
        return entry

    entry_name = create_field("Tên phim *", movie[1])
    entry_genre = create_field("Thể loại *", movie[2])
    entry_duration = create_field("Thời lượng, phút *", movie[3])
    entry_director = create_field("Đạo diễn", movie[4])
    entry_actors = create_field("Diễn viên", movie[5])
    entry_dates = create_field("Ngày chiếu *", movie[8])
    entry_times = create_field(
        "Suất chiếu *",
        movie[9] if len(movie) > 9 and movie[9] else "10:00, 12:00, 19:30"
    )
    entry_price = create_field(
        "Giá vé *",
        movie[10] if len(movie) > 10 and movie[10] else 90000
    )

    ctk.CTkLabel(
        form_inner,
        text="Mô tả phim",
        text_color=MUTED,
        font=("Arial", 12, "bold")
    ).pack(anchor="w", pady=(8, 5))

    text_desc = ctk.CTkTextbox(
        form_inner,
        height=140,
        corner_radius=10,
        fg_color="#F9FAFB",
        border_color=BORDER,
        text_color=TEXT,
        font=("Arial", 13),
        wrap="word"
    )
    text_desc.pack(fill="x", pady=(0, 8))
    text_desc.insert("1.0", movie[6] or "")

    poster_section = ctk.CTkFrame(form_inner, fg_color="#F9FAFB", corner_radius=16, border_width=1, border_color=BORDER)
    poster_section.pack(fill="x", pady=(12, 8))

    left_poster = ctk.CTkFrame(poster_section, fg_color="transparent")
    left_poster.pack(side="left", fill="x", expand=True, padx=18, pady=18)

    ctk.CTkLabel(
        left_poster,
        text="Ảnh bìa phim",
        text_color=TEXT,
        font=("Arial", 14, "bold")
    ).pack(anchor="w")

    img_status = ctk.CTkLabel(
        left_poster,
        text="Ảnh hiện tại" if image_path.get() else "Chưa có ảnh",
        text_color=GREEN if image_path.get() else MUTED,
        font=("Arial", 12)
    )
    img_status.pack(anchor="w", pady=(4, 12))

    preview_box = ctk.CTkFrame(
        poster_section,
        fg_color="#F3F4F6",
        corner_radius=14,
        border_width=1,
        border_color=BORDER,
        width=150,
        height=210
    )
    preview_box.pack(side="right", padx=18, pady=18)
    preview_box.pack_propagate(False)

    preview_label = ctk.CTkLabel(
        preview_box,
        text="Poster",
        text_color=MUTED,
        font=("Arial", 12, "bold")
    )
    preview_label.pack(expand=True)

    def load_preview(path):
        try:
            img = fit_image(path, (130, 185))
            poster = ctk.CTkImage(light_image=img, dark_image=img, size=(130, 185))
            preview_label.configure(image=poster, text="")
            preview_label.image = poster
            img_status.configure(text="Đã chọn ảnh", text_color=GREEN)
        except Exception:
            preview_label.configure(image=None, text="Không tải được ảnh")
            img_status.configure(text="Không tải được ảnh", text_color=MUTED)

    if image_path.get():
        load_preview(image_path.get())

    def choose_image():
        path = filedialog.askopenfilename(
            title="Chọn ảnh bìa",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
        )

        if path:
            image_path.set(path)
            load_preview(path)

    ctk.CTkButton(
        left_poster,
        text="Đổi ảnh bìa",
        width=150,
        height=40,
        corner_radius=12,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="white",
        font=("Arial", 12, "bold"),
        command=choose_image
    ).pack(anchor="w")

    def save():
        name = entry_name.get().strip()
        genre = entry_genre.get().strip()
        duration_text = entry_duration.get().strip()
        dates = entry_dates.get().strip()
        times = entry_times.get().strip()
        price_text = entry_price.get().strip()

        if not name or not genre or not duration_text or not dates or not times or not price_text:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ các trường bắt buộc (*)")
            return

        try:
            duration = int(duration_text)
            price = int(price_text)

            if duration <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Thời lượng và giá vé phải là số nguyên dương")
            return

        try:
            poster_path = save_poster_to_assets(image_path.get()) if image_path.get() else ""

            update_movie(
                movie[0],
                name,
                genre,
                duration,
                entry_director.get().strip(),
                entry_actors.get().strip(),
                text_desc.get("1.0", "end").strip(),
                poster_path,
                dates,
                times,
                price
            )

            messagebox.showinfo("Thành công", "Đã cập nhật phim")
            callback()
            win.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không lưu được: {e}")

    action = ctk.CTkFrame(form_inner, fg_color="transparent")
    action.pack(fill="x", pady=(18, 4))

    ctk.CTkButton(
        action,
        text="LƯU THAY ĐỔI",
        width=180,
        height=46,
        corner_radius=14,
        fg_color=GREEN,
        hover_color=GREEN_HOVER,
        text_color="white",
        font=("Arial", 13, "bold"),
        command=save
    ).pack(side="left")

    ctk.CTkButton(
        action,
        text="Đóng",
        width=110,
        height=46,
        corner_radius=14,
        fg_color="#E5E7EB",
        hover_color="#D1D5DB",
        text_color=TEXT,
        font=("Arial", 13, "bold"),
        command=win.destroy
    ).pack(side="left", padx=10)
