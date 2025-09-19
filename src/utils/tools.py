from datetime import datetime


def get_wait_first() -> float:
    now = datetime.now()
    return (24 - now.hour) * 3600 + (60 - now.minute) * 60 + (60 - now.second)
