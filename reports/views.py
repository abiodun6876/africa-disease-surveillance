from django.shortcuts import render
from django.http import HttpResponse
from .report_generators.pdf_generator import PDFReportGenerator
from .report_generators.excel_generator import ExcelReportGenerator

def generate_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        country = request.POST.get('country')
        
        if report_type == 'pdf':
            generator = PDFReportGenerator()
            pdf_file = generator.generate_country_report(country)
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{country}_report.pdf"'
            return response
            
        elif report_type == 'excel':
            generator = ExcelReportGenerator()
            excel_file = generator.generate_country_report(country)
            response = HttpResponse(excel_file, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{country}_report.xlsx"'
            return response
    
    return render(request, 'reports/generate.html')

def report_list(request):
    return render(request, 'reports/report_list.html')

def download_report(request, report_id):
    # Download logic here
    return HttpResponse("Download report")