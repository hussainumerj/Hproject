from django import forms
from .models import Department, Team, TeamType, Dependency


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'specialisation', 'leader']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'specialisation': forms.TextInput(attrs={'class': 'form-control'}),
            'leader': forms.Select(attrs={'class': 'form-select'}),
        }


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'name', 'description', 'purpose', 'department',
            'team_type', 'manager', 'members',
            'slack_channel', 'email', 'code_repository', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'team_type': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'members': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'slack_channel': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'code_repository': forms.URLInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class DependencyForm(forms.ModelForm):
    class Meta:
        model = Dependency
        fields = ['upstream_team', 'downstream_team', 'description']
        widgets = {
            'upstream_team': forms.Select(attrs={'class': 'form-select'}),
            'downstream_team': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        upstream = cleaned_data.get('upstream_team')
        downstream = cleaned_data.get('downstream_team')
        if upstream and downstream and upstream == downstream:
            raise forms.ValidationError('A team cannot depend on itself.')
        return cleaned_data
