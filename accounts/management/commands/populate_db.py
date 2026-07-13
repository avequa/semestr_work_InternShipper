import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from students.models import StudentProfile
from partners.models import PartnerProfile
from teams.models import Team, TeamMember
from projects.models import Project, ProjectApplication


UNIVERSITIES = [
    'КФУ', 'КНИТУ-КАИ', 'КГМУ', 'КНИТУ-КХТИ', 'ТИСБИ',
    'Иннополис', 'МГУ', 'СПбГУ', 'ВШЭ', 'МФТИ',
]

SPECIALITIES = [
    'Программная инженерия', 'Информационные системы',
    'Кибербезопасность', 'Прикладная математика',
    'Бизнес-информатика', 'Искусственный интеллект',
]

COMPANIES = [
    ('Яндекс', 'Старший разработчик', 'https://yandex.ru'),
    ('Сбер', 'Технический директор', 'https://sber.ru'),
    ('Тинькофф', 'Head of Engineering', 'https://tinkoff.ru'),
    ('Kaspersky', 'Product Manager', 'https://kaspersky.com'),
    ('1С', 'Руководитель проектов', 'https://1c.ru'),
    ('Mail.ru', 'CTO', 'https://mail.ru'),
    ('Авито', 'Tech Lead', 'https://avito.ru'),
    ('Ozon', 'Директор по разработке', 'https://ozon.ru'),
]

PROJECT_TITLES = [
    'Система управления стажировками',
    'Платформа онлайн-обучения',
    'CRM для малого бизнеса',
    'Мобильное приложение для доставки',
    'Сервис аналитики данных',
    'Чат-бот для поддержки клиентов',
    'Система мониторинга серверов',
    'Маркетплейс фриланс-услуг',
    'Образовательный портал',
    'Сервис управления задачами',
]

PROJECT_DESCRIPTIONS = [
    'Разработка веб-приложения для автоматизации процессов подбора стажёров в крупных компаниях.',
    'Создание платформы для дистанционного обучения с поддержкой видеолекций и тестирования.',
    'Разработка CRM-системы с модулями продаж, аналитики и управления клиентской базой.',
    'Мобильное приложение для курьерской службы с отслеживанием заказов в реальном времени.',
    'Платформа для визуализации и анализа больших данных с дашбордами и отчётами.',
    'Интеллектуальный чат-бот на базе NLP для автоматизации первой линии поддержки.',
    'Система мониторинга инфраструктуры с алертингом и графиками метрик.',
    'Двусторонний маркетплейс для фрилансеров и заказчиков с системой эскроу.',
    'Образовательный портал для школьников с адаптивными учебными программами.',
    'Таск-менеджер с Kanban-досками, таймером и интеграцией с календарём.',
]

TEAM_NAMES = [
    'Alpha Squad', 'ByteForce', 'CodeCraft', 'DevStorm',
    'ErrorNot', 'FastBuild', 'GitGood', 'HackMasters',
    'InnoTeam', 'JavaJets',
]


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми записями'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить тестовые данные перед заполнением',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()

        self.stdout.write('Создаём студентов...')
        students = self.create_students(10)

        self.stdout.write('Создаём партнёров...')
        partners = self.create_partners(8)

        self.stdout.write('Создаём команды...')
        teams = self.create_teams(students, 5)

        self.stdout.write('Создаём проекты...')
        projects = self.create_projects(partners, 10)

        self.stdout.write('Создаём заявки...')
        self.create_applications(projects, students, teams)

        self.stdout.write(self.style.SUCCESS(
            f'\nГотово! Создано: '
            f'{len(students)} студентов, '
            f'{len(partners)} партнёров, '
            f'{len(teams)} команд, '
            f'{len(projects)} проектов.'
        ))

    def clear_data(self):
        self.stdout.write('Очищаем тестовые данные...')
        User.objects.filter(username__startswith='student_').delete()
        User.objects.filter(username__startswith='partner_').delete()
        self.stdout.write(self.style.WARNING('Данные очищены.'))

    def create_students(self, count):
        students = []
        for i in range(1, count + 1):
            username = f'student_{i}'
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(
                    username=username,
                    email=f'student{i}@test.ru',
                    password='testpass123',
                    first_name=f'Студент',
                    last_name=f'{i}',
                )

            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'uni': random.choice(UNIVERSITIES),
                    'course': random.randint(1, 6),
                    'speciality': random.choice(SPECIALITIES),
                    'info': f'Тестовый студент #{i}. Увлекаюсь разработкой и новыми технологиями.',
                }
            )
            students.append(profile)
        return students

    def create_partners(self, count):
        partners = []
        for i, (company, position, website) in enumerate(COMPANIES[:count], 1):
            username = f'partner_{i}'
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(
                    username=username,
                    email=f'partner{i}@test.ru',
                    password='testpass123',
                    first_name='Представитель',
                    last_name=company,
                )

            profile, _ = PartnerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': company,
                    'position': position,
                    'website': website,
                    'is_verified': random.choice([True, False]),
                    'phone': f'+7900{random.randint(1000000, 9999999)}',
                }
            )
            partners.append(profile)
        return partners

    def create_teams(self, students, count):
        teams = []
        for i in range(count):
            captain = students[i]
            team, created = Team.objects.get_or_create(
                name=TEAM_NAMES[i],
                defaults={
                    'description': f'Команда {TEAM_NAMES[i]} — дружный коллектив разработчиков.',
                    'captain': captain,
                }
            )
            if created:
                TeamMember.objects.get_or_create(team=team, student=captain)
                # добавляем ещё 1-2 участника
                other_students = [s for s in students if s != captain]
                for member in random.sample(other_students, min(2, len(other_students))):
                    TeamMember.objects.get_or_create(team=team, student=member)
            teams.append(team)
        return teams

    def create_projects(self, partners, count):
        projects = []
        for i in range(count):
            partner = partners[i % len(partners)]
            project, _ = Project.objects.get_or_create(
                title=PROJECT_TITLES[i],
                defaults={
                    'partner': partner,
                    'description': PROJECT_DESCRIPTIONS[i],
                    'requirements': 'Python, Django, React, PostgreSQL',
                    'deadline': timezone.now() + timedelta(days=random.randint(30, 180)),
                    'max_teams': random.randint(2, 8),
                    'is_active': random.choice([True, True, True, False]),
                }
            )
            projects.append(project)
        return projects

    def create_applications(self, projects, students, teams):
        count = 0
        for project in projects[:5]:
            for student in random.sample(students, min(3, len(students))):
                _, created = ProjectApplication.objects.get_or_create(
                    project=project,
                    student=student,
                )
                if created:
                    count += 1
        self.stdout.write(f'Создано {count} заявок.')
