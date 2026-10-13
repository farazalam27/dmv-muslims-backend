import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, Integer, ForeignKey, DateTime, Text, JSON, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from db.database import Base

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    role = Column(String(50), default="user")
    auth_provider = Column(String(50))
    is_verified = Column(Boolean, default=False)
    profile_picture_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("Submission", back_populates="submitted_by_user")
    favorites = relationship("Favorite", back_populates="user")

# Restaurant model
class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    halal_status = Column(String(50))  # halal, zabiha, unverified
    serves_alcohol = Column(Boolean)
    serves_pork = Column(Boolean)
    cuisine_types = Column(ARRAY(String))
    price_range = Column(String(10))
    rating = Column(Float)
    data_completeness = Column(Float)
    is_verified = Column(Boolean, default=False)
    
    # Contact
    phone = Column(String(20))
    website = Column(String(255))
    menu_url = Column(String(255))
    
    # Location
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(2))
    lat = Column(Float)
    lng = Column(Float)
    
    # Media
    image_urls = Column(ARRAY(String))
    
    # Tracking
    sources = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scraped_at = Column(DateTime)

# Event model
class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))
    date = Column(DateTime, nullable=False)
    time = Column(String(50))
    end_time = Column(String(50))
    
    # Location
    address = Column(String(255))
    city = Column(String(100))
    lat = Column(Float)
    lng = Column(Float)
    masjid_id = Column(UUID(as_uuid=True), ForeignKey("masjids.id"))
    
    # Organization
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organizer_name = Column(String(255))
    contact_email = Column(String(255))
    speaker = Column(String(255))
    audience = Column(String(100))
    
    # RSVP
    rsvp_link = Column(String(255))
    website = Column(String(255))
    
    # Admin
    is_featured = Column(Boolean, default=False)
    featured_at = Column(DateTime)
    is_approved = Column(Boolean, default=False)
    
    # Recurring
    recurrence_rule = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    masjid = relationship("Masjid", back_populates="events")
    organizer = relationship("User")

# Masjid model
class Masjid(Base):
    __tablename__ = "masjids"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Location
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(2))
    lat = Column(Float)
    lng = Column(Float)
    
    # Contact
    phone = Column(String(20))
    website = Column(String(255))
    email = Column(String(255))
    donation_link = Column(String(255))
    
    # Prayer times
    fajr = Column(String(20))
    dhuhr = Column(String(20))
    asr = Column(String(20))
    maghrib = Column(String(20))
    isha = Column(String(20))
    prayer_times_source = Column(String(255))
    prayer_time_selectors = Column(JSON)
    prayer_times_updated_at = Column(DateTime)
    
    # Media
    image_urls = Column(ARRAY(String))
    
    # Admin
    is_verified = Column(Boolean, default=False)
    is_claimed = Column(Boolean, default=False)
    claimer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = relationship("Event", back_populates="masjid")
    claimer = relationship("User")

# Submission model
class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50))  # restaurant, event, business, masjid
    submission_type = Column(String(50))  # new, update, claim
    entity_data = Column(JSON)
    
    # User info
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected, flagged
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Source
    data_source = Column(String(50))  # user, admin, scraper
    source_details = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submitted_by_user = relationship("User", foreign_keys=[submitted_by], back_populates="submissions")
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])

# Favorite model
class Favorite(Base):
    __tablename__ = "favorites"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    entity_type = Column(String(50), primary_key=True)  # restaurant, event, business
    entity_id = Column(UUID(as_uuid=True), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="favorites")

# Curated Pages model
class CuratedPage(Base):
    __tablename__ = "curated_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50))  # instagram, tiktok
    username = Column(String(255))
    page_type = Column(String(50))  # restaurant, event, general
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# Scraping Logs model
class ScrapingLog(Base):
    __tablename__ = "scraping_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String(100))
    source = Column(String(50))
    status = Column(String(50))  # success, failed, partial
    items_scraped = Column(Integer)
    items_saved = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)