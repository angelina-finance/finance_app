import tkinter as tk
from database import init_db
from auth import LoginWindow

def main():
    init_db()
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()