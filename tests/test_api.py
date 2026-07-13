import pytest

STUDENTS_API = '/students/api/'
PROJECTS_API = '/projects/api/'
PARTNERS_API = '/partners/api/'


@pytest.mark.django_db
class TestStudentProfileAPI:
    def test_requires_authentication(self, api_client):
        """без авторизации профиль студента недоступен"""
        response = api_client.get(STUDENTS_API + 'profile/')
        assert response.status_code in (401, 403)

    def test_returns_own_profile(self, api_client, student_user, student_profile):
        """авторизованный студент получает свой профиль"""
        api_client.force_authenticate(user=student_user)
        response = api_client.get(STUDENTS_API + 'profile/')
        assert response.status_code == 200
        data = response.json()
        assert data['uni'] == 'МГУ'
        assert data['course'] == 3


@pytest.mark.django_db
class TestMyProjectsAPI:
    """эндпоинт со вложенной структурой JSON"""

    def test_returns_applications_with_nested_fields(
        self, api_client, student_user, student_profile, application
    ):
        api_client.force_authenticate(user=student_user)
        response = api_client.get(STUDENTS_API + 'my-projects/')

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1

        item = data[0]
        assert item['project_title'] == 'Веб-платформа аналитики'
        assert item['partner_name'] == 'Acme Corp'
        assert 'team_name' in item
        assert item['team_name'] is None


@pytest.mark.django_db
class TestProjectListAPI:
    def test_lists_only_active_projects(
        self, api_client, student_user, student_profile, project
    ):
        """список проектов отдаёт активные проекты авторизованному пользователю"""
        api_client.force_authenticate(user=student_user)
        response = api_client.get(PROJECTS_API + 'list/')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == 'Веб-платформа аналитики'
        assert data[0]['is_active'] is True


@pytest.mark.django_db
class TestPartnerProfileAPI:
    def test_returns_partner_profile(self, api_client, partner_user, partner_profile):
        """партнёр получает свой проиль со статусом 200"""
        api_client.force_authenticate(user=partner_user)
        response = api_client.get(PARTNERS_API + 'profile/')
        assert response.status_code == 200
        data = response.json()
        assert data['company_name'] == 'Acme Corp'
        assert data['is_verified'] is False
