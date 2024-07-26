import csv
import io
from tabulate import tabulate
from ..database.models import Diamond


def generate_text_table(diamonds: list[Diamond]) -> str:
    header = ["Shape", "Color", "Clarity", "Weight"]
    limited_diamonds = diamonds[:5]
    table = [[d.shape.value, d.color.value, d.clarity.value, d.weight] for d in limited_diamonds]
    if len(diamonds) > 5:
        table.append(['...'] * 4)
    return tabulate(table, headers=header, tablefmt="plain")


def get_csv_row(diamond: Diamond):
    return [
        str(diamond.stock),
        diamond.shape.value if diamond.shape else '',
        str(diamond.weight),
        diamond.color.value if diamond.color else '',
        diamond.clarity.value if diamond.clarity else '',
        diamond.lab if diamond.lab else '',
        str(diamond.certificate_number),
        f"{diamond.length} - {diamond.width} x {diamond.depth}",
        str(diamond.ratio),
        diamond.cut.value if diamond.cut else '',
        diamond.polish.value if diamond.polish else '',
        diamond.symmetry.value if diamond.symmetry else '',
        diamond.fluorescence.value if diamond.fluorescence else '',
        str(diamond.table),
        str(diamond.depth_percentage),
        diamond.gridle if diamond.gridle else '',
        diamond.culet.value if diamond.culet else '',
        diamond.certificate_comment if diamond.certificate_comment else '',
        str(diamond.rapnet),
        str(diamond.price_per_carat),
        diamond.picture if diamond.picture else ''
    ]


def generate_csv_content(diamonds: list[Diamond]) -> bytes:
    header = [
        'Stock', 'Shape', 'Weight', 'Color', 'Clarity', 'Lab', 'Certificate Number',
        'Measurements', 'Ratio', 'Cut', 'Polish', 'Symmetry', 'Fluorescence', 'Table',
        'Depth', 'Gridle', 'Culet', 'Certificate Comment', 'Rapnet', 'Price per Carat', 'Picture'
    ]

    with io.StringIO(newline='') as csv_buffer:
        writer = csv.writer(csv_buffer, delimiter=',')
        writer.writerow(header)
        for diamond in diamonds:
            writer.writerow(get_csv_row(diamond))
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
    return csv_bytes

