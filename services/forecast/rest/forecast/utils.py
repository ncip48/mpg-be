import datetime

INDONESIAN_MONTHS = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}


def format_tanggal_indonesia(date_obj: datetime.date) -> str:
    return f"{date_obj.day} {INDONESIAN_MONTHS[date_obj.month]}"
