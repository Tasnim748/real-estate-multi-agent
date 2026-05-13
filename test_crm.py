import os
import asyncio
from dotenv import load_dotenv
from app.tools import create_crm_lead, match_crm_properties, log_crm_activity

async def main():
    # Load .env file
    load_dotenv()
    
    # Check if CRM API keys are set
    if not os.getenv("CRM_API_BASE_URL") or not os.getenv("CRM_API_KEY"):
        print("Please set CRM_API_BASE_URL and CRM_API_KEY in your .env file.")
        return

    print("--- Testing Milestone 3: CRM Integration ---")
    
    print("\n1. Testing create_crm_lead...")
    lead_result = create_crm_lead.invoke({
        "budget_min": 4000000,
        "budget_max": 5000000,
        "desired_location": "Gulshan",
        "property_type": "apartment",
        "first_name": "Test",
        "last_name": "User",
        "phone": "01711111111",
        "email": "testuser@example.com"
    })
    
    print(f"Result: {lead_result}")
    
    # Extract lead_id to use in subsequent tests
    lead_id = None
    if isinstance(lead_result, dict) and "id" in lead_result:
        lead_id = lead_result["id"]
    elif isinstance(lead_result, dict) and "lead_id" in lead_result:
        lead_id = lead_result["lead_id"]
    
    if lead_id:
        print(f"\n2. Testing log_crm_activity for Lead ID {lead_id}...")
        activity_result = log_crm_activity.invoke({
            "lead_id": lead_id,
            "activity_type": "message",
            "description": "User requested an apartment in Gulshan."
        })
        print(f"Result: {activity_result}")
        
        print(f"\n3. Testing match_crm_properties for Lead ID {lead_id}...")
        match_result = match_crm_properties.invoke({"lead_id": lead_id})
        print(f"Result: {match_result}")
    else:
        print("\nSkipping activity and match tests because lead creation did not return an ID.")
        print("Please ensure your CRM is running and accessible at the base URL.")

if __name__ == "__main__":
    asyncio.run(main())
