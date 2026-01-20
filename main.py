from student import Student
from database import add_student
from attendance_stack import mark_attendance, undo_attendance

while True:
    print("\n1. Add Student")
    print("2. Mark Attendance")
    print("3. Undo Attendance")
    print("4. Exit")

    try:
        choice = int(input("Enter choice: "))
    except ValueError:
        print("Please enter a valid number")
        continue

    if choice == 1:
        roll = input("Roll No (alphanumeric): ")
        name = input("Name: ")

        marks = {}
        n = int(input("Enter number of subjects: "))

        for i in range(n):
            subject = input(f"Enter subject {i+1} name: ")
            mark = int(input(f"Enter marks for {subject}: "))
            marks[subject] = mark

        student = Student(roll, name, marks)
        add_student(student)

        print("Student added successfully")

    elif choice == 2:
        roll = input("Roll No: ")
        status = input("Present / Absent: ")
        mark_attendance(roll, status)
        print("Attendance marked")

    elif choice == 3:
        undone = undo_attendance()
        print("Undone attendance:", undone)

    elif choice == 4:
        print("Exiting...")
        break

    else:
        print("Invalid choice")
