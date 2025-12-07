# Satellite Pass Tracker (Django + N2YO)

A Django-based web application that tracks satellite pass predictions for selected locations using **N2YO data**.  
The project supports **scraping**, **API-based prediction**, and database-backed viewing of satellite passes.

---

## Features

- Add & manage **Locations** (latitude, longitude, altitude)
- Add & manage **Satellites** (NORAD ID-based)
- Scrape satellite pass data from **N2YO website**
- Predict upcoming satellite passes (10 days)
- Store pass predictions in database
- View pass list ordered by time
- Django Admin support
- Modular Django architecture
- IOMMI-powered UI pages

---

## Tech Stack

- **Backend:** Django 5.x
- **Database:** SQLite (default)
- **API / Data Source:**
  - N2YO API (limited/free)
  - N2YO website scraping (fallback)
- **Frontend:** IOMMI (server-rendered UI)
- **Language:** Python 3.12+

---
