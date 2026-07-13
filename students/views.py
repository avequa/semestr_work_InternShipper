from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentProfileForm
from projects.models import ProjectApplication
from students.models import StudentProfile

@login_required
def my_projects(request):
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "Вы не студент")
        return redirect('home')

    from django.db.models import Q

    solo_applications = ProjectApplication.objects.filter(
        student=request.user.student_profile
    )

    from teams.models import TeamMember
    team_member = TeamMember.objects.filter(student=request.user.student_profile).first()

    if team_member:
        team_applications = ProjectApplication.objects.filter(team=team_member.team)
    else:
        team_applications = ProjectApplication.objects.none()

    applications = (solo_applications | team_applications).select_related(
        'project', 'project__partner', 'team'
    ).distinct().order_by('-applied_at')

    return render(request, 'students/my_projects.html', {
        'applications': applications
    })


@login_required
def profile_view(request):
    profile = request.user.student_profile

    return render(request, 'students/profile.html', {
        'profile': profile
    })


@login_required
def profile_edit(request):
    profile = request.user.student_profile

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлён")
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, 'students/profile_edit.html', {
        'form': form
    })


@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('login')
    return render(request, 'students/profile_delete.html')

@login_required
def student_public_profile(request, pk):
    """
    Просмотр профиля студента по id. Доступен партнёрам (например, чтобы
    посмотреть, кто подал заявку на их проект) и самому студенту.
    """
    profile = get_object_or_404(StudentProfile.objects.select_related('user'), pk=pk)

    # Партнёрам и самому студенту — можно. Другим студентам закрываем.
    is_partner = hasattr(request.user, 'partner_profile')
    is_owner = hasattr(request.user, 'student_profile') and request.user.student_profile == profile
    if not (is_partner or is_owner):
        return redirect('main_page')

    return render(request, 'students/public_profile.html', {'profile': profile})