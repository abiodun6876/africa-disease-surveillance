from django.shortcuts import render
from django.http import JsonResponse

def predict_outbreak(request):
    if request.method == 'POST':
        # ML prediction logic will go here
        return JsonResponse({'status': 'success', 'prediction': {}})
    return render(request, 'ml_predictions/predict.html')

def model_list(request):
    # Mock data instead of database models
    models = [
        {
            'id': 1,
            'name': 'Outbreak Risk Predictor',
            'description': 'Predicts disease outbreak risks based on historical data',
            'accuracy': 87.5,
            'status': 'active',
            'last_trained': '2024-01-15'
        },
        {
            'id': 2,
            'name': 'Case Trend Analyzer', 
            'description': 'Analyzes case trends and seasonal patterns',
            'accuracy': 92.1,
            'status': 'active',
            'last_trained': '2024-01-10'
        }
    ]
    return render(request, 'ml_predictions/model_list.html', {'models': models})

def train_model(request):
    # Model training logic will go here
    return JsonResponse({'status': 'training_started'})