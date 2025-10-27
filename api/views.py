from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import pandas as pd
from data_collection.mongo_utils import mongo_manager

class SubmissionViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        country = request.GET.get('country')
        data = mongo_manager.get_country_summary(country)
        return Response(data)

class PredictionViewSet(viewsets.ViewSet):
    
    def list(self, request):
        # Return predictions list
        return Response([])

def export_data(request):
    format = request.GET.get('format', 'csv')
    df = mongo_manager.export_to_dataframe()
    
    if format == 'excel':
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="disease_data.xlsx"'
        df.to_excel(response, index=False)
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="disease_data.csv"'
        df.to_csv(response, index=False)
    
    return response