from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    
    def __str__(self):
        return self.name

class Disease(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[
        ('communicable', 'Communicable'),
        ('non-communicable', 'Non-Communicable'),
    ])
    
    def __str__(self):
        return self.name

class EpidemiologicalData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    date_reported = models.DateField()
    cases = models.IntegerField()
    deaths = models.IntegerField(default=0)
    region = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.country} - {self.disease} - {self.date_reported}"