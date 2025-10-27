from django.contrib import admin
from .models import Country, Disease, EpidemiologicalData

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']

@admin.register(EpidemiologicalData)
class EpidemiologicalDataAdmin(admin.ModelAdmin):
    list_display = ['country', 'disease', 'date_reported', 'cases', 'deaths']
    list_filter = ['country', 'disease', 'date_reported']