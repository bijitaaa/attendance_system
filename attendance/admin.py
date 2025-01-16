from django.contrib import admin
from .models import Teacher, Student, Subject, Attendance


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_subjects')  # Use a method to display subjects
    list_filter = ('subjects',)  # Use the ManyToManyField for filtering

    def get_subjects(self, obj):
        return ", ".join([subject.name for subject in obj.subjects.all()])
    get_subjects.short_description = 'Subjects'


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'rollno', 'get_subjects')  
    list_filter = ('subjects',)  # Use the ManyToManyField for filtering

    def get_subjects(self, obj):
        return ", ".join([subject.name for subject in obj.subjects.all()])
    get_subjects.short_description = 'Subjects'


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status')
    list_filter = ('subject', 'status', 'date')


# Register models with the admin site
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Attendance, AttendanceAdmin)
