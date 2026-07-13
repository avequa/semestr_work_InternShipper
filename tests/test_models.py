import pytest

from projects.models import ProjectApplication
from teams.models import Team, TeamMember
from chat.models import Conversation, Message


@pytest.mark.django_db
class TestProjectApplication:
    def test_default_status_is_pending(self, application):
        """новая заявка по умолчанию должна иметь статус 'pending' - на рассмотрении"""
        assert application.status == ProjectApplication.STATUS_PENDING

    def test_get_status_display(self, application):
        """get_status_display() возвращает человекочитаемую подпись статуса"""
        assert application.get_status_display() == 'На рассмотрении'

    def test_cascade_delete_with_project(self, application, project):
        """при удалении проекта связанные заявки удаляются - правило каскад"""
        assert ProjectApplication.objects.count() == 1
        project.delete()
        assert ProjectApplication.objects.count() == 0


@pytest.mark.django_db
class TestProjectStr:
    def test_str_contains_title(self, project):
        """__str__ проекта содержит его название"""
        assert 'Веб-платформа аналитики' in str(project)


@pytest.mark.django_db
class TestTeam:
    def test_str(self, team):
        """__str__ команды содержит её название"""
        assert 'Code Wizards' in str(team)

    def test_member_unique_together(self, team, student_profile):
        """нельзя добавить одного студента в одну команду дважды"""
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            TeamMember.objects.create(team=team, student=student_profile)


@pytest.mark.django_db
class TestConversationAccess:
    """бизнес-логика доступа к чату"""

    def test_solo_access(self, application, student_user, partner_user, student_user2):
        """в соло-диалоге доступ есть только у студента-заявителя и партнёра"""
        conv = Conversation.objects.create(application=application)
        assert conv.has_access(student_user) is True
        assert conv.has_access(partner_user) is True
        assert conv.has_access(student_user2) is False

    def test_team_access_includes_all_members(
        self, project, partner_user, student_profile, student_profile2
    ):
        """
        в командном диалоге доступ есть у всех участников команды и у партнёра
        """
        team = Team.objects.create(name='Dream Team', captain=student_profile)
        TeamMember.objects.create(team=team, student=student_profile)
        TeamMember.objects.create(team=team, student=student_profile2)

        app = ProjectApplication.objects.create(project=project, team=team)
        conv = Conversation.objects.create(application=app)

        assert conv.has_access(student_profile.user) is True
        assert conv.has_access(student_profile2.user) is True
        assert conv.has_access(partner_user) is True


@pytest.mark.django_db
class TestMessage:
    def test_message_belongs_to_conversation(self, application, student_user):
        """месседж сохраняется и привязывается к диалогу в бд"""
        conv = Conversation.objects.create(application=application)
        msg = Message.objects.create(
            conversation=conv, sender=student_user, text='Привет!'
        )
        assert conv.messages.count() == 1
        assert conv.messages.first().text == 'Привет!'
        assert msg.sender == student_user
