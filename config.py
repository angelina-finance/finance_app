import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "finance.db")

CATEGORIES = [
    "Продукты", "Транспорт", "Зарплата", "Развлечения",
    "Здоровье", "Образование", "Коммунальные услуги",
    "Связь/Интернет", "Одежда", "Прочее"
]

MIN_PASSWORD_LENGTH = 6