from flask import Flask, request, jsonify
from flask_cors import CORS 
from database import students
from student import Student
from attendence_stack import mark_attendance, undo_attendance
from datetime import date as _date
import calendar as _calendar

app = Flask(__name__)
CORS(app)

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json

    if not data or 'roll' not in data or 'name' not in data:
        return jsonify({"error": "Roll and Name are required"}), 400

    students.insert_one({
        "roll": data['roll'],
        "name": data['name'],
        "marks": {},
        "attendance": []
    })

    return jsonify({"msg": "Student added successfully"})


@app.route('/add_marks', methods=['POST'])
def add_marks():
    data = request.json
    students.update_one(
        {"roll": data['roll']},
        {"$set": {"marks": data['marks']}}
    )
    return jsonify({"msg": "Marks updated successfully"})

@app.route('/update_marks', methods=['POST'])
def update_marks():
    data = request.json
    
    if not data or 'roll' not in data or 'subject' not in data or 'marks' not in data:
        return jsonify({"error": "Roll, Subject, and Marks are required"}), 400
    
    # Find the student
    student = students.find_one({"roll": data['roll']})
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Update the specific subject marks
    marks = student.get('marks', {})
    marks[data['subject']] = data['marks']
    
    students.update_one(
        {"roll": data['roll']},
        {"$set": {"marks": marks}}
    )
    
    return jsonify({"msg": f"Marks for {data['subject']} updated to {data['marks']}"})

@app.route('/mark_attendance', methods=['POST'])
def attendance():
    data = request.json
    # Accept optional `date` (ISO string) or `day`, `month`, `year` fields
    date_str = None
    if not data or 'roll' not in data or 'status' not in data:
        return jsonify({"error": "roll and status required"}), 400

    if 'date' in data and data['date']:
        try:
            # validate iso date
            date_str = _date.fromisoformat(data['date']).isoformat()
        except Exception:
            date_str = data['date']
    elif all(k in data for k in ('day', 'month', 'year')) and data['day'] and data['month'] and data['year']:
        try:
            date_str = _date(int(data['year']), int(data['month']), int(data['day'])).isoformat()
        except Exception:
            date_str = _date.today().isoformat()
    else:
        date_str = _date.today().isoformat()

    # push to in-memory stack and persist as a dict with date
    mark_attendance(data['roll'], data['status'], date_str)
    students.update_one(
        {"roll": data['roll']},
        {"$push": {"attendance": {"status": data['status'], "date": date_str}}}
    )
    return jsonify({"msg": "Attendance marked"})

@app.route('/undo_attendance', methods=['POST'])
def undo():
    return jsonify({"undone": undo_attendance()})

@app.route('/students', methods=['GET'])
def view_students():
    result = []
    for s in students.find({}, {"_id": 0}):
        stu = Student(s['roll'], s['name'], s['marks'], s['attendance'])
        result.append({
            "roll": stu.roll,
            "name": stu.name,
            "marks": stu.marks,
            "total": stu.total_marks(),
            "max_marks": 500,
            "percentage": stu.percentage(),
            "attendance_percentage": stu.attendance_percentage(),
            "grade": stu.grade(),
            "attendance": stu.attendance
        })
    return jsonify(result)
