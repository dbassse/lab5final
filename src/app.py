import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk
from typing import Any, Dict, List, Optional, cast

import pandas as pd

# Определяем путь к директории исполняемого файла
if getattr(sys, "frozen", False):
    base_path: str = (
        sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(sys.executable)
    )
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Путь к ParquetViewer.exe
viewer_path = os.path.join(
    base_path,
    "tools",
    r"C:\Users\Admino\PycharmProjects\PeopleManager\tools\ParquetViewer.exe",
)

# Пути к данным
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
data_folder = os.path.join(desktop_path, "data")
DATA_FILE = os.path.join(data_folder, "people.parquet")
EXPECTED_COLUMNS: List[str] = ["Фамилия", "Имя", "Телефон", "Дата рождения"]


# Аннотации для tkinter widgets
class TkEntry(tk.Entry):
    pass


class TkTreeview(ttk.Treeview):
    pass


def load_data(file_path: str = DATA_FILE) -> pd.DataFrame:
    """Загружает данные из указанного файла."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        try:
            return pd.read_parquet(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")
    return pd.DataFrame(columns=EXPECTED_COLUMNS)


def save_data(df: pd.DataFrame, file_path: str = DATA_FILE) -> None:
    """Сохраняет DataFrame в указанный файл."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        df.to_parquet(file_path, index=False)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить данные:\n{e}")


def validate_with_parquetviewer() -> None:
    """Запускает внешний просмотрщик ParquetViewer для проверки файла данных."""
    if not os.path.exists(DATA_FILE):
        messagebox.showwarning("Валидация", "Файл с данными не найден!")
        return
    if not os.path.exists(viewer_path):
        messagebox.showerror("Ошибка", "Файл ParquetViewer.exe не найден в tools ")
        return
    # Для Windows используем os.startfile, для других платформ - subprocess
    try:
        if sys.platform.startswith("win"):
            os.startfile(viewer_path)
        else:
            subprocess.run([viewer_path, DATA_FILE], check=True)
        messagebox.showinfo("Валидация", "ParquetViewer запущен. Проверьте файл!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить ParquetViewer:\n{e}")


class PeopleManagerApp(tk.Tk):
    df: pd.DataFrame

    def __init__(self) -> None:
        super().__init__()
        self.title("Менеджер людей")
        self.geometry("600x500")
        self.df = load_data()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self) -> None:
        input_frame: tk.LabelFrame = tk.LabelFrame(
            self, text="Добавить запись", padx=10, pady=10
        )
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Фамилия:").grid(row=0, column=0, sticky="e")
        self.entry_lastname: tk.Entry = tk.Entry(input_frame)
        self.entry_lastname.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(input_frame, text="Имя:").grid(row=1, column=0, sticky="e")
        self.entry_firstname: tk.Entry = tk.Entry(input_frame)
        self.entry_firstname.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(input_frame, text="Телефон:").grid(row=2, column=0, sticky="e")
        self.entry_phone: tk.Entry = tk.Entry(input_frame)
        self.entry_phone.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(input_frame, text="Дата рождения (ГГГГ-ММ-ДД):").grid(
            row=3, column=0, sticky="e"
        )
        self.entry_birth: tk.Entry = tk.Entry(input_frame)
        self.entry_birth.grid(row=3, column=1, padx=5, pady=2)

        btn_add: tk.Button = tk.Button(
            input_frame, text="Добавить", command=self.add_record
        )
        btn_add.grid(row=4, column=0, columnspan=2, pady=5)

        ops_frame: tk.LabelFrame = tk.LabelFrame(
            self, text="Операции", padx=10, pady=10
        )
        ops_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(ops_frame, text="Поиск по месяцу", command=self.search_by_month).pack(
            side="left", padx=5
        )
        tk.Button(
            ops_frame, text="Удалить по фамилии", command=self.delete_by_lastname
        ).pack(side="left", padx=5)
        tk.Button(
            ops_frame,
            text="Валидация через ParquetViewer",
            command=validate_with_parquetviewer,
        ).pack(side="left", padx=5)
        tk.Button(ops_frame, text="Показать все", command=self.refresh_table).pack(
            side="left", padx=5
        )

        table_frame: tk.Frame = tk.Frame(self)
        table_frame.pack(fill="both", padx=10, pady=5, expand=True)
        self.tree = ttk.Treeview(table_frame, columns=EXPECTED_COLUMNS, show="headings")
        for col in EXPECTED_COLUMNS:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

    def add_record(self) -> None:
        lastname: str = self.entry_lastname.get().strip()
        firstname: str = self.entry_firstname.get().strip()
        phone: str = self.entry_phone.get().strip()
        birth_input: str = self.entry_birth.get().strip()

        if not (lastname and firstname and phone and birth_input):
            messagebox.showwarning("Внимание", "Заполните все поля!")
            return

        try:
            dt: datetime = datetime.strptime(birth_input, "%Y-%m-%d")
            birth_list: List[int] = [dt.year, dt.month, dt.day]
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
            return

        new_row: Dict[str, Any] = {
            "Фамилия": lastname,
            "Имя": firstname,
            "Телефон": phone,
            "Дата рождения": birth_list,
        }
        self.df = self.df._append(new_row, ignore_index=True)
        self.df.sort_values(by="Фамилия", inplace=True)
        save_data(self.df)
        self.refresh_table()
        self.clear_entries()
        messagebox.showinfo("Успех", "Запись добавлена.")

    def clear_entries(self) -> None:
        self.entry_lastname.delete(0, tk.END)
        self.entry_firstname.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_birth.delete(0, tk.END)

    def refresh_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in self.df.iterrows():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["Фамилия"],
                    row["Имя"],
                    row["Телефон"],
                    row["Дата рождения"],
                ),
            )

    def search_by_month(self) -> None:
        month: Optional[int] = simpledialog.askinteger(
            "Поиск", "Введите номер месяца (1-12):", minvalue=1, maxvalue=12
        )
        if month is None:
            return
        result: pd.DataFrame = self.df[
            self.df["Дата рождения"].apply(lambda b: b[1] == month)
        ]
        if result.empty:
            messagebox.showinfo("Результат", f"Нет записей для месяца {month}")
        else:
            result_window: tk.Toplevel = tk.Toplevel(self)
            result_window.title(f"Результаты для месяца {month}")
            tree: ttk.Treeview = ttk.Treeview(
                result_window, columns=EXPECTED_COLUMNS, show="headings"
            )
            for col in EXPECTED_COLUMNS:
                tree.heading(col, text=col)
            tree.pack(fill="both", expand=True)
            for _, row in result.iterrows():
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        row["Фамилия"],
                        row["Имя"],
                        row["Телефон"],
                        row["Дата рождения"],
                    ),
                )

    def delete_by_lastname(self) -> None:
        lastname: Optional[str] = simpledialog.askstring(
            "Удаление", "Введите фамилию для удаления:"
        )
        if not lastname:
            return
        new_df: pd.DataFrame = self.df[self.df["Фамилия"] != lastname]
        if new_df.shape[0] == self.df.shape[0]:
            messagebox.showinfo(
                "Удаление", f"Записей с фамилией '{lastname}' не найдено."
            )
        else:
            self.df = new_df
            save_data(self.df)
            self.refresh_table()
            messagebox.showinfo("Удаление", f"Записи с фамилией '{lastname}' удалены.")


if __name__ == "__main__":
    app = PeopleManagerApp()
    app.mainloop()
