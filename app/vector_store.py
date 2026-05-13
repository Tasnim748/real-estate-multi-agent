import os
import chromadb
import urllib.request
import json
from app.tools import get_headers, get_api_base

CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="properties")

def sync_properties_from_crm():
    """
    ETL process to fetch properties from the CRM and index them in ChromaDB.
    """
    url = f"{get_api_base()}/api/v1/properties/"
    req = urllib.request.Request(url, headers=get_headers(), method='GET')
    
    try:
        with urllib.request.urlopen(req) as response:
            # Assuming the response is a list of property dictionaries
            properties = json.loads(response.read().decode('utf-8'))
            
            ids = []
            documents = []
            metadatas = []
            
            for prop in properties:
                prop_id = str(prop.get("id"))
                ids.append(prop_id)
                
                # Create a text representation for the vector embedding
                desc = f"{prop.get('title')} in {prop.get('location')}. Type: {prop.get('property_type')}. Price: {prop.get('asking_price')} BDT. {prop.get('bedrooms')} beds, {prop.get('bathrooms')} baths."
                documents.append(desc)
                
                metadatas.append({
                    "location": prop.get("location", ""),
                    "property_type": prop.get("property_type", ""),
                    "asking_price": prop.get("asking_price", 0)
                })
                
            if ids:
                collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                return f"Successfully synced {len(ids)} properties."
            return "No properties found to sync."
    except Exception as e:
        return f"Failed to sync properties: {str(e)}"

def search_properties(query: str, n_results: int = 3):
    """
    Query ChromaDB for properties matching the string.
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    formatted_results = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        meta = results["metadatas"][0]
        for i in range(len(docs)):
            formatted_results.append({
                "description": docs[i],
                "metadata": meta[i]
            })
            
    return formatted_results
