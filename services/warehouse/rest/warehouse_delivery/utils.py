from datetime import date

MONTH_CODES = {
    1: "A",
    2: "B",
    3: "C",
    4: "D",
    5: "E",
    6: "F",
    7: "G",
    8: "H",
    9: "I",
    10: "J",
    11: "K",
    12: "L",
}

def generate_production_code(production_date):
    return (
        f"{production_date:%y}"
        f"{MONTH_CODES[production_date.month]}"
        f"{production_date:%d}"
    )