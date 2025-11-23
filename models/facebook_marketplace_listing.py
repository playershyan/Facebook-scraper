"""
Pydantic model for Facebook Marketplace listing data.
This model defines the structure and validation for scraped Facebook Marketplace listings.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class FacebookMarketplaceListing(BaseModel):
    """
    Model representing a Facebook Marketplace listing.

    Attributes:
        title: The listing title/name
        price: The listing price (e.g., "$5,000", "Free")
        location: Geographic location of the item
        image_url: URL to the listing's primary image
        listing_url: Direct URL to the Facebook Marketplace listing
        mileage: Vehicle mileage (for vehicles category)
        description: Seller's description/message
        transmission: Transmission type (e.g., "Automatic", "Manual")
        year: Vehicle year (for vehicles)
        make: Vehicle make/manufacturer (for vehicles)
        model: Vehicle model (for vehicles)
        condition: Item condition (e.g., "New", "Used - Like New")
        posted_date: When the listing was posted
        seller_name: Name of the seller
        category: Marketplace category (e.g., "vehicles", "electronics")
    """

    title: str = Field(..., description="The listing title")
    price: str = Field(..., description="The listing price")
    location: str = Field(..., description="Geographic location")
    image_url: Optional[str] = Field(None, description="URL to listing image")
    listing_url: str = Field(..., description="Facebook Marketplace listing URL")

    # Vehicle-specific fields
    mileage: Optional[str] = Field(None, description="Vehicle mileage")
    transmission: Optional[str] = Field(None, description="Transmission type")
    year: Optional[str] = Field(None, description="Vehicle year")
    make: Optional[str] = Field(None, description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model")

    # Additional fields
    description: Optional[str] = Field(None, description="Seller's description")
    condition: Optional[str] = Field(None, description="Item condition")
    posted_date: Optional[str] = Field(None, description="When listing was posted")
    seller_name: Optional[str] = Field(None, description="Seller name")
    category: Optional[str] = Field(default="general", description="Marketplace category")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "2018 Honda Civic",
                "price": "$15,000",
                "location": "Los Angeles, CA",
                "image_url": "https://example.com/image.jpg",
                "listing_url": "https://www.facebook.com/marketplace/item/123456",
                "mileage": "45,000 miles",
                "transmission": "Automatic",
                "year": "2018",
                "make": "Honda",
                "model": "Civic",
                "description": "Well maintained, single owner",
                "condition": "Used - Excellent",
                "posted_date": "2 days ago",
                "seller_name": "John Doe",
                "category": "vehicles"
            }
        }
