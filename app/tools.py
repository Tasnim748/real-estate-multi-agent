import os
import json
import urllib.request
import urllib.error
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

def get_api_base():
    return os.getenv("CRM_API_BASE_URL", "http://localhost:8000")

def get_headers():
    return {
        "Content-Type": "application/json",
        "X-API-Key": os.getenv("CRM_API_KEY", "")
    }

@tool
def create_crm_lead(
    budget_min: int,
    budget_max: int,
    desired_location: str,
    property_type: str, 
    first_name: str = "New",
    last_name: str = "Lead",
    phone: str = "Unknown", 
    email: str = "unknown@example.com",
    source: str = "telegram",
    preferred_channel: str = "whatsapp"
) -> dict:
    """
    Creates a new lead in the CRM using the qualified fields gathered from the user.
    Returns the created lead's data, including the lead_id.
    """
    url = f"{get_api_base()}/api/v1/leads/"
    
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "email": email,
        "source": source,
        "preferred_channel": preferred_channel,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "desired_location": desired_location,
        "property_type_preference": property_type
    }
    
    print(f"CRM Lead Creation Payload: {json.dumps(payload, indent=2)}")
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=get_headers(), method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        # Read the error response body to get detailed validation errors (especially for 422)
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            return {"error": f"HTTP Error {e.code}: {e.reason}", "detail": error_json}
        except:
            return {"error": f"HTTP Error {e.code}: {e.reason}", "detail": error_body}
    except Exception as e:
        return {"error": str(e)}

@tool
def log_crm_activity(
    lead_id: int, 
    activity_type: str, 
    description: str
) -> dict:
    """
    Logs an interaction activity (like a chat summary) against a lead in the CRM.
    """
    url = f"{get_api_base()}/api/v1/leads/{lead_id}/activities"
    
    payload = {
        "activity_type": activity_type,
        "description": description
    }
    
    print(f"CRM Activity Payload: {json.dumps(payload, indent=2)}")
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=get_headers(), method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        return {"error": str(e)}

@tool
def match_crm_properties(
    lead_id: int
) -> dict:
    """
    Fetches matching properties for a lead from the CRM based on their qualified preferences.
    """
    url = f"{get_api_base()}/api/v1/properties/match/{lead_id}"
    
    req = urllib.request.Request(url, headers=get_headers(), method='GET')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        return {"error": str(e)}
