from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Team, TeamMember
from students.models import StudentProfile


@login_required
def my_team(request):
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "Вы не студент")
        return redirect('home')

    member = TeamMember.objects.filter(student=request.user.student_profile).first()
    if member:
        team = member.team
        members = TeamMember.objects.filter(team=team).select_related('student__user')
        return render(request, 'teams/my_team.html', {
            'team': team,
            'members': members,
            'is_captain': team.captain == request.user.student_profile,
        })

    return render(request, 'teams/no_team.html')


@login_required
def create_team(request):
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "У вас нет профиля студента")
        return redirect('home')

    if TeamMember.objects.filter(student=request.user.student_profile).exists():
        messages.error(request, "Вы уже состоите в команде")
        return redirect('teams:my_team')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:
            team = Team.objects.create(
                name=name,
                description=description,
                captain=request.user.student_profile
            )
            TeamMember.objects.create(team=team, student=request.user.student_profile)
            messages.success(request, f"Команда '{name}' создана!")
            return redirect('teams:my_team')

    return render(request, 'teams/create_team.html')


@login_required
def search_students(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if team.captain != request.user.student_profile:
        messages.error(request, "Только капитан может добавлять участников")
        return redirect('teams:my_team')

    query = request.GET.get('q', '')
    students = []

    if query:
        students = StudentProfile.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).exclude(
            user__in=TeamMember.objects.filter(team=team).values('student__user')
        ).select_related('user')

    return render(request, 'teams/search_students.html', {
        'team': team,
        'students': students,
        'query': query
    })


@login_required
def invite_member(request, team_id, student_id):
    team = get_object_or_404(Team, id=team_id)
    student = get_object_or_404(StudentProfile, id=student_id)

    if team.captain != request.user.student_profile:
        messages.error(request, "Только капитан может добавлять участников")
        return redirect('teams:my_team')

    if TeamMember.objects.filter(student=student).exists():
        messages.error(request, f"{student.user.username} уже состоит в другой команде")
        return redirect('teams:search_students', team_id=team.id)

    TeamMember.objects.create(team=team, student=student)
    messages.success(request, f"{student.user.get_full_name() or student.user.username} добавлен в команду!")

    return redirect('teams:my_team')


@login_required
def add_member(request, team_id):
    return redirect('teams:search_students', team_id=team_id)


@login_required
def remove_member(request, team_id, member_id):
    team = get_object_or_404(Team, id=team_id)
    member = get_object_or_404(TeamMember, id=member_id, team=team)

    if team.captain != request.user.student_profile:
        messages.error(request, "Только капитан может удалять участников")
        return redirect('teams:my_team')

    if member.student == team.captain:
        messages.error(request, "Нельзя удалить капитана команды")
        return redirect('teams:my_team')

    if request.method == 'POST':
        student_name = member.student.user.get_full_name() or member.student.user.username
        member.delete()
        messages.success(request, f"{student_name} удалён из команды")

    return redirect('teams:my_team')


@login_required
def leave_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not hasattr(request.user, 'student_profile'):
        return redirect('home')

    member = TeamMember.objects.filter(team=team, student=request.user.student_profile).first()
    if not member:
        return redirect('teams:my_team')

    if member.student == team.captain:
        messages.error(request, "Капитан не может покинуть команду. Сначала передайте капитанство или удалите команду.")
        return redirect('teams:my_team')

    if request.method == 'POST':
        member.delete()
        messages.success(request, "Вы покинули команду")
        return redirect('teams:my_team')

    return render(request, 'teams/leave_team.html', {'team': team})


@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if not hasattr(request.user, 'student_profile'):
        return redirect('home')

    if team.captain != request.user.student_profile:
        messages.error(request, "Только капитан может удалить команду")
        return redirect('teams:my_team')

    members_count = TeamMember.objects.filter(team=team).count()
    if members_count > 1:
        messages.error(request,
                       f"В команде ещё {members_count - 1} участников. Сначала удалите их или они должны выйти сами.")
        return redirect('teams:my_team')

    if request.method == 'POST':
        team_name = team.name
        team.delete()
        messages.success(request, f"Команда '{team_name}' удалена")
        return redirect('teams:my_team')

    return render(request, 'teams/delete_team.html', {'team': team})