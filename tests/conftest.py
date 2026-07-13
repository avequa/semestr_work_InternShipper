from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient

from partners.models import PartnerProfile
from students.models import StudentProfile
from projects.models import Project, ProjectApplication
from teams.models import Team, TeamMember


"""юзеры"""
@pytest.fixture
def partner_user(db):
    return User.objects.create_user(username='partner1', password='pass12345')


@pytest.fixture
def student_user(db):
    return User.objects.create_user(username='student1', password='pass12345')


@pytest.fixture
def student_user2(db):
    return User.objects.create_user(username='student2', password='pass12345')


"""профили"""

@pytest.fixture
def partner_profile(db, partner_user):
    return PartnerProfile.objects.create(
        user=partner_user,
        company_name='Acme Corp',
    )


@pytest.fixture
def student_profile(db, student_user):
    return StudentProfile.objects.create(
        user=student_user,
        uni='МГУ',
        course=3,
        speciality='Прикладная математика',
    )


@pytest.fixture
def student_profile2(db, student_user2):
    return StudentProfile.objects.create(user=student_user2, uni='МФТИ', course=2)


"""проект и заявка"""

@pytest.fixture
def project(db, partner_profile):
    return Project.objects.create(
        partner=partner_profile,
        title='Веб-платформа аналитики',
        description='Описание проекта',
        deadline=timezone.now() + timedelta(days=30),
    )


@pytest.fixture
def application(db, project, student_profile):
    """Соло-заявка студента на проект"""
    return ProjectApplication.objects.create(project=project, student=student_profile)


"""команда"""

@pytest.fixture
def team(db, student_profile):
    t = Team.objects.create(name='Code Wizards', captain=student_profile)
    TeamMember.objects.create(team=t, student=student_profile)
    return t


"""апи клиент"""

@pytest.fixture
def api_client():
    return APIClient()
