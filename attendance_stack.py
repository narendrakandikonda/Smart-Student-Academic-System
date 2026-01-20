attendance_stack = []

def mark_attendance(roll_no, status):
    attendance_stack.append((roll_no, status))
    return status

def undo_attendance():
    if attendance_stack:
        return attendance_stack.pop()
    return None
