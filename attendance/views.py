from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
from django.contrib import messages
from .models import Student, Attendance, Teacher, Subject
from .forms import TeacherLoginForm, StudentRegistrationForm
from datetime import timedelta, date
from .utils import get_face_encoding_from_frame, match_face
import cv2
import numpy as np
from collections import defaultdict


def capture_face(request):
    if request.method == 'GET':
        return render(request, 'capture.html')
    
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            image_data = data.get('image')  # Get the image data from the JSON payload

            if not image_data:
                return JsonResponse({'message': 'No image data provided.'})

            # Decode the Base64 image data
            image_bytes = base64.b64decode(image_data.split(',')[1])  # Ignore the "data:image/jpeg;base64," part
            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # Decode the image into an OpenCV format
            
            # Process the image to get encoding
            encoding = get_face_encoding_from_frame(frame)
            if encoding is None:
                return JsonResponse({'message': "No face detected. Please retry."})

            # Check in database for a match
            database_students = Student.objects.all()
            matched_student = None
            min_distance = float("inf")
            
            for student in database_students:
                db_encoding = np.frombuffer(student.facial_encoding)  # Get stored encoding from database
                if db_encoding.size == 0:  # Skip invalid or empty encodings
                    continue
                
                # Compare the encodings
                distance = np.linalg.norm(encoding - db_encoding)
                if distance < 0.6 and distance < min_distance:
                    min_distance = distance
                    matched_student = student

            if matched_student:
                # Mark attendance
                today = date.today()
                attendance, created = Attendance.objects.get_or_create(student=matched_student, date=today)
                if created:
                    attendance.status = 'Present'
                    attendance.save()
                return JsonResponse({'message': f"Attendance Done for {matched_student.name}!"})

            return JsonResponse({'message': "Unknown Face! Can't find in database."})
        except Exception as e:
            print("Error processing image:", e)
            return JsonResponse({'message': f"An error occurred during processing: {str(e)}"})
        
    return JsonResponse({'message': "Invalid request method."})





def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            subject_name = form.cleaned_data.get('subject')  # Use .get() for safety

            try:
                # Check if the subject exists
                subject = Subject.objects.get(name=subject_name)

                # Query the teacher and check for the subject in their subjects relationship
                teacher = Teacher.objects.get(name=name, password=password)
                if not teacher.subjects.filter(id=subject.id).exists():
                    form.add_error('subject', 'Invalid subject for this teacher')
                    return render(request, 'teacher_login.html', {'form': form})

                # Store teacher details in session
                request.session['teacher_id'] = teacher.id
                request.session['name'] = teacher.name
                request.session['subject'] = subject.name  # Store the selected subject

                return redirect('teacher_dashboard')
            except Subject.DoesNotExist:
                form.add_error('subject', 'Subject does not exist')
            except Teacher.DoesNotExist:
                form.add_error(None, 'Invalid credentials')
    else:
        form = TeacherLoginForm()

    return render(request, 'teacher_login.html', {'form': form})


def teacher_dashboard(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return redirect('teacher_login')

    teacher = Teacher.objects.get(id=teacher_id)

    # Get the subjects taught by the teacher
    subjects_taught = teacher.subjects.all()

    # Get students enrolled in any of the teacher's subjects
    students = Student.objects.filter(subjects__in=subjects_taught).distinct()

    return render(request, 'teacher_dashboard.html', {'teacher': teacher, 'students': students})


def register_student(request):
    teacher_id = request.session.get('teacher_id')  # Get the logged-in teacher's ID
    if not teacher_id:
        return redirect('teacher_login')  # Redirect to login if teacher is not logged in

    teacher = Teacher.objects.get(id=teacher_id)  # Fetch the logged-in teacher

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.subject = teacher  # Assign the logged-in teacher to the student's subject
            
            # Process the student's photo and extract facial encoding
            photo = form.cleaned_data.get('photo')
            if photo:
                # Convert the image to a format usable by OpenCV
                image = cv2.imdecode(np.frombuffer(photo.read(), np.uint8), cv2.IMREAD_COLOR)

                # Get the face encoding from the image
                encoding = get_face_encoding_from_frame(image)
                if encoding is not None:
                    student.facial_encoding = encoding.tobytes()  # Store the encoding as binary in the database
                else:
                    messages.error(request, "No face detected in the photo. Please try again.")
                    return redirect('register_student')

            try:
                student.save()  # Save the student to the database
                messages.success(request, f"Student {student.name} has been registered successfully!")
                return redirect('teacher_dashboard')  # Redirect to the teacher dashboard
            except Exception as e:
                messages.error(request, f"Error while registering student: {str(e)}")
                return redirect('register_student')  # Redirect back to the registration page
        else:
            # If form is not valid, show the errors
            messages.error(request, "Form is not valid. Please check the input fields.")
            return redirect('register_student')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register_student.html', {'form': form})

def view_attendance(request):
    teacher_id = request.session.get('teacher_id')  # Fetch the logged-in teacher's ID
    if not teacher_id:
        return redirect('teacher_login')

    teacher = Teacher.objects.get(id=teacher_id)  # Get the Teacher instance

    # Get the subjects taught by the teacher
    subjects_taught = teacher.subjects.all()

    # Get students enrolled in any of the teacher's subjects
    students = Student.objects.filter(subjects__in=subjects_taught).distinct()

    # Fetch attendance records for these students
    attendance_records = Attendance.objects.filter(student__in=students).order_by('-date')

    return render(request, 'view_attendance.html', {'attendance_records': attendance_records, 'teacher': teacher})

def view_attendance_by_subject(request):
    teacher_id = request.session.get('teacher_id')  # Fetch the logged-in teacher's ID
    if not teacher_id:
        return redirect('teacher_login')

    teacher = Teacher.objects.get(id=teacher_id)  # Get the Teacher instance

    # Get the subjects taught by the teacher
    subjects_taught = teacher.subjects.all()

    # Initialize a dictionary to hold attendance by subject and date
    attendance_by_subject = defaultdict(lambda: defaultdict(list))

    # Iterate over subjects and group attendance records
    for subject in subjects_taught:
        students = Student.objects.filter(subjects=subject)
        attendance_records = Attendance.objects.filter(student__in=students).order_by('-date')

        for record in attendance_records:
            attendance_by_subject[subject.name][record.date].append(record)

    return render(request, 'attendance_by_subject.html', {
        'teacher': teacher,
        'attendance_by_subject': attendance_by_subject,
    })

        