import requests
import json

def check_parse_data():
    app_id = "K6lQVSqx3B7BU5ePJ1SvdhtXQN7h8S9OMEdOOuNj"
    rest_api_key = "cLxvBXdulLXGklKbBi9Lbhj6Q07CXvVDskWFTZ8K"
    
    headers = {
        "X-Parse-Application-Id": app_id,
        "X-Parse-REST-API-Key": rest_api_key,
        "Content-Type": "application/json"
    }
    
    print("🔍 Checking what data exists in your Parse backend...")
    print("=" * 50)
    
    classes = [
        ('Disease', 'Diseases'),
        ('Country', 'Countries'), 
        ('HealthFacility', 'Health Facilities'),
        ('CaseReport', 'Case Reports'),
        ('Alert', 'Alerts'),
        ('_User', 'Users'),
        ('LabTest', 'Lab Tests')
    ]
    
    for class_name, display_name in classes:
        url = f"https://parseapi.back4app.com/classes/{class_name}"
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', []))
                if count > 0:
                    print(f"✅ {display_name}: {count} records")
                    # Show first item as sample
                    first_item = data['results'][0]
                    print(f"   Sample: {json.dumps(first_item, indent=2)[:200]}...")
                else:
                    print(f"📭 {display_name}: No records (empty)")
            elif response.status_code == 403:
                print(f"🔒 {display_name}: Permission denied (403)")
            else:
                print(f"❌ {display_name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {display_name}: Error - {e}")
    
    print("=" * 50)
    print("💡 If you see 'Permission denied', you need to:")
    print("   1. Get your Master Key from Back4App Dashboard")
    print("   2. Update parse_client.py with the Master Key")
    print("   3. Or fix Class-Level Permissions in Back4App")

if __name__ == "__main__":
    check_parse_data()