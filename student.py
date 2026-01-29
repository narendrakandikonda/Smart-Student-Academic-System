class Student:
    def __init__(self, roll, name, marks=None, attendance=None):
        self.roll = roll
        self.name = name
        self.marks = marks or {}
        self.attendance = attendance or []

    def total_marks(self):
        return sum(self.marks.values())

    def percentage(self):
        if not self.marks:
            return 0
        # Calculate percentage out of 5 subjects × 100 marks each = 500 total
        max_total_marks = 5 * 100  # 500
        return (self.total_marks() / max_total_marks) * 100

    def grade(self):
        p = self.percentage()
        if p >= 90:
            return 'A'
        elif p >= 75:
            return 'B'
        elif p >= 60:
            return 'C'
        else:
            return 'D'

    def attendance_percentage(self):
        """Calculate attendance percentage from the attendance list.

        Entries may be legacy strings like 'P'/'A' or dicts with {'status','date'}.
        Presence is detected by status values: 'P', 'present', '1', 'true', 'yes' (case-insensitive).
        """
        if not self.attendance:
            return 0
        present = 0
        total = 0
        for a in self.attendance:
            if isinstance(a, dict):
                status = a.get('status')
            else:
                status = a
            if status is None:
                continue
            total += 1
            sval = str(status).strip().lower()
            if sval in ('p', 'present', '1', 'true', 'yes'):
                present += 1
        if total == 0:
            return 0
        return (present / total) * 100

    def attendance_by(self, day=None, month=None, year=None):
        """Return attendance records filtered by day/month/year.

        day/month/year are integers. If none provided, returns all records (including legacy non-dated records).
        """
        res = []
        from datetime import datetime

        for a in self.attendance:
            if isinstance(a, dict):
                date_str = a.get('date')
                status = a.get('status')
            else:
                date_str = None
                status = a

            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str)
                except Exception:
                    # fallback: try simple YYYY-MM-DD
                    try:
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                    except Exception:
                        continue

                if day and dt.day != int(day):
                    continue
                if month and dt.month != int(month):
                    continue
                if year and dt.year != int(year):
                    continue

                res.append({"date": dt.date().isoformat(), "status": status})
            else:
                # legacy entry without date
                if not (day or month or year):
                    res.append({"date": None, "status": status})

        return res

    def semester_attendance_percentage(self, months=6):
        """Calculate attendance percentage for a semester (default 6 months).
        
        Counts all weekdays (Mon-Fri) in the semester period and calculates:
        (days present) / (total working days in semester) * 100
        """
        if not self.attendance:
            return 0
        
        from datetime import datetime, timedelta
        
        # Get the date range for the semester (last N months)
        today = datetime.now().date()
        semester_start = today - timedelta(days=30*months)
        
        # Create a map of attendance records for quick lookup
        attendance_map = {}
        for a in self.attendance:
            if isinstance(a, dict):
                date_str = a.get('date')
                status = a.get('status')
            else:
                continue
            
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str).date()
                except Exception:
                    try:
                        dt = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except Exception:
                        continue
                
                # Only map records within semester period
                if semester_start <= dt <= today:
                    attendance_map[dt.isoformat()] = status
        
        # Count all working days in semester and mark present days
        present = 0
        total_working_days = 0
        current_date = semester_start
        
        while current_date <= today:
            # Count only weekdays (Mon-Fri)
            if current_date.weekday() < 5:  # 0=Monday, 4=Friday
                total_working_days += 1
                
                # Check if this day has attendance record marked as present
                date_iso = current_date.isoformat()
                if date_iso in attendance_map:
                    status = attendance_map[date_iso]
                    sval = str(status).strip().lower()
                    if sval in ('p', 'present', '1', 'true', 'yes'):
                        present += 1
            
            current_date += timedelta(days=1)
        
        if total_working_days == 0:
            return 0
        return (present / total_working_days) * 100