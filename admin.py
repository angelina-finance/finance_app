import tkinter as tk
from tkinter import ttk, messagebox
from database import get_all_users, delete_user

class AdminWindow:
    def __init__(self, parent, admin_id):
        self.parent = parent
        self.admin_id = admin_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Управление пользователями")
        self.dialog.geometry("600x400")
        
        columns = ("ID", "Логин", "Email", "Дата регистрации", "Админ?")
        self.tree = ttk.Treeview(self.dialog, columns=columns, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Логин", text="Логин")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Дата регистрации", text="Дата регистрации")
        self.tree.heading("Админ?", text="Админ?")
        self.tree.column("ID", width=40)
        self.tree.column("Логин", width=100)
        self.tree.column("Email", width=150)
        self.tree.column("Дата регистрации", width=150)
        self.tree.column("Админ?", width=60)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        btn_delete = tk.Button(self.dialog, text="Удалить выбранного пользователя",
                               command=self.delete_user)
        btn_delete.pack(side=tk.BOTTOM, pady=10)
        self.refresh_users()
    
    def refresh_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        users = get_all_users()
        for user in users:
            is_admin = "Да" if user[4] else "Нет"
            self.tree.insert("", tk.END, values=(user[0], user[1], user[2], user[3], is_admin))
    
    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите пользователя для удаления")
            return
        item = selected[0]
        user_id = self.tree.item(item, 'values')[0]
        username = self.tree.item(item, 'values')[1]
        if int(user_id) == self.admin_id:
            messagebox.showerror("Ошибка", "Вы не можете удалить самого себя (администратора)")
            return
        confirm = messagebox.askyesno("Подтверждение", 
                                      f"Вы уверены, что хотите удалить пользователя '{username}' и все его транзакции?")
        if confirm:
            success = delete_user(int(user_id))
            if success:
                messagebox.showinfo("Успех", "Пользователь удалён")
                self.refresh_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя")