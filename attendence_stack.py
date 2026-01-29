attendance_stack = []


def mark_attendance(roll, status, date=None):
    """Push an attendance entry onto the in-memory stack.

    Entry format: {"roll": <roll>, "status": <status>, "date": "YYYY-MM-DD"}
    """
    # Lazy import to avoid module-level datetime dependency for tests
    from datetime import date as _date

    if date is None:
        date_str = _date.today().isoformat()
    elif isinstance(date, str):
        date_str = date
    else:
        # assume date-like (datetime.date)
        try:
            date_str = date.isoformat()
        except Exception:
            date_str = _date.today().isoformat()

    entry = {"roll": roll, "status": status, "date": date_str}
    attendance_stack.append(entry)
    return entry


def undo_attendance():
    if attendance_stack:
        return attendance_stack.pop()
    return None