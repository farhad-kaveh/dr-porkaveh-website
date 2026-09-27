"""Small dependency-free Gregorian -> Jalali date helpers for display."""

JALALI_MONTHS = (
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
)


def gregorian_to_jalali(gy, gm, gd):
    """Convert a Gregorian date to a Jalali (Solar Hijri) date."""
    g_days_in_month = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    j_days_in_month = (31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29)

    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    for i in range(gm2):
        g_day_no += g_days_in_month[i]
    if gm2 > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        g_day_no += 1
    g_day_no += gd2

    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    jm = 0
    while jm < 11 and j_day_no >= j_days_in_month[jm]:
        j_day_no -= j_days_in_month[jm]
        jm += 1
    jd = j_day_no + 1
    return jy, jm + 1, jd


def jalali_date_string(value):
    """Return a compact Persian display such as '28 شهریور 1405'."""
    if value is None:
        return ''
    jy, jm, jd = gregorian_to_jalali(value.year, value.month, value.day)
    return f'{jd} {JALALI_MONTHS[jm - 1]} {jy}'
