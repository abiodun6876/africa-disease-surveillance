import os
import json
import requests
from django.conf import settings
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ParseClient:
    def __init__(
        self,
        app_id=None,
        rest_api_key=None,
        master_key=None,
        base_url="https://parseapi.back4app.com",
        session_token=None,
        timeout=30,
    ):
        # Use your actual credentials
        self.app_id = app_id or "K6lQVSqx3B7BU5ePJ1SvdhtXQN7h8S9OMEdOOuNj"
        self.rest_api_key = rest_api_key or "cLxvBXdulLXGklKbBi9Lbhj6Q07CXvVDskWFTZ8K"
        self.master_key = master_key or "c7RPaycZmbjf5TBi8vKCKZ29iNnaTkHaGqiulRyf"  # IMPORTANT: Get this from Back4App
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.headers = {
            "X-Parse-Application-Id": self.app_id,
            "X-Parse-REST-API-Key": self.rest_api_key,
            "Content-Type": "application/json",
        }
        
        # Add master key for full access
        if self.master_key and self.master_key != "YOUR_MASTER_KEY_HERE":
            self.headers["X-Parse-Master-Key"] = self.master_key
            print("✅ Using Master Key for full access")
        else:
            print("⚠️  Master Key not set - some operations may fail")

        print(f"Parse Client initialized with App ID: {self.app_id[:10]}...")

    @staticmethod
    def pointer(class_name, object_id):
        return {"__type": "Pointer", "className": class_name, "objectId": object_id}

    @staticmethod
    def date(iso_str):
        return {"__type": "Date", "iso": iso_str}

    @staticmethod
    def geo(latitude, longitude):
        return {"__type": "GeoPoint", "latitude": latitude, "longitude": longitude}

    def make_request(self, method, endpoint, data=None, params=None, ok_status=None):
        """Generic HTTP request to Parse REST API"""
        ok_status = ok_status or {200, 201}
        url = f"{self.base_url}{endpoint}"
        
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=self.timeout,
                verify=False  # Disable SSL verification for now
            )
            
            if resp.status_code in ok_status:
                if resp.content and resp.headers.get("Content-Type", "").startswith("application/json"):
                    return resp.json()
                return {"success": True}
            
            print(f"HTTP {resp.status_code} error on {method} {url}")
            if resp.status_code == 403:
                print("💡 403 Error: Need Master Key or proper permissions")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    # Basic connectivity test
    def test_connection(self):
        result = self.make_request("GET", "/classes/Disease", params={"limit": 1})
        return result is not None

    # Data operations
    def get_diseases(self, limit=100):
        return self.make_request("GET", "/classes/Disease", params={"limit": limit})

    def get_health_facilities(self, limit=100):
        return self.make_request("GET", "/classes/HealthFacility", params={"limit": limit})

    def get_case_reports(self, limit=100, include=None):
        params = {"limit": limit}
        if include:
            params["include"] = ",".join(include)
        return self.make_request("GET", "/classes/CaseReport", params=params)

    def get_countries(self, limit=100):
        return self.make_request("GET", "/classes/Country", params={"limit": limit})

    def get_alerts(self, limit=100):
        return self.make_request("GET", "/classes/Alert", params={"limit": limit})

    def create_case_report(self, case_data):
        return self.make_request("POST", "/classes/CaseReport", data=case_data, ok_status={201})

# Global instance - UPDATE THE MASTER KEY!
parse_client = ParseClient(
    master_key="c7RPaycZmbjf5TBi8vKCKZ29iNnaTkHaGqiulRyf"  # ← REPLACE THIS
)