"""Задача 2: Случайные фото котов и собак."""

import io
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import requests
from PIL import Image, ImageTk

CAT_API = "https://api.thecatapi.com/v1/images/search"
DOG_API = "https://dog.ceo/api/breeds/image/random"
TIMEOUT = 15
IMAGE_SIZE = (480, 360)


class PetPhotoApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Коты и собаки")
        self.geometry("520x500")
        self.minsize(480, 450)
        self._photo: ImageTk.PhotoImage | None = None

        ttk.Label(self, text="Случайные фотографии", font=("Segoe UI", 12, "bold")).pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Получить кота", command=self.get_cat).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Получить собаку", command=self.get_dog).pack(side=tk.LEFT, padx=10)

        self.status = ttk.Label(self, text="Нажмите кнопку, чтобы загрузить фото")
        self.status.pack(pady=5)

        self.image_label = ttk.Label(self)
        self.image_label.pack(expand=True, pady=10)

    def set_image(self, image_data: bytes) -> None:
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail(IMAGE_SIZE, Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=self._photo)

    def load_cat(self) -> None:
        try:
            response = requests.get(CAT_API, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if not data:
                raise ValueError("Пустой ответ API")
            url = data[0]["url"]
            img_resp = requests.get(url, timeout=TIMEOUT)
            img_resp.raise_for_status()
            self.after(0, lambda: self.set_image(img_resp.content))
            self.after(0, lambda: self.status.config(text="Случайный кот загружен"))
        except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
            self.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось загрузить кота: {exc}"))
            self.after(0, lambda: self.status.config(text="Ошибка загрузки"))

    def load_dog(self) -> None:
        try:
            response = requests.get(DOG_API, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "success":
                raise ValueError(data.get("message", "Ошибка API"))
            url = data["message"]
            img_resp = requests.get(url, timeout=TIMEOUT)
            img_resp.raise_for_status()
            self.after(0, lambda: self.set_image(img_resp.content))
            self.after(0, lambda: self.status.config(text="Случайная собака загружена"))
        except (requests.RequestException, ValueError, KeyError) as exc:
            self.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось загрузить собаку: {exc}"))
            self.after(0, lambda: self.status.config(text="Ошибка загрузки"))

    def get_cat(self) -> None:
        self.status.config(text="Загрузка кота...")
        threading.Thread(target=self.load_cat, daemon=True).start()

    def get_dog(self) -> None:
        self.status.config(text="Загрузка собаки...")
        threading.Thread(target=self.load_dog, daemon=True).start()


def main() -> None:
    app = PetPhotoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
