from django.db import models

class MLModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    accuracy = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('training', 'Training'),
        ('inactive', 'Inactive'),
    ], default='active')
    last_trained = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Prediction(models.Model):
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    disease = models.CharField(max_length=100)
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ])
    probability = models.FloatField()
    expected_cases = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.country} - {self.disease} - {self.risk_level}"