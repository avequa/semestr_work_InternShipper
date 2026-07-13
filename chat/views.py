from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from projects.models import ProjectApplication
from .models import Conversation


@login_required
def open_chat(request, application_id):
    """
    открывает (или создаёт) диалог по заявкам, статус должен быть одобрено
    """
    application = get_object_or_404(
        ProjectApplication.objects.select_related(
            'student__user', 'team__captain__user', 'project__partner__user'
        ),
        pk=application_id,
    )

    if application.status != ProjectApplication.STATUS_APPROVED:
        return redirect('main_page')

    conversation, _ = Conversation.objects.get_or_create(application=application)

    if request.user not in conversation.participant_users():
        return redirect('main_page')

    partner_user = application.project.partner.user
    if request.user == partner_user:
        if application.team_id:
            chat_title = f'Команда: {application.team.name}'
        else:
            s = application.student.user
            chat_title = s.get_full_name() or s.username
    else:
        chat_title = application.project.partner.company_name

    return render(request, 'chat/chat.html', {
        'conversation': conversation,
        'application': application,
        'chat_title': chat_title,
        'is_team_chat': bool(application.team_id),
    })
