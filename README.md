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

## 🗺️ Implementation Steps

1. **Build the Scraper Script:** Write a Python script using Telethon to authenticate as a user and listen to new messages in 2-3 target Telegram groups.
2. **Integrate the AI Parser:** Write a prompt that takes a raw message and outputs a JSON object (Venue, Date, StartTime, EndTime, Price). Test edge cases (e.g., "tmr", "next wed").
3. **Set up the Database:** Create PostgreSQL tables for `Users`, `AlertPreferences`, and `ParsedListings`.
4. **Develop the Matching Engine:** Write the logic that triggers whenever a new `ParsedListing` enters the database, checking it against all active `AlertPreferences`.
5. **Build the Notification Delivery:** Connect the matching engine to a Telegram Bot API to send the final matched alert to the user.
6. **Develop the User Interface:** Build the React/Flutter frontend for users to register, log in, and easily create their alert parameters.