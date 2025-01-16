# forms.py
from django import forms
from .models import Student, Attendance, Teacher

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'rollno', 'photo']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'status']

class TeacherLoginForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'})
    )
    password = forms.CharField(
        max_length=100,
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )
    subject = forms.CharField(
        max_length=100,
        label="Subject",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your subject'})
    )
