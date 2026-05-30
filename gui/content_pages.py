import os
import customtkinter as ctk
from PIL import Image

from database.db import get_content_items

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_image_path(path):
    if not path:
        return ""

    if os.path.isabs(path):
        return path

    return os.path.join(BASE_DIR, path)


def load_ctk_image(path, size):
    real_path = resolve_image_path(path)

    if not real_path or not os.path.exists(real_path):
        return None

    try:
        img = Image.open(real_path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


def show_content_detail(parent, item):
    win = ctk.CTkToplevel(parent)
    win.transient(parent)
    win.grab_set()
    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.title(item["title"])
    win.state("zoomed")
    win.configure(fg_color="#f4f6fb")
    win.lift()
    win.focus_force()

    main = ctk.CTkScrollableFrame(win, fg_color="#f4f6fb")
    main.pack(fill="both", expand=True, padx=36, pady=28)

    banner = load_ctk_image(item["image_path"], (980, 360))
    if banner:
        ctk.CTkLabel(main, image=banner, text="").pack(pady=(0, 24))
    else:
        ctk.CTkFrame(main, width=980, height=260, fg_color="#e5e7eb").pack(pady=(0, 24))

    ctk.CTkLabel(
        main,
        text=item["title"],
        font=("Arial", 30, "bold"),
        text_color="#005bac",
        anchor="w"
    ).pack(fill="x", pady=(0, 6))

    if item["subtitle"]:
        ctk.CTkLabel(
            main,
            text=item["subtitle"],
            font=("Arial", 16),
            text_color="#374151",
            anchor="w",
            wraplength=980,
            justify="left"
        ).pack(fill="x", pady=(0, 20))

    desc_box = ctk.CTkTextbox(
        main,
        height=330,
        fg_color="white",
        text_color="#111111",
        font=("Arial", 16),
        corner_radius=14,
        border_width=1,
        border_color="#e5e7eb",
        wrap="word"
    )
    desc_box.pack(fill="x", pady=(0, 24))
    desc_box.insert("1.0", item["description"] or "Chưa có mô tả chi tiết.")
    desc_box.configure(state="disabled")

    ctk.CTkButton(
        main,
        text="Đóng",
        width=150,
        height=42,
        fg_color="#f58220",
        hover_color="#e66f00",
        command=win.destroy
    ).pack(anchor="center", pady=10)


def show_content_list(parent, category, title, subtitle=""):
    win = ctk.CTkToplevel(parent)
    win.transient(parent)
    win.grab_set()
    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.title(title)
    win.state("zoomed")
    win.configure(fg_color="#f4f6fb")
    win.lift()
    win.focus_force()

    header = ctk.CTkFrame(win, fg_color="white", height=120, corner_radius=0)
    header.pack(fill="x")
    header.pack_propagate(False)

    ctk.CTkLabel(
        header,
        text=title.upper(),
        font=("Arial", 28, "bold"),
        text_color="#f58220"
    ).pack(anchor="w", padx=38, pady=(24, 4))

    ctk.CTkLabel(
        header,
        text=subtitle or "Danh sách nội dung đang hiển thị từ database.",
        font=("Arial", 13),
        text_color="#64748b"
    ).pack(anchor="w", padx=38)

    body = ctk.CTkScrollableFrame(win, fg_color="#f4f6fb")
    body.pack(fill="both", expand=True, padx=38, pady=30)

    rows = get_content_items(category)
    items = []

    for row in rows:
        status = row[6] if len(row) > 6 else "active"

        if status == "hidden":
            continue

        items.append({
            "id": row[0],
            "category": row[1],
            "title": row[2] or "",
            "subtitle": row[3] or "",
            "description": row[4] or "",
            "image_path": row[5] or "",
            "status": status,
            "created_at": row[7] if len(row) > 7 else "",
        })

    if not items:
        empty = ctk.CTkFrame(body, fg_color="white", corner_radius=16, height=360)
        empty.pack(fill="x", pady=20)
        empty.pack_propagate(False)

        ctk.CTkLabel(
            empty,
            text="Chưa có nội dung nào",
            font=("Arial", 24, "bold"),
            text_color="#111827"
        ).pack(expand=True)

        return

    for item in items:
        card = ctk.CTkFrame(body, fg_color="white", corner_radius=14)
        card.pack(fill="x", pady=10)

        thumb = load_ctk_image(item["image_path"], (190, 105))

        if thumb:
            ctk.CTkLabel(card, image=thumb, text="").pack(side="left", padx=14, pady=14)
        else:
            ctk.CTkFrame(card, width=190, height=105, fg_color="#e5e7eb", corner_radius=10).pack(
                side="left", padx=14, pady=14
            )

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=(4, 14), pady=14)

        ctk.CTkLabel(
            info,
            text=item["title"],
            font=("Arial", 19, "bold"),
            text_color="#111827",
            anchor="w"
        ).pack(fill="x", pady=(4, 6))

        ctk.CTkLabel(
            info,
            text=item["subtitle"] or "Bấm xem chi tiết để đọc thêm.",
            font=("Arial", 14),
            text_color="#64748b",
            anchor="w",
            wraplength=760,
            justify="left"
        ).pack(fill="x")

        ctk.CTkButton(
            card,
            text="Chi tiết",
            width=110,
            height=38,
            fg_color="#f58220",
            hover_color="#e66f00",
            command=lambda selected=item: show_content_detail(win, selected)
        ).pack(side="right", padx=18)