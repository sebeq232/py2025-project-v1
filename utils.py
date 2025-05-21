def get_season_from_date(year, month, day):
    """
    Zwraca porę roku na podstawie daty.
    Założenia:
    - Każdy miesiąc ma 30 dni
    - Sezony wg miesięcy:
        - zima: grudzień (12), styczeń (1), luty (2)
        - wiosna: marzec (3), kwiecień (4), maj (5)
        - lato: czerwiec (6), lipiec (7), sierpień (8)
        - jesień: wrzesień (9), październik (10), listopad (11)
    """

    if month in (12, 1, 2):
        return "zima"
    elif month in (3, 4, 5):
        return "wiosna"
    elif month in (6, 7, 8):
        return "lato"
    elif month in (9, 10, 11):
        return "jesień"
    else:
        # Dla pewności — jeśli miesiąc poza 1-12, zwracamy lato jako default
        return "lato"