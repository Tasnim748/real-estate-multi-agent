from typing import Annotated, TypedDict
import operator
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

# Pydantic model for extracting fields from the user's message
class QualifierSchema(BaseModel):
    budget_min: int | None = Field(default=None, description="Minimum budget in BDT")
    budget_max: int | None = Field(default=None, description="Maximum budget in BDT")
    desired_location: str | None = Field(default=None, description="Desired location or neighborhood")
    timeline: str | None = Field(default=None, description="Expected timeline to buy/rent")
    property_type_preference: str | None = Field(default=None, description="Type of property, e.g., apartment, house, commercial")

# LangGraph State
class AgentState(TypedDict):
    # The conversation history
    messages: Annotated[list[BaseMessage], operator.add]
    
    # Extracted entity fields
    budget_min: int | None
    budget_max: int | None
    desired_location: str | None
    timeline: str | None
    property_type_preference: str | None
    
    # Metadata and workflow flags
    lead_id: int | None
    thread_id: str | None
    ready_to_sync: bool
    market_insights: str | None
    top_properties: list[dict] | None
