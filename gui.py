"""
🔧 Название: Avito Parser 
📁 Файл: Gui.py
👤 Автор: Metiso4kas
📅 Июнь 2025
💼 Назначение: Парсинг Avito 
🛡 Лицензия: MIT

## 📜 Отказ от ответственности

- 🛠️ Данный проект создан исключительно для учебных и ознакомительных целей.
- 🏢 Он не является официальным продуктом Avito и не связан с администрацией сайта [Avito.ru](https://www.avito.ru).
- ⚠️ Использование данного парсера может противоречить **условиям обслуживания Avito.
- 👤 Автор проекта не несёт ответственности за любые последствия использования этого инструмента.
- ❌ Коммерческое использование, массовый сбор данных и автоматизированная перепродажа информации строго запрещены."
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import threading
from unidecode import unidecode
from parser import run_parser
from transliterate import translit

# 🌍 Словарь slug → Название города
CITY_NAMES = {
    "moskva": "Москва",
    "sankt-peterburg": "Санкт-Петербург",
    "novosibirsk": "Новосибирск",
    "ekaterinburg": "Екатеринбург",
    "kazan": "Казань",
    "rostov-na-donu": "Ростов-на-Дону",
    "nizhniy_novgorod": "Нижний Новгород",
    "chelyabinsk": "Челябинск",
    "samara": "Самара",
    "ufa": "Уфа",
    "krasnoyarsk": "Красноярск",
    "perm": "Пермь",
    "voronezh": "Воронеж",
    "volgograd": "Волгоград",
    "omsk": "Омск",
    "podolsk": "Подольск",
    "rossiya": "Россия"
}

def slug_to_city(slug):
    slug = slug.lower()
    if slug in CITY_NAMES:
        return CITY_NAMES[slug]
    return translit(slug.replace("-", " ").title(), 'ru')

# 🎨 Цвета и стили
BG_COLOR = "#f0f4f8"
BTN_COLOR = "#4a90e2"
BTN_TEXT = "#ffffff"
FONT_MAIN = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI", 10, "bold")

root = tk.Tk()
root.title("Avito Парсер — by Metiso4kas")
root.geometry("950x650")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

# === Фрейм ввода
frm_inputs = tk.Frame(root, bg=BG_COLOR)
frm_inputs.pack(pady=15)

tk.Label(frm_inputs, text="🔍 Запрос:", font=FONT_MAIN, bg=BG_COLOR).grid(row=0, column=0, sticky="e", padx=5)
entry = tk.Entry(frm_inputs, font=FONT_MAIN, width=35)
entry.grid(row=0, column=1, padx=5)
entry.insert(0, "гиря")

# === Кнопки
frm_buttons = tk.Frame(root, bg=BG_COLOR)
frm_buttons.pack(pady=10)

btn = tk.Button(frm_buttons, text="▶️ Запустить парсинг", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT, width=22, command=lambda: threading.Thread(target=start_parsing).start())
btn.grid(row=0, column=0, padx=10)

btn_copy = tk.Button(frm_buttons, text="📋 Копировать ссылку", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT, width=22, command=lambda: copy_selected_link())
btn_copy.grid(row=0, column=1, padx=10)

# === Таблица
style = ttk.Style()
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", font=("Segoe UI", 9), rowheight=26, background="#ffffff", fieldbackground="#ffffff")
style.map("Treeview", background=[("selected", "#d0e8ff")])

tree = ttk.Treeview(root, columns=("Название", "Цена", "Город", "Ссылка"), show="headings", height=17)
tree.pack(fill="both", expand=True, padx=20, pady=10)

for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, anchor="w", width=220 if col != "Ссылка" else 300)

# === Статус
status = tk.StringVar()
status.set("⌛ Готов к работе")
tk.Label(root, textvariable=status, font=("Segoe UI", 9), bg=BG_COLOR).pack(pady=5)


# === Функции ===

def load_and_display_csv():
    if not os.path.exists("data/results.csv"):
        messagebox.showerror("Ошибка", "Файл data/results.csv не найден")
        return

    df = pd.read_csv("data/results.csv")

    for row in tree.get_children():
        tree.delete(row)

    df["Цена (число)"] = df["Цена"].str.replace("₽", "").str.replace(" ", "").str.extract(r"(\d+)", expand=False).astype(float)
    df = df.sort_values(by="Цена (число)", ascending=True)

    df["Город"] = df["Город"].apply(slug_to_city)

    for _, row in df.iterrows():
        tree.insert("", "end", values=(row["Название"], row["Цена"], row["Город"], row["Ссылка"]))


def copy_selected_link():
    selected = tree.focus()
    if selected:
        link = tree.item(selected)["values"][-1]
        root.clipboard_clear()
        root.clipboard_append(link)
        root.update()
        messagebox.showinfo("Скопировано", f"Ссылка скопирована:\n{link}")


def start_parsing():
    query = entry.get().strip()
    if not query:
        messagebox.showwarning("Ошибка", "Введите поисковый запрос")
        return

    city_slug = "rossiya"
    btn["state"] = "disabled"
    status.set("🔄 Парсинг выполняется...")
    root.update()

    try:
        run_parser(query, city_slug)
        load_and_display_csv()
        messagebox.showinfo("✅ Успех", f"Парсинг завершён!")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
    finally:
        btn["state"] = "normal"
        status.set("✔️ Готово")


root.mainloop()
