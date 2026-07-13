from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PartnerProfileForm
from projects.models import Project


@login_required
def partner_profile_view(request):
    if not hasattr(request.user, 'partner_profile'):
        messages.error(request, "Вы не партнер")
        return redirect('home')

    profile = request.user.partner_profile
    return render(request, 'partners/profile.html', {'profile': profile})


@login_required
def partner_profile_edit(request):
    if not hasattr(request.user, 'partner_profile'):
        messages.error(request, "Вы не партнер")
        return redirect('home')

    profile = request.user.partner_profile

    if request.method == 'POST':
        form = PartnerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлён")
            return redirect('partner_profile')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
    else:
        form = PartnerProfileForm(instance=profile)

    return render(request, 'partners/profile_edit.html', {'form': form, 'profile': profile})


@login_required
def partner_profile_delete(request):
    if not hasattr(request.user, 'partner_profile'):
        messages.error(request, "Вы не партнер")
        return redirect('home')

    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Ваш аккаунт был успешно удалён")
        return redirect('login')

    return render(request, 'partners/profile_delete.html')


@login_required
def partner_projects(request):
    if not hasattr(request.user, 'partner_profile'):
        messages.error(request, "У вас нет профиля партнера")
        return redirect('home')

    projects = Project.objects.filter(partner=request.user.partner_profile).order_by('-created_at')
    return render(request, 'partners/projects_list.html', {'projects': projects})
