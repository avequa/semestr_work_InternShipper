from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """
    диалог, привязанный к заявке на проект
    один диалог на заявку 1 к 1
    """
    application = models.OneToOneField(
        'projects.ProjectApplication',
        on_delete=models.CASCADE,
        related_name='conversation',
        verbose_name='Заявка',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'

    def __str__(self):
        return f'Диалог по заявке #{self.application_id}'

    def participant_users(self):
        from teams.models import TeamMember

        app = self.application
        users = []

        partner_user = app.project.partner.user
        users.append(partner_user)

        if app.team_id:
            members = TeamMember.objects.filter(
                team=app.team
            ).select_related('student__user')
            users.extend(m.student.user for m in members)
            if app.team.captain and app.team.captain.user not in users:
                users.append(app.team.captain.user)
        elif app.student_id:
            users.append(app.student.user)

        return users

    def has_access(self, user):
        """может ли юзер писать в этом диалоге"""
        return user in self.participant_users()


class Message(models.Model):
    """сообщения, хранятся в постгрес"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages',
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.sender}: {self.text[:40]}'
