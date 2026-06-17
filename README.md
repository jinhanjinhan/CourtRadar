# CourtRadar 🏸

CourtRadar is an intelligent aggregator and notification engine for the secondary badminton court market. It monitors fragmented community channels, standardizes unstructured let-go listings using AI, and dispatches real-time alerts to users based on their precise scheduling constraints.

## 🎯 The Problem
The secondary market for court bookings is highly inefficient. 
1. **Fragmentation:** Listings are scattered across dozens of Telegram groups, Facebook pages, and Carousell.
2. **High Latency:** Slots are claimed within seconds. Manual monitoring is impossible.
3. **Unstructured Data:** Sellers use varying formats ("wts ocbc arena tmr 8-10"), making automated filtering difficult.
4. **Lack of Trust (Adverse Selection):** Scams are prevalent, and buyers have no way to verify the authenticity of a court before transferring money.

## 💡 The Solution
CourtRadar bridges the gap between buyers and sellers through a three-phase pipeline:
1. **Ingestion:** Continuous monitoring of public listing channels.
2. **Normalization:** Passing raw, unstructured messages through an LLM to extract structured data (Date, Time, Venue, Price, Seller ID).
3. **Distribution:** A Pub/Sub architecture that instantly matches structured slots against user-defined queries and dispatches push notifications.

## 🚀 Features

### Phase 1: The Aggregator MVP (Current Focus)
* **Telegram Integration:** Automated scraping of major SG Badminton Telegram groups.
* **AI Parser:** Standardizes messages into strict JSON payloads.
* **Alert Rules Engine:** Users can define filters based on Date, Time Range, and Venue.
* **Notification System:** Real-time alerts sent via Telegram Bot or Push Notification.

### Phase 2: Premium Tiers & Action Automation
* **Granular Filtering:** Geofencing (e.g., "Courts within 5km of Clementi") and price-cap filters.
* **Priority Routing:** Millisecond-level priority alerts for premium subscribers.
* **Auto-Claiming:** 1-click auto-generation of messages sent directly to the seller's DMs.

### Phase 3: The Verified Exchange (Future State)
* **In-App Marketplace:** Transitioning from an aggregator to a centralized exchange.
* **Automated Verification:** OCR processing of booking receipts to prove authenticity before a listing goes live.
* **Escrow System:** Holding buyer funds securely until the session is completed to eliminate scam risk.

## 🛠️ Technical Stack
* **Scraper & AI Microservice:** Python, FastAPI, Telethon
* **LLM Engine:** Google Gemini API (Structured Outputs)
* **Core API & Logic:** TypeScript, Node.js
* **Database & Caching:** PostgreSQL (Relational Data), Redis (Pub/Sub & Rate Limiting)
* **Frontend Application:** React (Web), Flutter (Mobile iOS/Android)

## 🧱 Current Backend Starter
The Python backend now gives you the first working slice of the system:

* `app/main.py` creates the FastAPI app and mounts the API router.
* `app/api.py` exposes starter endpoints for health, users, alert preferences, parsed listings, and listing matches.
* `app/db/models.py` defines the current SQLAlchemy models for `users`, `alert_preferences`, and `parsed_listings`.
* `app/services/matching/engine.py` contains the first matching rule function that compares a parsed listing against an alert preference.

This is intentionally the smallest useful backend foundation. It is not the full product yet; it is the base you can extend into ingestion, parsing, notification dispatch, and proper persistence.

## 🗂️ Repository Layout
* `app/modules` - HTTP routes, repositories, services, and module-local schemas.
* `app/core` - app configuration and environment settings.
* `app/db` - SQLAlchemy base, models, and async session helpers.
* `app/schemas` - Pydantic request and response schemas.
* `app/services` - shared business logic split by concern.
* `tests` - smoke tests and future unit/integration tests.

## ▶️ How To Start The Backend
The project uses a plain virtualenv, so startup should stay simple.

