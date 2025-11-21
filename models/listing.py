from pydantic import BaseModel, Field


class Listing(BaseModel):
    """
    Represents a car listing from riyasewana.com
    """
    title: str
    posted_date: str
    posted_by: str
    contact_info: str
    listing_url: str = Field(..., description="URL of the listing page")
    
