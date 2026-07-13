from django import forms
from .models import Project, PartnerProfile


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'requirements', 'preview', 'deadline', 'max_teams']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Например: Написание промтов в дипсик',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Подробно опишите проект, цели и ожидаемый результат...',
                'class': 'form-control'
            }),
            'requirements': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Например: знание Python, опыт работы с чатиком жпт...',
                'class': 'form-control'
            }),
            'preview': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'max_teams': forms.NumberInput(attrs={
                'min': 1,
                'max': 10,
                'class': 'form-control',
                'placeholder': 'От 1 до 10'
            }),
        }

        labels = {
            'title': 'Название проекта',
            'description': 'Описание',
            'requirements': 'Требования к участникам',
            'preview': 'Изображение проекта',
            'deadline': 'Дедлайн',
            'max_teams': 'Максимальное количество команд',
        }

        help_texts = {
            'requirements': 'Опишите, какие навыки и знания нужны для выполнения проекта',
            'preview': 'Загрузите картинку для проекта (опционально)',
            'max_teams': 'Сколько команд могут одновременно работать над проектом',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requirements'].required = False
        self.fields['preview'].required = False

class PartnerProfileForm(forms.ModelForm):
    class Meta:
        model = PartnerProfile
        fields = ['company_name', 'position', 'website']