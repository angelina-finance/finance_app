import csv
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def export_to_csv(filename, transactions):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['ID', 'Дата', 'Категория', 'Тип', 'Сумма', 'Описание'])
        for row in transactions:
            typ = 'Доход' if row[3] == 'income' else 'Расход'
            writer.writerow([row[0], row[1], row[2], typ, f"{row[4]:.2f}", row[5] or ''])

def export_to_pdf(filename, transactions, username):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Отчёт по транзакциям пользователя {username}")
    c.setFont("Helvetica", 10)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.drawString(50, height - 70, f"Дата генерации: {date_str}")
    
    y = height - 100
    headers = ["ID", "Дата", "Категория", "Тип", "Сумма (₽)", "Описание"]
    x_positions = [50, 90, 170, 270, 340, 420]
    
    c.setFont("Helvetica-Bold", 10)
    for i, header in enumerate(headers):
        c.drawString(x_positions[i], y, header)
    y -= 20
    c.setFont("Helvetica", 9)
    
    for row in transactions:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)
        typ = 'Доход' if row[3] == 'income' else 'Расход'
        values = [str(row[0]), row[1], row[2], typ, f"{row[4]:.2f}", row[5] or '']
        for i, val in enumerate(values):
            c.drawString(x_positions[i], y, val)
        y -= 15
    c.save()