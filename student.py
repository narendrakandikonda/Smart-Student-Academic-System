class Student:
    def __init__(self, roll_no, name, marks_dict):
        self.roll_no = roll_no              # alphanumeric
        self.name = name
        self.marks = marks_dict             # dictionary
        self.total = sum(marks_dict.values())
        self.percentage = self.total / len(marks_dict)
        self.grade = self.calculate_grade()

    def calculate_grade(self):
        if self.percentage >= 90:
            return "A+"
        elif self.percentage >= 80:
            return "A"
        elif self.percentage >= 70:
            return "B"
        else:
            return "C"
