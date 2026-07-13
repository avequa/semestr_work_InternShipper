from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Project, ProjectApplication
from .forms import ProjectForm
from teams.models import TeamMember, Team

@login_required
@require_http_methods(['GET', 'POST'])
def project_create(request):
    if not hasattr(request.user, 'partner_profile'):
        return redirect('main_page')
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.partner = request.user.partner_profile
            project.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
@require_http_methods(['GET', 'POST'])
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.partner.user != request.user:
        return redirect('project_list')
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
def project_list(request):
    if hasattr(request.user, 'partner_profile'):
        projects = Project.objects.filter(partner=request.user.partner_profile)
    else:
        projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
@require_http_methods(['GET', 'POST'])
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.partner.user != request.user:
        return redirect('project_list')
    if request.method == "POST":
        project.delete()
        return redirect('project_list')
    return render(request, 'projects/project_delete.html', {'project': project})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    can_apply_solo = False
    captain_teams = []  # команды, где пользователь — капитан и ещё не подал заявку

    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile

        # Соло: можно подать, если ещё нет соло-заявки от этого студента.
        if not ProjectApplication.objects.filter(project=project, student=student).exists():
            can_apply_solo = True

        # Команды, где пользователь — капитан (может быть несколько).
        teams_as_captain = Team.objects.filter(captain=student)
        for team in teams_as_captain:
            already = ProjectApplication.objects.filter(project=project, team=team).exists()
            if not already:
                captain_teams.append(team)

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'can_apply_solo': can_apply_solo,
        'captain_teams': captain_teams,
    })


@login_required
def apply_to_project(request, pk):
    """
    Подача заявки. Тип определяется параметром:
      - apply_type == 'team' + team_id  -> заявка от команды (только капитан);
      - иначе                            -> соло-заявка студента.
    """
    project = get_object_or_404(Project, pk=pk)

    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "Только студенты могут подавать заявки")
        return redirect('project_list')

    student = request.user.student_profile
    apply_type = request.POST.get('apply_type') or request.GET.get('apply_type', 'solo')

    if apply_type == 'team':
        team_id = request.POST.get('team_id') or request.GET.get('team_id')
        team = get_object_or_404(Team, pk=team_id)

        # Подавать командную заявку может только капитан этой команды.
        if team.captain != student:
            messages.error(request, "Только капитан команды может подать заявку от её лица")
            return redirect('project_detail', pk=pk)

        if ProjectApplication.objects.filter(project=project, team=team).exists():
            messages.error(request, "Эта команда уже подала заявку на проект")
            return redirect('project_detail', pk=pk)

        ProjectApplication.objects.create(project=project, team=team)
        messages.success(request, f"Заявка от команды «{team.name}» подана!")
        return redirect('project_list')

    # Соло-заявка.
    if ProjectApplication.objects.filter(project=project, student=student).exists():
        messages.error(request, "Вы уже подали заявку на этот проект")
        return redirect('project_list')

    ProjectApplication.objects.create(project=project, student=student)
    messages.success(request, f"Заявка на проект «{project.title}» подана!")
    return redirect('project_list')


@login_required
def project_applications(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not hasattr(request.user, 'partner_profile') or project.partner != request.user.partner_profile:
        messages.error(request, "У вас нет доступа к заявкам этого проекта")
        return redirect('project_list')

    applications = project.applications.select_related(
        'student__user', 'team__captain__user'
    ).all()

    # Для командных заявок заранее собираем участников (чтобы показать список).
    for app in applications:
        if app.team_id:
            app.member_list = TeamMember.objects.filter(
                team=app.team
            ).select_related('student__user')
        else:
            app.member_list = None

    return render(request, 'projects/project_applications.html', {
        'project': project,
        'applications': applications,
    })


@login_required
def update_application_status(request, project_pk, application_pk):
    project = get_object_or_404(Project, pk=project_pk)

    if not hasattr(request.user, 'partner_profile') or project.partner != request.user.partner_profile:
        messages.error(request, "У вас нет прав для этого действия")
        return redirect('project_list')

    application = get_object_or_404(ProjectApplication, pk=application_pk, project=project)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'approved', 'rejected']:
            application.status = new_status
            application.save()
            messages.success(request, f"Статус заявки обновлён на «{application.get_status_display()}»")

    return redirect('project_applications', pk=project_pk)

# work with session
@login_required
def add_to_favorites(request, pk):

    project = get_object_or_404(Project, pk=pk)
    favorites = request.session.get('favorites', [])

    if pk not in favorites:
        favorites.append(pk)
        request.session['favorites'] = favorites
        messages.success(request, f"{project.title} добавлен в избранное")
    else:
        messages.info(request, f"{project.title} уже в избранном")

    return redirect(request.META.get('HTTP_REFERER', 'project_list'))

@login_required
def remove_from_favorites(request, pk):

    favorites = request.session.get('favorites', [])
    if pk in favorites:
        favorites.remove(pk)
        request.session['favorites'] = favorites
        messages.success(request, "Проект удалён из избранного")

    return redirect(request.META.get('HTTP_REFERER', 'favorites_list'))

@login_required
def favorites_list(request):
    favorites_ids = request.session.get('favorites', [])
    projects = Project.objects.filter(id__in=favorites_ids, is_active=True)

    return render(request, 'projects/favorites.html', {
        'projects': projects,
        'favorites_count': len(favorites_ids)
    })

@login_required
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    favorites = request.session.get('favorites', [])

    if pk in favorites:
        favorites.remove(pk)
        messages.success(request, f"{project.title} удалён из избранного")
    else:
        favorites.append(pk)
        messages.success(request, f"{project.title} добавлен в избранное")

    request.session['favorites'] = favorites
    return redirect(request.META.get('HTTP_REFERER', 'project_list'))