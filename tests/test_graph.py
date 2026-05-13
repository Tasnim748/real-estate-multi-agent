import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.graph import graph
from langchain_core.messages import HumanMessage

async def main():
    # Load .env file
    load_dotenv()

    # Ensure OPENROUTER_API_KEY is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Please set OPENROUTER_API_KEY in your .env file.")
        return

    # Initialize state as it would be passed to the graph
    state = {
        "messages": [HumanMessage(content="I am looking for an apartment in Gulshan with a budget of 5000000 BDT.")],
        "budget_min": None,
        "budget_max": None,
        "desired_location": None,
        "timeline": None,
        "property_type_preference": None,
        "ready_to_sync": False,
        "market_insights": None,
        "top_properties": None,
        "lead_id": None,
        "thread_id": "test_thread"
    }

    print("Running graph...")
    
    try:
        result = await graph.ainvoke(state)
        
        print("\n--- Results ---")
        print(f"Extracted Location: {result.get('desired_location')}")
        print(f"Extracted Budget Max: {result.get('budget_max')}")
        print(f"Ready to Sync: {result.get('ready_to_sync')}")
        
        if "messages" in result and result["messages"]:
            last_msg = result["messages"][-1]
            print(f"\nLast Agent Message:\n{last_msg.content}")
            
    except Exception as e:
        print(f"Error running graph: {e}")

if __name__ == "__main__":
    asyncio.run(main())
