from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import StudentForm
from .models import Student


def student_list(request):
    students = Student.objects.all().order_by('-created_at')

    # Search: text query (first name, last name)
    q = request.GET.get('q', '').strip()
    if q:
        students = students.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )

    # Optional filters
    level = request.GET.get('level', '').strip()
    if level:
        students = students.filter(current_academic_level=level)
    status = request.GET.get('status', '').strip()
    if status:
        students = students.filter(enrolled_status=status)

    context = {
        'students': students,
        'search_query': q,
        'search_level': level,
        'search_status': status,
        'level_choices': Student.current_academic_level_choices,
        'status_choices': Student.enrolled_status_choices,
    }
    return render(request, 'list.html', context)


@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student "{student.first_name} {student.last_name}" was created successfully.')
            return redirect('students:student_profile', pk=student.pk)
    else:
        form = StudentForm(request=request)
    context = {
        'form': form,
        'title': 'Add New Student',
    }
    return render(request, 'form.html', context)


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, request=request, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student "{student.first_name} {student.last_name}" was updated successfully.')
            return redirect('students:student_profile', pk=student.pk)
    else:
        form = StudentForm(request=request, instance=student)
    context = {
        'form': form,
        'title': 'Edit Student',
        'student': student,
    }
    return render(request, 'form.html', context)


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    name = f"{student.first_name} {student.last_name}"
    if request.method == 'POST':
        student.delete()
        messages.success(request, f'Student "{name}" was deleted successfully.')
        return redirect('students:student_list')
    return redirect('students:student_list')


def student_profile(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'profile.html', {'student': student})