@app.route('/student/<roll>', methods=['GET'])
def get_student_by_roll(roll):
    # Optional query params: month, year — defaults to current month/year
    month = request.args.get('month')
    year = request.args.get('year')

    s = students.find_one({"roll": roll}, {"_id": 0})

    if not s:
        return jsonify({"error": "Student not found"}), 404

    stu = Student(s['roll'], s['name'], s.get('marks', {}), s.get('attendance', []))

    # default to current month/year when not provided
    if not month:
        month = str(_date.today().month)
    if not year:
        year = str(_date.today().year)

    # fetch attendance records for the requested month/year
    records = stu.attendance_by(month=month, year=year)

    # map date->status for quick lookup (ISO dates)
    record_map = {r['date']: r['status'] for r in records if r.get('date')}

    y = int(year)
    m = int(month)
    _, ndays = _calendar.monthrange(y, m)

    # build calendar array for frontend: one entry per day in month
    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    calendar_list = []
    present_days = 0
    total_working_days = 0
    for d in range(1, ndays + 1):
        date_obj = _date(y, m, d)
        date_iso = date_obj.isoformat()
        status = record_map.get(date_iso)
        weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
        
        # Count all weekdays (Monday-Friday) as working days
        if weekday < 5:  # Monday(0) to Friday(4)
            total_working_days += 1
            sval = str(status).strip().lower() if status is not None else ''
            if sval in ('p', 'present', '1', 'true', 'yes'):
                present_days += 1

        calendar_list.append({
            'day': d,
            'date': date_iso,
            'weekday': weekday_names[weekday],
            'status': status
        })

    period_percentage = (present_days / total_working_days * 100) if total_working_days > 0 else 0

    return jsonify({
        "roll": stu.roll,
        "name": stu.name,
        "marks": stu.marks,
        "total": stu.total_marks(),
        "max_marks": 500,
        "percentage": stu.percentage(),
        "attendance_percentage": stu.attendance_percentage(),
        "grade": stu.grade(),
        "attendance": stu.attendance,
        "attendance_period": {"month": int(month), "year": int(year)},
        "attendance_period_summary": {
            "present_days": present_days,
            "total_days": total_working_days,
            "percentage": period_percentage,
            "records": records
        },
        "calendar": calendar_list,
        "calendar_meta": {"month_start_weekday": _calendar.monthrange(y, m)[0]} 
    })


@app.route('/attendance/<roll>', methods=['GET'])
def attendance_by(roll):
    # Optional query params: day, month, year
    day = request.args.get('day')
    month = request.args.get('month')
    year = request.args.get('year')

    s = students.find_one({"roll": roll}, {"_id": 0})
    if not s:
        return jsonify({"error": "Student not found"}), 404

    stu = Student(s['roll'], s['name'], s.get('marks', {}), s.get('attendance', []))
    records = stu.attendance_by(day=day, month=month, year=year)
    return jsonify({"roll": roll, "attendance_records": records, "attendance_percentage": stu.attendance_percentage()})

@app.route('/semester_attendance/<roll>', methods=['GET'])
def semester_attendance(roll):
    # Optional query param: months (default 6 for a semester)
    months = request.args.get('months', default=6, type=int)

    s = students.find_one({"roll": roll}, {"_id": 0})
    if not s:
        return jsonify({"error": "Student not found"}), 404

    stu = Student(s['roll'], s['name'], s.get('marks', {}), s.get('attendance', []))
    semester_pct = stu.semester_attendance_percentage(months=months)
    
    # Count present days and total working days in semester
    from datetime import datetime, timedelta
    today = datetime.now().date()
    semester_start = today - timedelta(days=30*months)
    
    # Create attendance map for quick lookup
    attendance_map = {}
    for a in stu.attendance:
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
            
            if semester_start <= dt <= today:
                attendance_map[dt.isoformat()] = status
    
    # Count all working days in semester
    present_count = 0
    working_days_count = 0
    current_date = semester_start
    
    while current_date <= today:
        if current_date.weekday() < 5:  # Monday(0) to Friday(4)
            working_days_count += 1
            
            date_iso = current_date.isoformat()
            if date_iso in attendance_map:
                status = attendance_map[date_iso]
                sval = str(status).strip().lower()
                if sval in ('p', 'present', '1', 'true', 'yes'):
                    present_count += 1
        
        current_date += timedelta(days=1)
    
    return jsonify({
        "roll": roll,
        "name": stu.name,
        "semester_months": months,
        "semester_attendance_percentage": semester_pct,
        "present_days": present_count,
        "total_working_days": working_days_count
    })


if __name__ == '__main__':
    app.run(debug=True)