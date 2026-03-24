from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.worksheet import Worksheet

from dtos import Product
from string import ascii_uppercase

product_header = (
    "Ссылка на товар",
    "Артикул",
    "Название",
    "Цена",
    "Описание",
    "Изображения",
    "Характеристики",
    "Название селлера",
    "Ссылка на селлера",
    "Размеры товара",
    "Остатки по товару",
    "Рейтинг",
    "Количество отзывов",
)


def make_first_row_bold(ws: Worksheet):
    row = ws.row_dimensions[1]
    row.font = Font(bold=True)


def set_column_widths(ws: Worksheet, header: tuple):
    for letter, col_header in zip(ascii_uppercase, header):
        ws.column_dimensions[letter].width = len(col_header) + 5


def add_header(ws: Worksheet, header: tuple):
    ws.append(product_header)
    make_first_row_bold(ws)
    set_column_widths(ws, header)


def save_to_xlsx(products: list[Product], file_name):
    wb = Workbook()
    ws = wb.active

    add_header(ws, product_header)

    for row in products:
        ws.append(row.as_xlsx_row())

    wb.save(file_name)
