from django.core.management.base import BaseCommand
from attendance.models import Student, Attendance
from datetime import date

class Command(BaseCommand):
    help = 'Mark absent for students without attendance records for the day'
    
    def handle(self, *args, **kwargs):
        today = date.today()
        students = Student.objects.all()
        
        absent_count = 0
        for student in students:
            if not Attendance.objects.filter(student=student, date=today).exists():
                Attendance.objects.create(student=student, date=today, status='Absent')
                absent_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Default absences marked for {absent_count} students.'))
        