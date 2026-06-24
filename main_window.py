import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import get_transactions, delete_transaction, get_balance
from add_edit_transaction import AddEditTransactionDialog
from statistics import StatisticsWindow
from export import export_to_csv, export_to_pdf
from admin import AdminWindow

class MainWindow:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"Личные финансы – {user['username']}")
        self.root.geometry("900x600")
        
        self.search_var = tk.StringVar()
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()
        self.type_filter_var = tk.StringVar(value="all")
        self.current_transactions = []
        
        self.create_toolbar()
        self.create_filters()
        self.create_table()
        self.update_balance()
        self.refresh_table()
    
    def create_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        btn_add = tk.Button(toolbar, text="Добавить", command=self.add_transaction)
        btn_add.pack(side=tk.LEFT, padx=2)
        btn_edit = tk.Button(toolbar, text="Редактировать", command=self.edit_transaction)
        btn_edit.pack(side=tk.LEFT, padx=2)
        btn_delete = tk.Button(toolbar, text="Удалить", command=self.delete_transaction)
        btn_delete.pack(side=tk.LEFT, padx=2)
        btn_export = tk.Button(toolbar, text="Экспорт", command=self.export_data)
        btn_export.pack(side=tk.LEFT, padx=2)
        btn_stats = tk.Button(toolbar, text="Статистика", command=self.show_statistics)
        btn_stats.pack(side=tk.LEFT, padx=2)
        if self.user.get('is_admin', False):
            btn_admin = tk.Button(toolbar, text="Управление пользователями", command=self.manage_users)
            btn_admin.pack(side=tk.LEFT, padx=2)
        btn_exit = tk.Button(toolbar, text="Выйти", command=self.root.quit)
        btn_exit.pack(side=tk.RIGHT, padx=2)
    
    def create_filters(self):
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Label(filter_frame, text="Поиск:").pack(side=tk.LEFT, padx=2)
        entry_search = tk.Entry(filter_frame, textvariable=self.search_var, width=20)
        entry_search.pack(side=tk.LEFT, padx=2)
        entry_search.bind("<Return>", lambda e: self.refresh_table())
        btn_search = tk.Button(filter_frame, text="Найти", command=self.refresh_table)
        btn_search.pack(side=tk.LEFT, padx=2)
        btn_reset_search = tk.Button(filter_frame, text="Сбросить", command=self.reset_search)
        btn_reset_search.pack(side=tk.LEFT, padx=2)
        
        tk.Label(filter_frame, text="Дата с:").pack(side=tk.LEFT, padx=(10,2))
        entry_date_from = tk.Entry(filter_frame, textvariable=self.date_from_var, width=12)
        entry_date_from.pack(side=tk.LEFT, padx=2)
        tk.Label(filter_frame, text="по:").pack(side=tk.LEFT, padx=2)
        entry_date_to = tk.Entry(filter_frame, textvariable=self.date_to_var, width=12)
        entry_date_to.pack(side=tk.LEFT, padx=2)
        
        tk.Label(filter_frame, text="Тип:").pack(side=tk.LEFT, padx=(10,2))
        combo_type = ttk.Combobox(filter_frame, textvariable=self.type_filter_var,
                                  values=["all", "income", "expense"], state="readonly", width=10)
        combo_type.pack(side=tk.LEFT, padx=2)
        combo_type.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        btn_apply = tk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table)
        btn_apply.pack(side=tk.LEFT, padx=2)
        btn_reset_filters = tk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        btn_reset_filters.pack(side=tk.LEFT, padx=2)
    
    def create_table(self):
        columns = ("ID", "Дата", "Категория", "Тип", "Сумма", "Описание")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=20)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Тип", text="Тип")
        self.tree.heading("Сумма", text="Сумма (₽)")
        self.tree.heading("Описание", text="Описание")
        self.tree.column("ID", width=40, anchor='center')
        self.tree.column("Дата", width=100, anchor='center')
        self.tree.column("Категория", width=120, anchor='center')
        self.tree.column("Тип", width=80, anchor='center')
        self.tree.column("Сумма", width=100, anchor='e')
        self.tree.column("Описание", width=200, anchor='w')
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.tree.bind("<Double-1>", lambda e: self.edit_transaction())
    
    def update_balance(self):
        balance = get_balance(self.user['id'])
        if hasattr(self, 'balance_label'):
            self.balance_label.destroy()
        self.balance_label = tk.Label(self.root, text=f"Баланс: {balance:.2f} ₽",
                                      font=("Arial", 12, "bold"), fg="blue")
        self.balance_label.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
    
    def refresh_table(self):
        search = self.search_var.get().strip()
        date_from = self.date_from_var.get().strip()
        date_to = self.date_to_var.get().strip()
        trans_type = self.type_filter_var.get()
        if trans_type == "all":
            trans_type = None
        from utils import validate_date
        if date_from and not validate_date(date_from):
            messagebox.showerror("Ошибка", "Неверный формат даты 'С' (используйте ГГГГ-ММ-ДД)")
            return
        if date_to and not validate_date(date_to):
            messagebox.showerror("Ошибка", "Неверный формат даты 'По' (используйте ГГГГ-ММ-ДД)")
            return
        transactions = get_transactions(
            user_id=self.user['id'],
            search_text=search if search else None,
            date_from=date_from if date_from else None,
            date_to=date_to if date_to else None,
            trans_type=trans_type
        )
        self.current_transactions = transactions
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in transactions:
            trans_id, date, category, typ, amount, desc = row
            typ_display = "Доход" if typ == "income" else "Расход"
            tag = "income" if typ == "income" else "expense"
            self.tree.insert("", tk.END, values=(trans_id, date, category, typ_display, f"{amount:.2f}", desc or ""),
                             tags=(tag,))
        self.tree.tag_configure("income", background="#e6ffe6")
        self.tree.tag_configure("expense", background="#ffe6e6")
        self.update_balance()
    
    def reset_search(self):
        self.search_var.set("")
        self.refresh_table()
    
    def reset_filters(self):
        self.search_var.set("")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.type_filter_var.set("all")
        self.refresh_table()
    
    def add_transaction(self):
        dialog = AddEditTransactionDialog(self.root, self.user['id'], mode='add')
        if dialog.result:
            self.refresh_table()
    
    def edit_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите запись для редактирования")
            return
        item = selected[0]
        trans_id = self.tree.item(item, 'values')[0]
        dialog = AddEditTransactionDialog(self.root, self.user['id'], mode='edit', trans_id=trans_id)
        if dialog.result:
            self.refresh_table()
    
    def delete_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите запись для удаления")
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        trans_id = values[0]
        amount = values[4]
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить запись на сумму {amount} ₽?")
        if confirm:
            success = delete_transaction(int(trans_id), self.user['id'])
            if success:
                self.refresh_table()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить запись")
    
    def export_data(self):
        format_choice = messagebox.askyesno("Экспорт", "Выберите формат:\nДа – CSV, Нет – PDF")
        filetypes = [("CSV files", "*.csv")] if format_choice else [("PDF files", "*.pdf")]
        default_ext = ".csv" if format_choice else ".pdf"
        filename = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            title="Сохранить отчёт"
        )
        if not filename:
            return
        try:
            if format_choice:
                export_to_csv(filename, self.current_transactions)
            else:
                export_to_pdf(filename, self.current_transactions, self.user['username'])
            messagebox.showinfo("Успех", f"Файл сохранён: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def show_statistics(self):
        StatisticsWindow(self.root, self.user['id'])
    
    def manage_users(self):
        AdminWindow(self.root, self.user['id'])