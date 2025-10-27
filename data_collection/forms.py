from django import forms
from django.core.exceptions import ValidationError
from datetime import date
import json

class EpidemiologicalDataForm(forms.Form):
    # Basic patient and case information
    report_date = forms.DateField(
        label="Report Date",
        widget=forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()}),
        initial=date.today
    )
    
    patient_age = forms.IntegerField(
        label="Patient Age",
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    patient_sex = forms.ChoiceField(
        label="Patient Sex",
        choices=[
            ('', 'Select Sex'),
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Disease selection - will be populated dynamically
    disease = forms.ChoiceField(
        label="Disease",
        choices=[],  # Will be populated from Parse
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Health facility selection - will be populated dynamically
    health_facility = forms.ChoiceField(
        label="Health Facility",
        choices=[],  # Will be populated from Parse
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Symptoms
    symptoms = forms.CharField(
        label="Symptoms",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter symptoms separated by commas (e.g., fever, cough, headache)'
        }),
        help_text="Separate multiple symptoms with commas"
    )
    
    # Case status
    status = forms.ChoiceField(
        label="Case Status",
        choices=[
            ('suspected', 'Suspected'),
            ('confirmed', 'Confirmed'),
            ('probable', 'Probable'),
            ('recovered', 'Recovered'),
            ('deceased', 'Deceased')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Location data
    latitude = forms.FloatField(
        label="Latitude",
        min_value=-90,
        max_value=90,
        initial=6.515,  # Default Lagos coordinates
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.000001'
        })
    )
    
    longitude = forms.FloatField(
        label="Longitude",
        min_value=-180,
        max_value=180,
        initial=3.375,  # Default Lagos coordinates
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.000001'
        })
    )
    
    # Additional fields from your original form
    cases = forms.IntegerField(
        label="Number of Cases",
        min_value=0,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    
    deaths = forms.IntegerField(
        label="Number of Deaths",
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    
    region = forms.CharField(
        label="Region",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        # Extract dynamic choices passed from view
        diseases = kwargs.pop('diseases', [])
        facilities = kwargs.pop('facilities', [])
        super().__init__(*args, **kwargs)
        
        # Populate disease choices from Parse data
        disease_choices = [('', 'Select Disease')]
        for disease in diseases:
            disease_choices.append((disease['objectId'], disease['name']))
        self.fields['disease'].choices = disease_choices
        
        # Populate facility choices from Parse data
        facility_choices = [('', 'Select Health Facility')]
        for facility in facilities:
            facility_choices.append((facility['objectId'], facility['name']))
        self.fields['health_facility'].choices = facility_choices
    
    def clean_cases(self):
        cases = self.cleaned_data.get('cases')
        if cases < 0:
            raise ValidationError("Cases cannot be negative")
        return cases
    
    def clean_deaths(self):
        deaths = self.cleaned_data.get('deaths', 0)
        cases = self.cleaned_data.get('cases', 0)
        
        if deaths < 0:
            raise ValidationError("Deaths cannot be negative")
        
        if deaths > cases:
            raise ValidationError("Deaths cannot exceed cases")
        
        return deaths
    
    def clean_symptoms(self):
        symptoms = self.cleaned_data.get('symptoms', '')
        # Convert comma-separated symptoms to list and clean each one
        symptom_list = [symptom.strip() for symptom in symptoms.split(',') if symptom.strip()]
        return symptom_list
    
    def clean_latitude(self):
        latitude = self.cleaned_data.get('latitude')
        if not (-90 <= latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90")
        return latitude
    
    def clean_longitude(self):
        longitude = self.cleaned_data.get('longitude')
        if not (-180 <= longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180")
        return longitude

class BulkDataUploadForm(forms.Form):
    # These will be populated from Parse data
    disease = forms.ChoiceField(
        label="Disease",
        choices=[],  # Will be populated from Parse
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    health_facility = forms.ChoiceField(
        label="Health Facility",
        choices=[],  # Will be populated from Parse
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    data_file = forms.FileField(
        label='Upload CSV/Excel File',
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload a CSV or Excel file with columns: date_reported,patient_age,patient_sex,symptoms,status,cases,deaths,region,latitude,longitude'
    )
    
    file_format = forms.ChoiceField(
        label="File Format",
        choices=[
            ('csv', 'CSV'),
            ('excel', 'Excel')
        ],
        initial='csv',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        diseases = kwargs.pop('diseases', [])
        facilities = kwargs.pop('facilities', [])
        super().__init__(*args, **kwargs)
        
        # Populate disease choices
        disease_choices = [('', 'Select Disease')]
        for disease in diseases:
            disease_choices.append((disease['objectId'], disease['name']))
        self.fields['disease'].choices = disease_choices
        
        # Populate facility choices
        facility_choices = [('', 'Select Health Facility')]
        for facility in facilities:
            facility_choices.append((facility['objectId'], facility['name']))
        self.fields['health_facility'].choices = facility_choices
    
    def clean_data_file(self):
        data_file = self.cleaned_data.get('data_file')
        if data_file:
            # Validate file extension
            valid_extensions = ['.csv', '.xlsx', '.xls']
            file_name = data_file.name.lower()
            
            if not any(file_name.endswith(ext) for ext in valid_extensions):
                raise ValidationError(
                    "Unsupported file format. Please upload a CSV or Excel file."
                )
            
            # Validate file size (max 10MB)
            if data_file.size > 10 * 1024 * 1024:
                raise ValidationError("File size must be less than 10MB")
        
        return data_file

class CaseFilterForm(forms.Form):
    """Form for filtering case reports"""
    disease = forms.ChoiceField(
        label="Disease",
        required=False,
        choices=[],  # Will be populated
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=[
            ('', 'All Statuses'),
            ('suspected', 'Suspected'),
            ('confirmed', 'Confirmed'),
            ('probable', 'Probable'),
            ('recovered', 'Recovered'),
            ('deceased', 'Deceased')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        label="From Date",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        label="To Date",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        diseases = kwargs.pop('diseases', [])
        super().__init__(*args, **kwargs)
        
        disease_choices = [('', 'All Diseases')]
        for disease in diseases:
            disease_choices.append((disease['objectId'], disease['name']))
        self.fields['disease'].choices = disease_choices
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError("'From date' cannot be after 'To date'")
        
        return cleaned_data

class AlertForm(forms.Form):
    """Form for creating disease alerts"""
    level = forms.ChoiceField(
        label="Alert Level",
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    disease = forms.ChoiceField(
        label="Disease",
        choices=[],  # Will be populated
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    region = forms.ChoiceField(
        label="Region",
        choices=[],  # Will be populated
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    threshold_count = forms.IntegerField(
        label="Case Threshold",
        min_value=1,
        initial=10,
        help_text="Number of cases that triggers this alert",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    window_days = forms.IntegerField(
        label="Time Window (days)",
        min_value=1,
        max_value=30,
        initial=7,
        help_text="Number of days to consider for threshold",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        label="Alert Notes",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional information about this alert...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        diseases = kwargs.pop('diseases', [])
        regions = kwargs.pop('regions', [])
        super().__init__(*args, **kwargs)
        
        # Populate disease choices
        disease_choices = [('', 'Select Disease')]
        for disease in diseases:
            disease_choices.append((disease['objectId'], disease['name']))
        self.fields['disease'].choices = disease_choices
        
        # Populate region choices
        region_choices = [('', 'Select Region')]
        for region in regions:
            region_choices.append((region['objectId'], region['name']))
        self.fields['region'].choices = region_choices