from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
import pandas as pd
from .parse_client import parse_client
from .forms import EpidemiologicalDataForm, BulkDataUploadForm
import urllib3
import requests

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Authentication credentials - UPDATE THESE!
PARSE_USERNAME = "africa_disease_surveillance"  # Replace with actual username from your Back4App
PARSE_PASSWORD = "Secur3P@ss!123"  # Replace with actual password

def ensure_authenticated():
    """Ensure we have a valid session token"""
    try:
        # Try to login if we don't have a session
        if "X-Parse-Session-Token" not in parse_client.headers:
            user = parse_client.login(PARSE_USERNAME, PARSE_PASSWORD)
            if not user:
                print("Failed to authenticate with Parse backend")
                return False
        return True
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

def home(request):
    """Homepage with dashboard overview"""
    try:
        # Get data from Parse backend (read operations don't need auth)
        case_reports = parse_client.get_case_reports(include=["disease", "facility"]) or {}
        diseases = parse_client.get_diseases() or {}
        countries = parse_client.get_countries() or {}
        alerts = parse_client.get_alerts() or {}
        
        # Calculate statistics
        total_cases = len(case_reports.get('results', []))
        total_diseases = len(diseases.get('results', []))
        total_countries = len(countries.get('results', []))
        active_alerts = len([alert for alert in alerts.get('results', []) 
                           if alert.get('status') == 'active'])
        
        # Get recent case reports
        recent_cases = case_reports.get('results', [])[:5]
        
    except Exception as e:
        print(f"Error loading home data: {e}")
        total_cases = 0
        total_diseases = 0
        total_countries = 0
        active_alerts = 0
        recent_cases = []
    
    context = {
        'total_cases': total_cases,
        'total_diseases': total_diseases,
        'total_countries': total_countries,
        'active_alerts': active_alerts,
        'recent_cases': recent_cases,
        'parse_connected': True,
    }
    return render(request, 'home.html', context)

def submit_data(request):
    """Submit individual case reports using Parse backend"""
    try:
        # Get available options from Parse
        diseases_data = parse_client.get_diseases() or {}
        facilities_data = parse_client.get_health_facilities() or {}
        
        diseases = diseases_data.get('results', [])
        facilities = facilities_data.get('results', [])
        
    except Exception as e:
        print(f"Error loading form data: {e}")
        diseases = []
        facilities = []
    
    if request.method == 'POST':
        form = EpidemiologicalDataForm(
            request.POST, 
            diseases=diseases, 
            facilities=facilities
        )
        if form.is_valid():
            try:
                # Ensure we're authenticated for write operations
                if not ensure_authenticated():
                    messages.error(request, 'Authentication failed. Cannot submit data.')
                    return redirect('submit_data')
                
                # Prepare data for Parse backend using helper methods
                case_data = {
                    "reportDate": parse_client.date(form.cleaned_data['report_date'].isoformat() + "T00:00:00.000Z"),
                    "patientAge": form.cleaned_data['patient_age'],
                    "patientSex": form.cleaned_data['patient_sex'],
                    "symptoms": form.cleaned_data['symptoms'],
                    "status": form.cleaned_data['status'],
                    "location": {
                        "__type": "GeoPoint",
                        "latitude": form.cleaned_data['latitude'],
                        "longitude": form.cleaned_data['longitude']
                    },
                    "disease": parse_client.pointer("Disease", form.cleaned_data['disease']),
                    "facility": parse_client.pointer("HealthFacility", form.cleaned_data['health_facility']),
                    "cases": form.cleaned_data['cases'],
                    "deaths": form.cleaned_data['deaths'],
                    "region": form.cleaned_data['region']
                }
                
                # Create case report in Parse
                result = parse_client.create_case_report(case_data)
                
                if result and 'objectId' in result:
                    messages.success(request, 'Case report submitted successfully!')
                    return redirect('submit_data')
                else:
                    messages.error(request, 'Error submitting case report to backend!')
                    
            except Exception as e:
                messages.error(request, f'Backend error: {str(e)}')
    else:
        form = EpidemiologicalDataForm(diseases=diseases, facilities=facilities)
    
    context = {
        'form': form,
        'diseases': diseases,
        'facilities': facilities,
    }
    return render(request, 'data_collection/submit_data.html', context)