1. Create the virtual environment if it does not exist yet:
	`python3 -m venv .venv`
2. Activate it:
	`source .venv/bin/activate`
3. Install dependencies:
	`pip install -r requirements.txt`
4. Install the project so the `courtradar` package is importable:
  `pip install .`
5. Run the app in development mode from the `src` directory:
  `python -m uvicorn app.main:app --reload`

If you do not want to install the package, the repo root already works because `app/` is now at the top level.

## 🗃️ Manual Table Creation

If you want to create the PostgreSQL tables once, without enabling startup creation, run:

```bash
./.venv/bin/python scripts/create_tables.py
```

This uses the SQLAlchemy metadata from the current models and creates `users`, `alert_preferences`, and `parsed_listings` in the configured database.

## 🧪 How To Test
The current smoke test only checks that the app boots and the health endpoint responds.

```bash
./.venv/bin/python -m pytest tests/test_health.py
```

You can also run the whole test suite later with:

```bash
./.venv/bin/python -m pytest
```

## 🔌 How To Use The Starter API
The backend currently exposes these starter endpoints:

* `GET /health` - liveness check.
* `POST /users` - create a starter user record.
* `GET /users/{user_id}` - fetch a user.
* `POST /alert-preferences` - create a matching rule for a user.
* `GET /alert-preferences` - list saved alert rules.
* `POST /parsed-listings` - store a parsed court listing.
* `GET /parsed-listings` - list parsed listings.
* `GET /parsed-listings/{listing_id}/matches` - show which alerts match a listing.

Example user creation request:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","display_name":"Alex"}'
```

Example alert preference request:

```bash
curl -X POST http://127.0.0.1:8000/alert-preferences \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"venue":"OCBC Arena","earliest_time":"19:00:00","latest_time":"22:00:00","max_price":20}'
```

Example listing request:

```bash
curl -X POST http://127.0.0.1:8000/parsed-listings \
  -H "Content-Type: application/json" \
  -d '{"source_channel":"telegram","raw_text":"wts ocbc arena tmr 8-10","venue":"OCBC Arena","listing_date":"2026-06-14","start_time":"20:00:00","end_time":"22:00:00","price":18}'
```

## 🧠 What Happens In The Backend
The current flow is:

1. A listing gets stored in `parsed_listings`.
2. A saved alert preference is compared against that listing.
3. `listing_matches_alert` applies venue, price, and time filters.
4. The match endpoint returns the alert IDs that would receive a notification.

That means the backend already has the foundation for the real production pipeline, even though the Telegram ingestion and Gemini parsing are still placeholders.

## ⚙️ Environment Variables
Copy [.env.example](.env.example) to `.env` when you start wiring real services.

* `DATABASE_URL` - PostgreSQL connection string. This is required.
* `REDIS_URL` - Redis connection string.
* `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_BOT_TOKEN` - Telegram integrations.
* `GEMINI_API_KEY` - Gemini parser access.

Most of the service-specific secrets are optional for local startup, but `DATABASE_URL` is required because the app needs a database connection.

## 🗺️ Implementation Steps

1. **Build the Scraper Script:** Write a Python script using Telethon to authenticate as a user and listen to new messages in 2-3 target Telegram groups.
2. **Integrate the AI Parser:** Write a prompt that takes a raw message and outputs a JSON object (Venue, Date, StartTime, EndTime, Price). Test edge cases (e.g., "tmr", "next wed").
3. **Set up the Database:** Create PostgreSQL tables for `Users`, `AlertPreferences`, and `ParsedListings`.
4. **Develop the Matching Engine:** Write the logic that triggers whenever a new `ParsedListing` enters the database, checking it against all active `AlertPreferences`.
5. **Build the Notification Delivery:** Connect the matching engine to a Telegram Bot API to send the final matched alert to the user.
6. **Develop the User Interface:** Build the React/Flutter frontend for users to register, log in, and easily create their alert parameters.