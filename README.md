# 🕌 DMV Muslims Backend

**A modern, community-driven platform helping Muslims in the DMV discover halal food, Muslim-owned businesses, local events, and masjids.**

This is the backend API and data aggregation system. It collects halal restaurant data, business listings, events, and masjid information from multiple sources (Google Maps, Instagram, TikTok, masjid websites, user submissions), normalizes the data, and serves it via a REST API for the frontend app to consume.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Core Entities](#core-entities)
- [Data Scraping](#data-scraping)
- [API Endpoints](#api-endpoints)
- [User Roles & Permissions](#user-roles--permissions)
- [Moderation & Admin Workflows](#moderation--admin-workflows)
- [Deployment](#deployment)
- [Development](#development)
- [Roadmap](#roadmap)

---

## 🎯 Overview

### Problem

Muslims in the DMV struggle to:
- Find verified halal and zabiha food options
- Discover local Muslim-owned businesses
- Stay updated on community events
- Access accurate masjid information (prayer times, locations, programs)

### Solution

DMV Muslims provides:
- **Halal Food Discovery**: Map-based directory with filters (cuisine, zabiha status, price, alcohol/pork-free)
- **Business Directory**: Verified Muslim-owned businesses by category
- **Event Calendar**: Community events with RSVP integration
- **Masjid Listings**: Prayer times, locations, events, donation links
- **Admin Moderation**: User submissions reviewed before publishing
- **Data Aggregation**: Automatic scraping from Instagram, TikTok, Google Maps, and masjid websites

### Tech Stack

- **Backend**: FastAPI (async Python)
- **Database**: PostgreSQL (with async driver)
- **Task Queue**: Celery + Redis (for scheduled scraping)
- **Auth & Storage**: Supabase (social login, file storage)
- **Scraping**: Playwright, BeautifulSoup, Google Maps API, Instagram/TikTok API
- **Deployment**: Docker + cloud platform (AWS, GCP, DigitalOcean)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (for local dev)
- Git

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/dmv-muslims-backend.git
cd dmv-muslims-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Fill in `.env` with:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dmv_muslims

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Supabase (Auth & Storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
INSTAGRAM_API_KEY=your_instagram_api_key (if using official API)
TIKTOK_API_KEY=your_tiktok_api_key (if available)

# Application
ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-for-jwt
LOG_LEVEL=INFO
DEFAULT_REGION=dmv

# Email (for notifications)
RESEND_API_KEY=your_resend_key  # For transactional emails

# Scraping Config
SCRAPER_RUN_HOUR=2  # Daily run at 2 AM UTC
ENABLE_INSTAGRAM_SCRAPING=True
ENABLE_TIKTOK_SCRAPING=False
```

### 3. Start Local Environment

```bash
docker-compose up -d
```

This starts PostgreSQL, Redis, and migrations automatically.

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start Services

**Terminal 1: FastAPI app**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Celery worker** (for scraping tasks)
```bash
celery -A tasks.celery_app worker --loglevel=info
```

**Terminal 3: Celery beat** (for scheduling)
```bash
celery -A tasks.celery_app beat --loglevel=info
```

### 6. Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

---

## 🏗️ Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
├─────────────────────────────────────────────────────────────┤
│  Google Maps API  │  Instagram Scraper  │  TikTok Scraper   │
│  Masjid Websites  │  User Submissions   │  Business Claims  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 SCRAPING LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  • Daily scheduled jobs (Celery Beat)                       │
│  • On-demand scraping (API endpoint)                        │
│  • Data extraction & normalization                          │
│  • Partial saves for incomplete data                        │
│  • Deduplication & conflict resolution                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              MODERATION QUEUE                               │
├─────────────────────────────────────────────────────────────┤
│  • Pending user submissions                                 │
│  • Pending scraped data                                     │
│  • Flag reviews from admins                                 │
│  • Notifications to moderators                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (PostgreSQL)                          │
├─────────────────────────────────────────────────────────────┤
│  Users  │  Businesses  │  Events  │  Masjids  │  Listings   │
│  Claims │  Submissions │  Logs    │  Images   │  Favorites  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              REST API (FastAPI)                             │
├─────────────────────────────────────────────────────────────┤
│  GET /api/restaurants  │  GET /api/events  │  GET /api/maps  │
│  POST /api/submissions │  POST /api/claims │  Etc.           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         FRONTEND (React) & MOBILE                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
dmv-muslims-backend/
├── .env.example                  # Environment template
├── .gitignore
├── docker-compose.yml            # Local dev environment
├── Dockerfile                    # Production image
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Database migrations config
│
├── main.py                       # FastAPI app entry point
├── config.py                     # Pydantic Settings
│
├── agents/                       # Data scrapers
│   ├── __init__.py
│   ├── base_agent.py            # Abstract base class
│   ├── google_maps_agent.py     # Google Places API
│   ├── instagram_agent.py       # Instagram scraper
│   ├── tiktok_agent.py          # TikTok scraper
│   ├── masjid_site_agent.py     # Website scraper for masjids
│   └── utils.py                 # Shared utilities
│
├── core/                         # Business logic
│   ├── __init__.py
│   ├── schema.py                # Pydantic models
│   ├── normalizer.py            # Data normalization
│   ├── deduplicator.py          # Duplicate detection
│   └── constants.py             # Regions, categories, etc.
│
├── db/                           # Database layer
│   ├── __init__.py
│   ├── models.py                # SQLAlchemy ORM models
│   ├── database.py              # Async connection
│   ├── queries.py               # Common queries
│   ├── migrations/              # Alembic migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/            # Migration files
│   └── init_db.py               # Seed data
│
├── api/                          # REST API
│   ├── __init__.py
│   ├── routes/
│   │   ├── auth.py              # Auth endpoints
│   │   ├── restaurants.py       # Halal food endpoints
│   │   ├── businesses.py        # Business directory
│   │   ├── events.py            # Event calendar
│   │   ├── masjids.py           # Masjid listings
│   │   ├── submissions.py       # User submissions
│   │   ├── admin.py             # Admin panel
│   │   ├── map.py               # Map data
│   │   └── health.py            # Health checks
│   ├── deps.py                  # Dependencies (auth, DB)
│   ├── middleware.py            # CORS, logging, etc.
│   └── schemas.py               # Request/response schemas
│
├── tasks/                        # Background jobs
│   ├── __init__.py
│   ├── celery_app.py            # Celery configuration
│   ├── scheduled_tasks.py       # Daily scraping jobs
│   └── orchestrator.py          # Coordinates all scrapers
│
├── supabase_client/             # Supabase integration
│   ├── __init__.py
│   ├── auth.py                  # Auth helper functions
│   └── storage.py               # File storage helper
│
├── notifications/               # Email & alerts
│   ├── __init__.py
│   └── email.py                 # Resend API integration
│
├── utils/                        # Utilities
│   ├── __init__.py
│   ├── logger.py                # Logging setup
│   └── helpers.py               # General helpers
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Fixtures
│   ├── test_schema.py
│   ├── test_normalizer.py
│   ├── test_agents/
│   ├── test_api/
│   └── test_tasks/
│
└── README.md
```

---

## 🍽️ Core Entities

### 1. Restaurant/Business (Primary Entity)

```python
# core/schema.py
class Restaurant(BaseModel):
    id: str
    name: str
    description: str
    location: Location
    contact: Contact
    
    # Halal info
    halal_status: Literal["halal", "zabiha", "unverified"]
    halal_verified_by: List[str]  # ["google_maps", "instagram", "user"]
    
    # Dietary restrictions
    serves_alcohol: Optional[bool]
    serves_pork: Optional[bool]
    
    # Business info
    hours: Dict[str, str]  # {"Monday": "11am-10pm"}
    phone: str
    website: str
    menu_url: Optional[str]
    
    # Categorization
    cuisine_type: List[str]  # ["Pakistani", "Arab", "Turkish"]
    price_range: Literal["$", "$$", "$$$", "$$$$"]
    rating: Optional[float]  # From Google Maps
    
    # Images & media
    image_urls: List[str]  # From Google Maps, Instagram, etc.
    
    # Tracking
    sources: List[str]  # ["google_maps", "instagram"]
    data_completeness: float  # 0.0-1.0
    is_verified: bool  # Admin verified
    
    created_at: datetime
    updated_at: datetime
    scraped_at: Optional[datetime]
```

### 2. Event

```python
class Event(BaseModel):
    id: str
    title: str
    description: str
    
    # Timing
    date: date
    time: time
    end_time: Optional[time]
    recurring: Optional[RecurrenceRule]  # For Jummah, weekly halaqas
    
    # Location
    location: Location
    masjid_id: Optional[str]  # Linked masjid
    
    # Organization
    organizer_id: str  # User ID
    organizer_name: str
    contact_email: str
    
    # Content
    event_type: Literal["iftaar", "halaqah", "eid", "fundraiser", "other"]
    speaker: Optional[str]
    audience: Optional[str]  # "Adults", "Youth", "Families"
    image_url: Optional[str]
    
    # RSVP & External Links
    rsvp_link: Optional[str]  # Eventbrite, Ticket Tailor, etc.
    website: Optional[str]
    
    # Featured events
    is_featured: bool  # Admin-selected for homepage
    featured_at: Optional[datetime]
    
    is_approved: bool
    created_at: datetime
    updated_at: datetime
```

### 3. Masjid

```python
class Masjid(BaseModel):
    id: str
    name: str
    location: Location
    
    # Prayer times (updated daily via scraper)
    prayer_times: PrayerTimes  # {fajr, dhuhr, asr, maghrib, isha}
    prayer_times_source: str  # URL of scraped website
    prayer_times_updated_at: datetime
    prayer_time_selectors: Optional[Dict]  # CSS selectors for scraping
    
    # Contact & Links
    phone: str
    website: str
    email: Optional[str]
    donation_link: Optional[str]
    
    # Additional info
    description: str
    images: List[str]
    
    # Events held at this masjid
    events: List[str]  # Event IDs
    
    # Admin controls
    is_verified: bool
    is_claimed: bool  # Business owner/masjid rep claimed this
    claimer_id: Optional[str]  # User ID of claimer
    
    created_at: datetime
    updated_at: datetime
```

### 4. User

```python
class User(BaseModel):
    id: str
    email: str
    name: str
    role: Literal["user", "business_owner", "event_organizer", "masjid_rep", "admin"]
    
    # Supabase auth
    supabase_id: str  # From Supabase Auth
    auth_provider: Literal["email", "google", "apple"]
    
    # Profile
    profile_picture: Optional[str]  # Supabase storage URL
    bio: Optional[str]
    
    # Permissions
    is_verified: bool  # Email verified or admin verified
    verified_at: Optional[datetime]
    
    # User data
    saved_restaurants: List[str]  # Restaurant IDs
    saved_events: List[str]  # Event IDs
    saved_businesses: List[str]  # Business IDs
    
    # Submission history
    submissions: List[str]  # IDs of user submissions
    claims: List[str]  # IDs of business claims
    
    created_at: datetime
    updated_at: datetime
```

### 5. Submission (For Moderation)

```python
class Submission(BaseModel):
    id: str
    entity_type: Literal["restaurant", "business", "event", "masjid"]
    entity_data: dict  # Partial or complete entity data
    
    # Submission info
    submitted_by: str  # User ID
    submission_type: Literal["new", "update", "claim"]
    
    # Status
    status: Literal["pending", "approved", "rejected"]
    reviewed_by: Optional[str]  # Admin user ID
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    
    # Source
    data_source: Literal["user", "admin", "scraper"]
    source_details: Optional[dict]
    
    created_at: datetime
    updated_at: datetime
```

---

## 🕷️ Data Scraping

### Scrapers Overview

| Source | Agent | Frequency | Data |
|--------|-------|-----------|------|
| Google Maps | `GoogleMapsAgent` | Daily | Restaurants, hours, ratings, images |
| Instagram | `InstagramAgent` | Daily | Restaurant posts, event flyers, hashtags |
| TikTok | `TikTokAgent` | Daily (if enabled) | Event videos, restaurant posts |
| Masjid Websites | `MasjidSiteAgent` | Daily | Prayer times, events, announcements |
| User Submissions | Admin Panel | On demand | Any entity type |

### Scraping Flow

#### 1. **Daily Scheduled Scraping** (Celery Beat at 2 AM UTC)

```python
# tasks/scheduled_tasks.py
@app.task
def daily_scraping_job():
    """Run all scrapers daily"""
    orchestrator = Orchestrator()
    
    # Run all agents
    results = asyncio.run(orchestrator.run_all_agents(region="dmv"))
    
    # Results go to moderation queue
    for item in results:
        queue_for_moderation(item)
```

#### 2. **On-Demand Scraping** (API endpoint)

```python
# api/routes/admin.py
@router.post("/admin/trigger-scrape/{source}")
async def trigger_scrape(source: str, db: AsyncSession = Depends(get_db)):
    """Manually trigger a specific scraper"""
    orchestrator = Orchestrator()
    results = await orchestrator.run_agent(source)
    return {"scraped_items": len(results), "status": "queued"}
```

#### 3. **Data Extraction & Normalization**

```python
# tasks/orchestrator.py
class Orchestrator:
    async def run_all_agents(self, region: str):
        agents = [
            GoogleMapsAgent(region),
            InstagramAgent(region),
            MasjidSiteAgent(region),
            TikTokAgent(region),
        ]
        
        results = []
        for agent in agents:
            try:
                data = await agent.collect()  # Scraping happens here
                normalized = normalizer.normalize(data, agent.source_type)
                results.append(normalized)
            except Exception as e:
                logger.error(f"Agent {agent.name} failed: {e}")
                # Continue with other agents
        
        return results
```

#### 4. **Deduplication & Conflict Resolution**

```python
# core/deduplicator.py
class Deduplicator:
    async def deduplicate(self, items: List[dict]):
        """Find duplicates across sources and merge"""
        duplicates = find_similar_items(items)  # Fuzzy matching
        
        for dup_group in duplicates:
            # Merge data, prefer verified sources
            merged = merge_items(dup_group)
            yield merged
```

#### 5. **Partial Saves** (For Incomplete Data)

```python
# db/queries.py
async def save_restaurant(data: dict, db: AsyncSession):
    """Save restaurant, even if some fields are missing"""
    
    # Calculate completeness score
    completeness = calculate_completeness(data)
    
    if completeness >= 0.3:  # Accept if 30%+ complete
        restaurant = Restaurant(
            name=data.get("name"),
            location=data.get("location"),
            halal_status=data.get("halal_status", "unverified"),
            data_completeness=completeness,
            # ... other fields
        )
        db.add(restaurant)
        await db.commit()
        return restaurant
    else:
        logger.warning(f"Data too incomplete (${completeness}): {data}")
        return None
```

### Masjid Prayer Time Scraping

```python
# agents/masjid_site_agent.py
class MasjidSiteAgent(BaseAgent):
    async def collect(self):
        """Scrape masjids for daily prayer times"""
        
        # Get all masjids with scraping config
        masjids = await db.query(Masjid).filter(
            Masjid.prayer_time_selectors != None
        ).all()
        
        results = []
        for masjid in masjids:
            try:
                times = await self.scrape_prayer_times(
                    masjid.prayer_times_source,
                    masjid.prayer_time_selectors
                )
                results.append({
                    "masjid_id": masjid.id,
                    "prayer_times": times,
                    "source": masjid.prayer_times_source
                })
            except Exception as e:
                logger.error(f"Failed to scrape {masjid.name}: {e}")
                # Partial save: update with whatever data we got
        
        return results
    
    async def scrape_prayer_times(self, url: str, selectors: dict):
        """Use Playwright to scrape dynamic websites"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            
            times = {}
            for prayer, selector in selectors.items():
                times[prayer] = await page.text_content(selector)
            
            await browser.close()
            return times
```

### Instagram Scraping

```python
# agents/instagram_agent.py
class InstagramAgent(BaseAgent):
    async def collect(self):
        """Scrape manually curated Instagram pages"""
        
        # Get list of pages to scrape from DB
        pages = await db.query(CuratedPage).filter(
            CuratedPage.source == "instagram",
            CuratedPage.is_active == True
        ).all()
        
        results = []
        for page in pages:
            posts = await self.scrape_page(page.username)
            
            for post in posts:
                # Extract restaurant name, location, halal status from caption
                extracted = self.extract_data_from_post(post)
                results.append(extracted)
        
        return results
    
    def extract_data_from_post(self, post):
        """Parse caption for restaurant name, location, halal info"""
        caption = post["caption"]
        
        return {
            "name": extract_restaurant_name(caption),
            "location": extract_location(caption),
            "halal_status": "zabiha" if "zabiha" in caption.lower() else "halal",
            "image_url": post["image_url"],
            "source": "instagram",
            "source_url": post["url"]
        }
```

---

## 🔌 API Endpoints

### Base URL: `http://localhost:8000/api`

### Authentication

**All endpoints** use Supabase JWT tokens. Include in headers:

```
Authorization: Bearer <supabase_jwt_token>
```

### Public Endpoints (No Auth Required)

#### Restaurants

```bash
GET /restaurants                  # List all restaurants
  ?cuisine=Pakistani,Arab         # Filter by cuisine (comma-separated)
  ?zabiha=true                    # Only zabiha-certified
  ?alcohol_free=true              # No alcohol served
  ?pork_free=true                 # No pork served
  ?price_range=$                  # $ to $$$$
  ?rating_min=4.0                 # Minimum rating
  ?limit=20&offset=0              # Pagination

GET /restaurants/search           # Full-text search
  ?q=kabab

GET /restaurants/{id}             # Get single restaurant
GET /restaurants/nearby           # Nearby restaurants (geo query)
  ?lat=38.8951&lng=-77.0369&radius_km=5
```

#### Events

```bash
GET /events                       # List all events
  ?event_type=iftaar,halaqah      # Filter by type
  ?featured=true                  # Featured only
  ?start_date=2025-01-20          # ISO format
  ?end_date=2025-02-20

GET /events/upcoming              # Next 7 days
GET /events/{id}                  # Single event details
GET /events/by-masjid/{masjid_id} # Events at specific masjid
```

#### Masjids

```bash
GET /masjids                      # List all masjids
  ?city=Falls%20Church

GET /masjids/{id}                 # Single masjid (includes prayer times)
GET /masjids/nearby               # Nearby masjids
  ?lat=38.8951&lng=-77.0369&radius_km=5

GET /masjids/{id}/prayer-times    # Today's prayer times
```

#### Businesses

```bash
GET /businesses                   # List all Muslim-owned businesses
  ?category=restaurant,halal

GET /businesses/{id}
```

#### Map Data

```bash
GET /map/markers                  # Get all markers for map
  ?type=restaurant,event,masjid   # Filter by type
  ?zoom_level=12                  # For clustering

Returns:
{
  "restaurants": [{lat, lng, name, id, ...}],
  "events": [...],
  "masjids": [...]
}
```

### Protected Endpoints (Auth Required)

#### User Profile

```bash
GET /auth/me                      # Current user profile
PATCH /auth/me                    # Update profile

GET /auth/favorites               # User's saved items
POST /auth/favorites              # Save a restaurant/event/business
DELETE /auth/favorites/{id}       # Unsave
```

#### Submissions

```bash
POST /submissions/restaurant      # Submit new restaurant
POST /submissions/event           # Submit new event
POST /submissions/business        # Submit new business

Request body:
{
  "name": "Restaurant Name",
  "location": {...},
  "halal_status": "zabiha",
  "cuisine_type": ["Pakistani"],
  ...
}

Response: {status: "pending_review", submission_id: "..."}
```

#### Claims

```bash
POST /claims/restaurant/{id}      # Claim ownership of restaurant
POST /claims/business/{id}        # Claim ownership of business
POST /claims/masjid/{id}          # Claim masjid

GET /claims/my-claims             # View user's pending claims
PATCH /claims/{claim_id}          # Update claimed business
```

### Admin Endpoints

```bash
# Moderate submissions
GET /admin/submissions?status=pending
PATCH /admin/submissions/{id}/approve
PATCH /admin/submissions/{id}/reject
  ?reason="Insufficient data"

# Feature content
PATCH /admin/events/{id}/feature   # Add to homepage
PATCH /admin/events/{id}/unfeature

# Manage scraped data
GET /admin/scraping-logs
POST /admin/trigger-scrape/{source}  # Run specific scraper manually

# User management
PATCH /admin/users/{id}/verify
PATCH /admin/users/{id}/ban

# Analytics (future)
GET /admin/analytics/scraped-items
GET /admin/analytics/user-submissions
```

---

## 👥 User Roles & Permissions

### Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **User** | General app user | View all public data, save favorites, submit listings, RSVP events |
| **Business Owner** | Claims restaurant/business | View own listings, update details, get analytics (future) |
| **Event Organizer** | Creates/manages events | Create events, edit own events, see RSVPs |
| **Masjid Rep** | Updates masjid info | Update prayer times, post announcements, manage events |
| **Admin** | Full platform control | Approve submissions, moderate content, manage users, trigger scrapers |

### Permission Matrix

```python
# api/deps.py
PERMISSIONS = {
    "user": [
        "view_public_data",
        "save_favorites",
        "submit_listing",
        "rsvp_event",
    ],
    "business_owner": [
        "submit_listing",
        "claim_business",
        "edit_own_business",
        "update_hours",
    ],
    "event_organizer": [
        "create_event",
        "edit_own_event",
        "delete_own_event",
    ],
    "masjid_rep": [
        "update_prayer_times",
        "post_announcement",
        "manage_masjid_events",
    ],
    "admin": [
        "approve_submissions",
        "reject_submissions",
        "feature_content",
        "ban_users",
        "trigger_scrapers",
        "view_analytics",
    ],
}

async def require_permission(required: str):
    """Dependency for protecting endpoints"""
    async def check(user: User = Depends(get_current_user)):
        if required not in PERMISSIONS.get(user.role, []):
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return check
```

---

## 🛡️ Moderation & Admin Workflows

### Submission Lifecycle

```
User/Scraper
    ↓
Submits Data (Restaurant, Event, Business)
    ↓
Data Validation (Schema check)
    ↓
Deduplication Check (Is this a duplicate?)
    ↓
    ├─ NEW ITEM → Moderation Queue (Status: pending)
    │             Admin review
    │             ├─ Approve → Published
    │             ├─ Reject  → Notification to user
    │             └─ Flag    → Needs revision
    │
    └─ DUPLICATE/UPDATE → Update existing item
                         If significant changes → Moderation queue
```

### Admin Notification Flow

```python
# notifications/email.py
class AdminNotifier:
    async def notify_new_submission(self, submission: Submission):
        """Alert admins of pending submissions"""
        admins = await db.query(User).filter(User.role == "admin").all()
        
        for admin in admins:
            await send_email(
                to=admin.email,
                subject="New Submission Pending Review",
                template="submission_review",
                data={
                    "submission_id": submission.id,
                    "entity_type": submission.entity_type,
                    "submitted_by": submission.submitted_by,
                    "review_url": f"https://admin.dmvmuslims.com/submissions/{submission.id}"
                }
            )
    
    async def notify_claim_received(self, claim_id: str, business_name: str):
        """Alert admins of new business claims"""
        admins = await db.query(User).filter(User.role == "admin").all()
        for admin in admins:
            await send_email(
                to=admin.email,
                subject=f"Business Claim: {business_name}",
                template="claim_received",
                data={"claim_id": claim_id, "business_name": business_name}
            )
    
    async def notify_submission_result(self, user_email: str, status: str, reason: str = None):
        """Notify user of submission approval/rejection"""
        template = "submission_approved" if status == "approved" else "submission_rejected"
        await send_email(
            to=user_email,
            subject=f"Submission {status.capitalize()}",
            template=template,
            data={"reason": reason}
        )
```

### Flagging & Review System

```python
# api/routes/admin.py
@router.post("/admin/submissions/{submission_id}/flag")
async def flag_submission(
    submission_id: str,
    reason: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_permission("view_analytics"))
):
    """Flag submission for manual review"""
    submission = await db.get(Submission, submission_id)
    submission.status = "flagged"
    submission.rejection_reason = reason
    await db.commit()
    
    # Notify admins
    await AdminNotifier().notify_flagged_submission(submission)
    
    return {"status": "flagged", "reason": reason}
```

---

## 🗄️ Database Schema

### Core Tables

**Users**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  supabase_id UUID UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'user',
  auth_provider VARCHAR(50),
  is_verified BOOLEAN DEFAULT FALSE,
  profile_picture_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Restaurants**
```sql
CREATE TABLE restaurants (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  halal_status VARCHAR(50),  -- halal, zabiha, unverified
  serves_alcohol BOOLEAN,
  serves_pork BOOLEAN,
  cuisine_types TEXT[],  -- {"Pakistani", "Arab"}
  price_range VARCHAR(10),  -- $, $, $$, $$
  rating FLOAT,
  data_completeness FLOAT,
  is_verified BOOLEAN DEFAULT FALSE,
  
  -- Contact
  phone VARCHAR(20),
  website VARCHAR(255),
  menu_url VARCHAR(255),
  
  -- Location
  address VARCHAR(255),
  city VARCHAR(100),
  state VARCHAR(2),
  lat FLOAT,
  lng FLOAT,
  
  -- Media
  image_urls TEXT[],
  
  -- Tracking
  sources TEXT[],  -- {"google_maps", "instagram"}
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  scraped_at TIMESTAMP
);

CREATE INDEX idx_restaurants_location ON restaurants USING GIST(ll_to_earth(lat, lng));
CREATE INDEX idx_restaurants_cuisine ON restaurants USING GIN(cuisine_types);
```

**Events**
```sql
CREATE TABLE events (
  id UUID PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  event_type VARCHAR(50),  -- iftaar, halaqah, eid, etc.
  date DATE NOT NULL,
  time TIME,
  end_time TIME,
  
  -- Location
  address VARCHAR(255),
  city VARCHAR(100),
  lat FLOAT,
  lng FLOAT,
  masjid_id UUID REFERENCES masjids(id),
  
  -- Organization
  organizer_id UUID NOT NULL REFERENCES users(id),
  organizer_name VARCHAR(255),
  contact_email VARCHAR(255),
  speaker VARCHAR(255),
  audience VARCHAR(100),
  
  -- RSVP
  rsvp_link VARCHAR(255),
  website VARCHAR(255),
  
  -- Admin
  is_featured BOOLEAN DEFAULT FALSE,
  featured_at TIMESTAMP,
  is_approved BOOLEAN DEFAULT FALSE,
  
  -- Recurring
  recurrence_rule TEXT,  -- iCal RRULE format
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_events_masjid ON events(masjid_id);
```

**Masjids**
```sql
CREATE TABLE masjids (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Location
  address VARCHAR(255),
  city VARCHAR(100),
  state VARCHAR(2),
  lat FLOAT,
  lng FLOAT,
  
  -- Contact
  phone VARCHAR(20),
  website VARCHAR(255),
  email VARCHAR(255),
  donation_link VARCHAR(255),
  
  -- Prayer times
  fajr TIME,
  dhuhr TIME,
  asr TIME,
  maghrib TIME,
  isha TIME,
  prayer_times_source VARCHAR(255),
  prayer_time_selectors JSONB,  -- CSS selectors for scraping
  prayer_times_updated_at TIMESTAMP,
  
  -- Media
  image_urls TEXT[],
  
  -- Admin
  is_verified BOOLEAN DEFAULT FALSE,
  is_claimed BOOLEAN DEFAULT FALSE,
  claimer_id UUID REFERENCES users(id),
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Submissions**
```sql
CREATE TABLE submissions (
  id UUID PRIMARY KEY,
  entity_type VARCHAR(50),  -- restaurant, event, business, masjid
  submission_type VARCHAR(50),  -- new, update, claim
  entity_data JSONB,  -- Partial or complete data
  
  -- User info
  submitted_by UUID NOT NULL REFERENCES users(id),
  
  -- Status
  status VARCHAR(50) DEFAULT 'pending',  -- pending, approved, rejected, flagged
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMP,
  rejection_reason TEXT,
  
  -- Source
  data_source VARCHAR(50),  -- user, admin, scraper
  source_details JSONB,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_submissions_status ON submissions(status);
CREATE INDEX idx_submissions_submitted_by ON submissions(submitted_by);
```

**User Favorites**
```sql
CREATE TABLE favorites (
  user_id UUID REFERENCES users(id),
  entity_type VARCHAR(50),  -- restaurant, event, business
  entity_id UUID NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, entity_type, entity_id)
);
```

**Curated Pages** (Instagram/TikTok pages to scrape)
```sql
CREATE TABLE curated_pages (
  id UUID PRIMARY KEY,
  source VARCHAR(50),  -- instagram, tiktok
  username VARCHAR(255),
  page_type VARCHAR(50),  -- restaurant, event, general
  is_active BOOLEAN DEFAULT TRUE,
  last_scraped TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Scraping Logs**
```sql
CREATE TABLE scraping_logs (
  id UUID PRIMARY KEY,
  agent_name VARCHAR(100),
  source VARCHAR(50),
  status VARCHAR(50),  -- success, failed, partial
  items_scraped INTEGER,
  items_saved INTEGER,
  error_message TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);

CREATE INDEX idx_scraping_logs_date ON scraping_logs(completed_at);
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=agents --cov=core --cov=api --cov=tasks

# Specific test file
pytest tests/test_schema.py -v

# Specific test function
pytest tests/test_agents/test_google_maps_agent.py::test_scrape_restaurants -v
```

### Test Structure

```
tests/
├── conftest.py                  # Shared fixtures
├── test_schema.py               # Pydantic models
├── test_normalizer.py           # Data normalization
├── test_deduplicator.py         # Duplicate detection
├── test_agents/
│   ├── test_google_maps_agent.py
│   ├── test_instagram_agent.py
│   ├── test_masjid_site_agent.py
│   └── test_base_agent.py
├── test_api/
│   ├── test_restaurants.py
│   ├── test_events.py
│   ├── test_masjids.py
│   ├── test_auth.py
│   └── test_admin.py
└── test_tasks/
    └── test_orchestrator.py
```

### Example Test

```python
# tests/test_agents/test_google_maps_agent.py
import pytest
from agents.google_maps_agent import GoogleMapsAgent

@pytest.mark.asyncio
async def test_google_maps_scrape_restaurants():
    """Test scraping restaurants from Google Maps"""
    agent = GoogleMapsAgent("dmv")
    results = await agent.collect()
    
    assert len(results) > 0
    assert results[0]["name"] is not None
    assert results[0]["location"] is not None
    assert "halal_status" in results[0]
```

---

## 🚀 Deployment

### Docker Build

```bash
# Build image
docker build -t dmv-muslims-backend:latest .

# Run locally
docker run -p 8000:8000 \
  --env-file .env \
  dmv-muslims-backend:latest
```

### Cloud Deployment Options

#### Option 1: DigitalOcean (Recommended for cost)

**Setup:**
- **App**: $5-12/month (App Platform)
- **Database**: $15/month (Managed PostgreSQL)
- **Redis**: $7/month (Managed Redis)
- **Total**: ~$25-35/month

```bash
# Deploy using doctl CLI
doctl apps create --spec app.yaml

# Or push to Docker Hub and deploy via UI
docker push your-docker-hub/dmv-muslims-backend:latest
```

#### Option 2: AWS (More scalable)

- **API**: AWS Lambda + API Gateway (pay per request)
- **Database**: AWS RDS (PostgreSQL) $20-50/month
- **Cache**: ElastiCache (Redis) $15-30/month
- **Background Jobs**: SQS + Lambda or EC2 for Celery

#### Option 3: Google Cloud

- **API**: Cloud Run (containers, serverless)
- **Database**: Cloud SQL (PostgreSQL)
- **Cache**: Memorystore (Redis)
- **Jobs**: Cloud Tasks or Cloud Pub/Sub

### Environment Setup for Production

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env for production
ENV=production
DEBUG=False
SECRET_KEY=<generated-key>
DATABASE_URL=<prod-db-url>
REDIS_URL=<prod-redis-url>

# CORS for frontend domain
FRONTEND_URL=https://app.dmvmuslims.com
```

---

## 💻 Development

### Adding a New Agent

1. **Create agent file** (`agents/new_source_agent.py`):

```python
from agents.base_agent import BaseAgent

class NewSourceAgent(BaseAgent):
    def __init__(self, region: str):
        self.region = region
        self.source_type = "new_source"
    
    async def collect(self) -> List[dict]:
        """Fetch and return standardized data"""
        data = []
        
        # Implement scraping logic here
        
        return data
```

2. **Register in orchestrator** (`tasks/orchestrator.py`):

```python
from agents.new_source_agent import NewSourceAgent

async def run_all_agents(self, region: str):
    agents = [
        GoogleMapsAgent(region),
        InstagramAgent(region),
        MasjidSiteAgent(region),
        NewSourceAgent(region),  # Add here
    ]
    # ... rest of orchestration
```

3. **Add tests** (`tests/test_agents/test_new_source_agent.py`)

### Adding an API Endpoint

1. **Create route file** (`api/routes/new_endpoint.py`):

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_user

router = APIRouter(prefix="/api/new", tags=["new"])

@router.get("/")
async def list_items(db: AsyncSession = Depends(get_db)):
    """List items"""
    items = await db.query(Item).all()
    return items

@router.post("/")
async def create_item(
    item: ItemSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new item"""
    new_item = Item(**item.dict())
    db.add(new_item)
    await db.commit()
    return new_item
```

2. **Register in main** (`main.py`):

```python
from api.routes import new_endpoint
app.include_router(new_endpoint.router)
```

### Local Database Backup

```bash
# Backup
pg_dump -U user dmv_muslims > backup.sql

# Restore
psql -U user dmv_muslims < backup.sql
```

### Running Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📈 Roadmap

### Phase 1 (MVP - Now)
- ✅ Halal restaurant directory (filterable)
- ✅ Event calendar
- ✅ Masjid listings with prayer times
- ✅ User authentication (Supabase)
- ✅ Admin moderation panel
- ✅ Google Maps + Instagram scraping
- ✅ User submissions

### Phase 2 (Q2 2025)
- Push notifications for saved events
- Weekly newsletter
- Featured listings & ads
- TikTok scraping
- Business analytics dashboard
- Email verification workflow

### Phase 3 (Q3 2025)
- Expand to 5+ major US cities
- Mobile app (React Native)
- AI-powered event discovery
- Community reviews (eventually)
- Donation system integration

### Phase 4 (Q4 2025+)
- International expansion (Canada, UK)
- Browser extension for Google Maps
- Machine learning for restaurant categorization
- Advanced search & recommendations

---

## 🔐 Security

- All API keys stored in environment variables (never committed)
- HTTPS enforced in production
- JWT tokens from Supabase Auth
- Rate limiting on public endpoints
- SQL injection prevention via SQLAlchemy ORM
- CORS configured for frontend domain only
- Admin endpoints require role-based access

---

## 🆘 Troubleshooting

### Celery tasks not running

```bash
# Check Redis is running
redis-cli ping  # Should return "PONG"

# Check Celery worker
celery -A tasks.celery_app worker --loglevel=debug

# Check Beat scheduler
celery -A tasks.celery_app beat --loglevel=debug
```

### Database connection issues

```bash
# Test connection
psql postgresql://user:password@localhost:5432/dmv_muslims

# Check async driver
python -c "import asyncpg; print('asyncpg OK')"
```

### Scraper failures

Check logs in `scraping_logs` table:

```python
from db.queries import get_scraping_logs
logs = await get_scraping_logs(limit=10)
for log in logs:
    print(f"{log.agent_name}: {log.status} - {log.error_message}")
```

---

## 📝 License

[Add your license here]

---

## 🙏 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes and add tests
4. Open a pull request

---

## 📞 Support

- **Issues**: GitHub Issues
- **Email**: [your-email@example.com]
- **Discord**: [Community server]

---

**Built with ❤️ for the Muslim community in the DMV and beyond.**
        