def bulk_upload(request):
    """Handle bulk data upload"""
    try:
        # Get available options from Parse
        diseases_data = parse_client.get_diseases() or {}
        facilities_data = parse_client.get_health_facilities() or {}
        
        diseases = diseases_data.get('results', [])
        facilities = facilities_data.get('results', [])
        
    except Exception as e:
        print(f"Error loading bulk upload data: {e}")
        diseases = []
        facilities = []
    
    if request.method == 'POST':
        form = BulkDataUploadForm(
            request.POST, 
            request.FILES,
            diseases=diseases,
            facilities=facilities
        )
        if form.is_valid():
            try:
                # Ensure authentication for write operations
                if not ensure_authenticated():
                    messages.error(request, 'Authentication failed. Cannot upload data.')
                    return redirect('bulk_upload')
                
                disease_id = form.cleaned_data['disease']
                facility_id = form.cleaned_data['health_facility']
                data_file = request.FILES['data_file']
                
                # Process the uploaded file
                if data_file.name.endswith('.csv'):
                    df = pd.read_csv(data_file)
                else:
                    df = pd.read_excel(data_file)
                
                # Process each row
                success_count = 0
                error_count = 0
                
                for index, row in df.iterrows():
                    try:
                        # Prepare case data for each row using helper methods
                        case_data = {
                            "reportDate": parse_client.date(str(row['date_reported']) + "T00:00:00.000Z"),
                            "patientAge": int(row.get('patient_age', 0)),
                            "patientSex": row.get('patient_sex', 'Unknown'),
                            "symptoms": row.get('symptoms', '').split(','),
                            "status": row.get('status', 'suspected'),
                            "location": {
                                "__type": "GeoPoint",
                                "latitude": float(row.get('latitude', 6.515)),
                                "longitude": float(row.get('longitude', 3.375))
                            },
                            "disease": parse_client.pointer("Disease", disease_id),
                            "facility": parse_client.pointer("HealthFacility", facility_id),
                            "cases": int(row.get('cases', 1)),
                            "deaths": int(row.get('deaths', 0)),
                            "region": row.get('region', '')
                        }
                        
                        # Create case report
                        result = parse_client.create_case_report(case_data)
                        if result and 'objectId' in result:
                            success_count += 1
                        else:
                            error_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        print(f"Error processing row {index}: {e}")
                
                if success_count > 0:
                    messages.success(request, f'Successfully uploaded {success_count} records!')
                if error_count > 0:
                    messages.warning(request, f'Failed to upload {error_count} records.')
                    
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = BulkDataUploadForm(diseases=diseases, facilities=facilities)
    
    return render(request, 'data_collection/bulk_upload.html', {'form': form})

def dashboard(request):
    """Comprehensive dashboard with analytics"""
    try:
        # Get data from Parse with included pointers for richer data
        case_reports = parse_client.get_case_reports(include=["disease", "facility"]) or {}
        diseases = parse_client.get_diseases() or {}
        alerts = parse_client.get_alerts() or {}
        
        cases_data = case_reports.get('results', [])
        diseases_data = diseases.get('results', [])
        alerts_data = alerts.get('results', [])
        
        # Calculate statistics
        total_cases = len(cases_data)
        total_deaths = sum(case.get('deaths', 0) for case in cases_data)
        
        # Disease statistics
        disease_stats = {}
        for case in cases_data:
            disease = case.get('disease', {})
            disease_name = disease.get('name', 'Unknown') if isinstance(disease, dict) else 'Unknown'
            if disease_name not in disease_stats:
                disease_stats[disease_name] = {'cases': 0, 'deaths': 0}
            disease_stats[disease_name]['cases'] += case.get('cases', 1)
            disease_stats[disease_name]['deaths'] += case.get('deaths', 0)
        
        # Recent alerts
        active_alerts = [alert for alert in alerts_data if alert.get('status') == 'active']
        
    except Exception as e:
        print(f"Error loading dashboard data: {e}")
        total_cases = 0
        total_deaths = 0
        disease_stats = {}
        active_alerts = []
        cases_data = []
    
    context = {
        'total_cases': total_cases,
        'total_deaths': total_deaths,
        'disease_stats': disease_stats,
        'active_alerts': active_alerts,
        'recent_cases': cases_data[:10],
    }
    return render(request, 'data_collection/dashboard.html', context)

