from django import forms
from .models import PartnerProfile


class PartnerProfileForm(forms.ModelForm):
    class Meta:
        model = PartnerProfile
        fields = ['company_name', 'position', 'website', 'phone', 'logo']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'placeholder': 'Например: ООО "Рога и Копыта"',
                'class': 'form-control'
            }),
            'position': forms.TextInput(attrs={
                'placeholder': 'Например: HR-директор',
                'class': 'form-control'
            }),
            'website': forms.URLInput(attrs={
                'placeholder': 'https://чатик-жпт.com',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 993 763 9 333',
                'class': 'form-control'
            }),
        }