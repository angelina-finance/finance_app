import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import CATEGORIES
from database import get_transaction_by_id, add_transaction, update_transaction
from utils import validate_date, validate_amount

class AddEditTransactionDialog:
    def __init__(self, parent, user_id, mode='add', trans_id=None):
        self.parent = parent
        self.user_id = user_id
        self.mode = mode
        self.trans_id = trans_id
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавление транзакции" if mode == 'add' else "Редактирование транзакции")
        self.dialog.geometry("400x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        tk.Label(self.dialog, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.entry_date = tk.Entry(self.dialog, width=20)
        self.entry_date.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        btn_today = tk.Button(self.dialog, text="Сегодня", command=self.set_today)
        btn_today.grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Категория:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.combo_category = ttk.Combobox(self.dialog, values=CATEGORIES, state="readonly", width=18)
        self.combo_category.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        tk.Label(self.dialog, text="Тип:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.type_var = tk.StringVar(value="expense")
        frame_type = tk.Frame(self.dialog)
        frame_type.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        rb_income = tk.Radiobutton(frame_type, text="Доход", variable=self.type_var, value="income")
        rb_income.pack(side=tk.LEFT, padx=5)
        rb_expense = tk.Radiobutton(frame_type, text="Расход", variable=self.type_var, value="expense")
        rb_expense.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.dialog, text="Сумма:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.entry_amount = tk.Entry(self.dialog, width=20)
        self.entry_amount.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        
        tk.Label(self.dialog, text="Описание (необязательно):").grid(row=4, column=0, padx=10, pady=5, sticky='ne')
        self.entry_description = tk.Text(self.dialog, width=30, height=5)
        self.entry_description.grid(row=4, column=1, padx=10, pady=5, sticky='w')
        
        btn_save = tk.Button(self.dialog, text="Сохранить", command=self.save)
        btn_save.grid(row=5, column=0, padx=10, pady=20, sticky='e')
        btn_cancel = tk.Button(self.dialog, text="Отмена", command=self.dialog.destroy)
        btn_cancel.grid(row=5, column=1, padx=10, pady=20, sticky='w')
        
        if mode == 'edit' and trans_id:
            self.load_data()
        else:
            self.set_today()
            if CATEGORIES:
                self.combo_category.current(0)
    
    def set_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, today)
    
    def load_data(self):
        trans = get_transaction_by_id(self.trans_id, self.user_id)
        if not trans:
            messagebox.showerror("Ошибка", "Транзакция не найдена или у вас нет прав")
            self.dialog.destroy()
            return
        self.entry_date.insert(0, trans[1])
        self.combo_category.set(trans[2])
        self.type_var.set(trans[3])
        self.entry_amount.insert(0, str(trans[4]))
        if trans[5]:
            self.entry_description.insert("1.0", trans[5])
    
    def save(self):
        date_str = self.entry_date.get().strip()
        category = self.combo_category.get().strip()
        trans_type = self.type_var.get()
        amount_str = self.entry_amount.get().strip()
        description = self.entry_description.get("1.0", tk.END).strip()
        
        if not date_str:
            messagebox.showerror("Ошибка", "Введите дату")
            return
        if not validate_date(date_str):
            messagebox.showerror("Ошибка", "Неверный формат даты (ГГГГ-ММ-ДД) или дата не существует")
            return
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию")
            return
        if not validate_amount(amount_str):
            messagebox.showerror("Ошибка", "Введите положительное число в поле 'Сумма'")
            return
        amount = float(amount_str)
        if len(description) > 200:
            messagebox.showerror("Ошибка", "Описание не должно превышать 200 символов")
            return
        
        if self.mode == 'add':
            new_id = add_transaction(self.user_id, date_str, category, trans_type, amount, description)
            if new_id:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить транзакцию")
        else:
            success = update_transaction(self.trans_id, self.user_id, date_str, category, trans_type, amount, description)
            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить транзакцию (возможно, она была удалена)")