def case_reports(request):
    """View all case reports with filtering"""
    try:
        filters = {}
        
        # Apply filters if provided
        disease_filter = request.GET.get('disease')
        status_filter = request.GET.get('status')
        
        if disease_filter:
            filters['disease'] = parse_client.pointer("Disease", disease_filter)
        
        if status_filter:
            filters['status'] = status_filter
        
        case_reports = parse_client.get_case_reports(filters=filters, include=["disease", "facility"]) or {}
        cases_data = case_reports.get('results', [])
        
        # Get filter options
        diseases = parse_client.get_diseases() or {}
        
    except Exception as e:
        print(f"Error loading case reports: {e}")
        cases_data = []
        diseases = {'results': []}
    
    context = {
        'cases': cases_data,
        'diseases': diseases.get('results', []),
    }
    return render(request, 'data_collection/case_reports.html', context)

def alerts_view(request):
    """View active alerts"""
    try:
        alerts = parse_client.get_alerts() or {}
        alerts_data = alerts.get('results', [])
        
        # Separate active and resolved alerts
        active_alerts = [alert for alert in alerts_data if alert.get('status') == 'active']
        resolved_alerts = [alert for alert in alerts_data if alert.get('status') == 'resolved']
        
    except Exception as e:
        print(f"Error loading alerts: {e}")
        active_alerts = []
        resolved_alerts = []
    
    context = {
        'active_alerts': active_alerts,
        'resolved_alerts': resolved_alerts,
    }
    return render(request, 'data_collection/alerts.html', context)

def api_stats(request):
    """JSON API endpoint for statistics"""
    try:
        case_reports = parse_client.get_case_reports(include=["disease"]) or {}
        diseases = parse_client.get_diseases() or {}
        countries = parse_client.get_countries() or {}
        alerts = parse_client.get_alerts() or {}
        
        cases_data = case_reports.get('results', [])
        
        stats = {
            'total_cases': len(cases_data),
            'total_diseases': len(diseases.get('results', [])),
            'total_countries': len(countries.get('results', [])),
            'active_alerts': len([a for a in alerts.get('results', []) 
                                if a.get('status') == 'active']),
            'total_deaths': sum(case.get('deaths', 0) for case in cases_data),
        }
    except Exception as e:
        print(f"Error loading API stats: {e}")
        stats = {
            'total_cases': 0,
            'total_diseases': 0,
            'total_countries': 0,
            'active_alerts': 0,
            'total_deaths': 0,
        }
    
    return JsonResponse(stats)

def initialize_parse_data(request):
    """Initialize Parse backend connection test"""
    try:
        print("Testing Parse backend connection...")
        
        # Test basic connection
        connection_ok = parse_client.test_connection()
        
        if connection_ok:
            # Test authentication
            auth_ok = ensure_authenticated()
            
            # Get some sample data
            diseases = parse_client.get_diseases(limit=5) or {}
            cases = parse_client.get_case_reports(limit=5, include=["disease", "facility"]) or {}
            
            return JsonResponse({
                'status': 'success',
                'message': 'Parse backend is connected and ready!',
                'authentication': 'successful' if auth_ok else 'failed',
                'sample_data': {
                    'diseases_count': len(diseases.get('results', [])),
                    'cases_count': len(cases.get('results', [])),
                },
                'collections': ['CaseReport', 'Disease', 'Country', 'HealthFacility', 'Alert', 'LabTest']
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Could not connect to Parse backend',
            })
            
    except Exception as e:
        print(f"Initialize error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Connection error: {str(e)}',
        })
    
   