import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import get_stats_data
from utils import validate_date

class StatisticsWindow:
    def __init__(self, parent, user_id):
        self.parent = parent
        self.user_id = user_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Статистика")
        self.dialog.geometry("800x600")
        
        today = datetime.now()
        first_day = today.replace(day=1).strftime("%Y-%m-%d")
        last_day = today.strftime("%Y-%m-%d")
        
        top_frame = tk.Frame(self.dialog)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        tk.Label(top_frame, text="Дата с:").pack(side=tk.LEFT, padx=2)
        self.entry_from = tk.Entry(top_frame, width=12)
        self.entry_from.pack(side=tk.LEFT, padx=2)
        self.entry_from.insert(0, first_day)
        
        tk.Label(top_frame, text="по:").pack(side=tk.LEFT, padx=2)
        self.entry_to = tk.Entry(top_frame, width=12)
        self.entry_to.pack(side=tk.LEFT, padx=2)
        self.entry_to.insert(0, last_day)
        
        tk.Label(top_frame, text="Группировка:").pack(side=tk.LEFT, padx=(20,2))
        self.group_var = tk.StringVar(value="day")
        combo_group = ttk.Combobox(top_frame, textvariable=self.group_var,
                                   values=["day", "category"], state="readonly", width=12)
        combo_group.pack(side=tk.LEFT, padx=2)
        
        btn_build = tk.Button(top_frame, text="Построить график", command=self.build_graph)
        btn_build.pack(side=tk.LEFT, padx=10)
        
        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.dialog)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.build_graph()
    
    def build_graph(self):
        date_from = self.entry_from.get().strip()
        date_to = self.entry_to.get().strip()
        group_by = self.group_var.get()
        
        if not validate_date(date_from) or not validate_date(date_to):
            messagebox.showerror("Ошибка", "Неверный формат дат (ГГГГ-ММ-ДД)")
            return
        if date_from > date_to:
            messagebox.showerror("Ошибка", "Дата 'С' не может быть позже 'По'")
            return
        
        data = get_stats_data(self.user_id, date_from, date_to, group_by)
        if not data:
            messagebox.showinfo("Информация", "Нет данных за выбранный период")
            self.figure.clear()
            self.canvas.draw()
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if group_by == 'day':
            dates = [row[0] for row in data]
            incomes = [row[1] for row in data]
            expenses = [row[2] for row in data]
            x = range(len(dates))
            width = 0.35
            ax.bar([i - width/2 for i in x], incomes, width, label='Доходы', color='green')
            ax.bar([i + width/2 for i in x], expenses, width, label='Расходы', color='red')
            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45, ha='right')
            ax.set_xlabel("Дата")
            ax.set_ylabel("Сумма (₽)")
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        else:
            categories = [row[0] for row in data]
            incomes = [row[1] for row in data]
            expenses = [row[2] for row in data]
            x = range(len(categories))
            width = 0.35
            ax.bar([i - width/2 for i in x], incomes, width, label='Доходы', color='green')
            ax.bar([i + width/2 for i in x], expenses, width, label='Расходы', color='red')
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, ha='right')
            ax.set_xlabel("Категория")
            ax.set_ylabel("Сумма (₽)")
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        self.figure.tight_layout()
        self.canvas.draw()