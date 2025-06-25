from openpyxl import Workbook
import io

def export_subscribers_xlsx(subscribers, year: int) -> io.BytesIO:
    headers = ["Nome", "Cognome", "Operatore", "N. abbonamento"]
    wb = Workbook()
    ws = wb.active
    ws.title = f'Abbonati {year}'
    ws.append(headers)
    for row in subscribers:
        ws.append(tuple(row))
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output