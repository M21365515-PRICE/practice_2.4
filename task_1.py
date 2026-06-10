"""Задача 1: Погода через OpenWeather API."""

import io
import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import requests
from PIL import Image, ImageTk

API_URL = "https://api.openweathermap.org/data/2.5/weather"
ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"
TIMEOUT = 15


class WeatherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Погода — OpenWeather")
        self.geometry("420x380")
        self.minsize(380, 340)
        self._photo: ImageTk.PhotoImage | None = None

        ttk.Label(self, text="Погода в городе", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill=tk.X)

        ttk.Label(form, text="API-ключ:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.key_entry = ttk.Entry(form, width=36, show="*")
        self.key_entry.grid(row=0, column=1, padx=5, pady=4)
        env_key = os.environ.get("OPENWEATHER_API_KEY", "")
        if env_key:
            self.key_entry.insert(0, env_key)

        ttk.Label(form, text="Город:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.city_entry = ttk.Entry(form, width=36)
        self.city_entry.grid(row=1, column=1, padx=5, pady=4)
        self.city_entry.insert(0, "Москва")

        ttk.Button(self, text="Показать погоду", command=self.fetch_weather).pack(pady=8)

        self.icon_label = ttk.Label(self)
        self.icon_label.pack(pady=5)

        self.info_label = ttk.Label(self, text="Введите город и нажмите кнопку", font=("Segoe UI", 11))
        self.info_label.pack(pady=10)

        ttk.Label(
            self,
            text="Получите бесплатный ключ на openweathermap.org/api",
            font=("Segoe UI", 8),
            foreground="gray",
        ).pack(side=tk.BOTTOM, pady=8)

    def fetch_weather(self) -> None:
        city = self.city_entry.get().strip()
        api_key = self.key_entry.get().strip()
        if not city:
            messagebox.showwarning("Ввод", "Введите название города.")
            return
        if not api_key:
            messagebox.showwarning("API-ключ", "Введите API-ключ OpenWeather или задайте OPENWEATHER_API_KEY.")
            return
        threading.Thread(target=self._load, args=(city, api_key), daemon=True).start()

    def _load(self, city: str, api_key: str) -> None:
        try:
            response = requests.get(
                API_URL,
                params={"q": city, "appid": api_key, "units": "metric", "lang": "ru"},
                timeout=TIMEOUT,
            )
            if response.status_code == 401:
                self.after(0, lambda: messagebox.showerror("Ошибка", "Неверный API-ключ."))
                return
            if response.status_code == 404:
                self.after(0, lambda: messagebox.showerror("Ошибка", f"Город «{city}» не найден."))
                return
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            self.after(0, lambda: messagebox.showerror("Ошибка", str(exc)))
            return

        self.after(0, lambda: self._show_result(data))

    def _show_result(self, data: dict) -> None:
        name = data.get("name", "—")
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        temp = main.get("temp", "—")
        feels = main.get("feels_like", "—")
        humidity = main.get("humidity", "—")
        desc = weather.get("description", "—").capitalize()
        icon_code = weather.get("icon", "01d")

        self.info_label.config(
            text=f"{name}\n{desc}\nТемпература: {temp}°C\nОщущается: {feels}°C\nВлажность: {humidity}%"
        )

        try:
            icon_resp = requests.get(ICON_URL.format(icon=icon_code), timeout=TIMEOUT)
            icon_resp.raise_for_status()
            image = Image.open(io.BytesIO(icon_resp.content))
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            self._photo = ImageTk.PhotoImage(image)
            self.icon_label.config(image=self._photo)
        except (requests.RequestException, OSError):
            self.icon_label.config(image="", text="🌤")


def main() -> None:
    app = WeatherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
