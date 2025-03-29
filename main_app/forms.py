from django import forms
from .models import MainMembers, Dependents, Treasury, TreasuryDep

class MainMembersForm(forms.ModelForm):
    class Meta:
        model = MainMembers
        exclude = ['branch_member_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(choices=[('M', 'Male'), ('F', 'Female')], attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DependentsForm(forms.ModelForm):
    class Meta:
        model = Dependents
        exclude = ['idDependents']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'card_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TreasuryForm(forms.ModelForm):
    class Meta:
        model = Treasury
        fields = '__all__'
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'fund': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TreasuryDepForm(forms.ModelForm):
    class Meta:
        model = TreasuryDep
        fields = '__all__'
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'fund': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
# main_app/forms.py

class TreasuryForm(forms.ModelForm):
    FUND_CHOICES = [
        ('Annual', 'Annual'),
        ('Building Fund', 'Building Fund'),
        ('Thanksgiving', 'Thanksgiving'),
        ('Maintenance', 'Maintenance'),
        ('Blessing', 'Blessing'),
        ('Registration', 'Registration'),
    ]
    
    fund = forms.ChoiceField(choices=FUND_CHOICES)
    
    class Meta:
        model = Treasury
        fields = '__all__'

