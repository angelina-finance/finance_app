import tkinter as tk
from tkinter import messagebox
from database import get_user_by_username, create_user
from utils import hash_password, verify_password, validate_email
from config import MIN_PASSWORD_LENGTH
from main_window import MainWindow

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Вход в систему учёта финансов")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        tk.Label(root, text="Логин:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.entry_login = tk.Entry(root, width=30)
        self.entry_login.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(root, text="Пароль:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.entry_password = tk.Entry(root, width=30, show="*")
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)
        
        btn_login = tk.Button(root, text="Войти", command=self.login, width=15)
        btn_login.grid(row=2, column=0, padx=10, pady=10, sticky='e')
        
        btn_register = tk.Button(root, text="Регистрация", command=self.open_register, width=15)
        btn_register.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        
        self.entry_login.bind("<Return>", lambda e: self.login())
        self.entry_password.bind("<Return>", lambda e: self.login())
        self.entry_login.focus()
    
    def login(self):
        username = self.entry_login.get().strip()
        password = self.entry_password.get()
        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
        user = get_user_by_username(username)
        if user and verify_password(password, user["salt"], user["password_hash"]):
            self.root.destroy()
            main_root = tk.Tk()
            app = MainWindow(main_root, user)
            main_root.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    
    def open_register(self):
        self.root.destroy()
        reg_root = tk.Tk()
        RegisterWindow(reg_root)
        reg_root.mainloop()

class RegisterWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Регистрация")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        tk.Label(root, text="Логин:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.entry_login = tk.Entry(root, width=30)
        self.entry_login.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Пароль (мин. 6 символов):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.entry_password = tk.Entry(root, width=30, show="*")
        self.entry_password.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Повторите пароль:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.entry_password2 = tk.Entry(root, width=30, show="*")
        self.entry_password2.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Email (необязательно):").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.entry_email = tk.Entry(root, width=30)
        self.entry_email.grid(row=3, column=1, padx=10, pady=5)
        
        btn_create = tk.Button(root, text="Создать аккаунт", command=self.register, width=20)
        btn_create.grid(row=4, column=0, columnspan=2, pady=20)
        
        btn_back = tk.Button(root, text="Назад к входу", command=self.back_to_login)
        btn_back.grid(row=5, column=0, columnspan=2)
    
    def register(self):
        username = self.entry_login.get().strip()
        password = self.entry_password.get()
        password2 = self.entry_password2.get()
        email = self.entry_email.get().strip()
        
        if not username:
            messagebox.showerror("Ошибка", "Логин не может быть пустым")
            return
        if len(password) < MIN_PASSWORD_LENGTH:
            messagebox.showerror("Ошибка", f"Пароль должен быть не менее {MIN_PASSWORD_LENGTH} символов")
            return
        if password != password2:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        if email and not validate_email(email):
            messagebox.showerror("Ошибка", "Введите корректный email (содержит @)")
            return
        if get_user_by_username(username):
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
            return
        
        salt, pwd_hash = hash_password(password)
        user_id = create_user(username, pwd_hash, salt, email, is_admin=False)
        if user_id:
            messagebox.showinfo("Успех", "Регистрация прошла успешно! Теперь вы можете войти.")
            self.back_to_login()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать пользователя")
    
    def back_to_login(self):
        self.root.destroy()
        login_root = tk.Tk()
        LoginWindow(login_root)
        login_root.mainloop()