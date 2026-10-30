# Mounjaro UK Price Tracker

## Overview
Automated daily scraping of **non-discounted** Mounjaro retail prices from 65+ UK GPhC-registered pharmacies. Data is stored as structured JSON and ready to embed on any website with price fluctuation graphs.

**Source:** https://monj.co.uk/mounjaro-price-list-non-discounted-uk/

---

## File Structure

```
/mounjaro-prices/
├── README.md              ← This file
├── price-history.json     ← Master file: latest prices + full pharmacy details
├── daily-snapshots/       ← One JSON file per day (YYYY-MM-DD.json)
│   └── 2026-05-24.json
├── scraper.py             ← Python scraper script (reference)
├── widget.js              ← Embeddable JavaScript widget
└── demo.html              ← Demo page for the widget
```

---

## Data Format

### price-history.json (Master File)
```json
{
  "meta": {
    "source": "https://monj.co.uk/mounjaro-price-list-non-discounted-uk/",
    "dosages": ["2.5mg", "5mg", "7.5mg", "10mg", "12.5mg", "15mg"],
    "last_scraped": "2026-05-24T03:45:00+04:00",
    "total_pharmacies": 64
  },
  "pharmacies": [
    {
      "name": "Pharmacy Name",
      "url": "https://...",
      "prices": { "2.5mg": 130.00, "5mg": 165.00, ... },
      "trustpilot": 4.5,
      "gphc": "1116105",
      "subscription": false,
      "discounts": "£40 Off 1st Orders"
    }
  ]
}
```

### daily-snapshots/YYYY-MM-DD.json
Same structure as price-history.json but with a `date` and `scraped_at` field. Each day adds a new file, creating a full time series for price fluctuation tracking.

---

## Embedding on Another Website

### Option 1: Widget.js (Self-contained)
```html
<!-- Add to your page -->
<div id="mounjaro-widget"></div>
<script src="/path-to/widget.js"></script>
```
Update the `DATA_BASE` variable in widget.js to point to your hosted JSON files.

### Option 2: Direct JSON API
Host the JSON files on your server and fetch them with your own frontend:

```javascript
// Fetch latest prices
const response = await fetch('/mounjaro-prices/price-history.json');
const data = await response.json();

// Fetch snapshots for trend graphs
const dates = ['2026-05-24', '2026-05-23', ...]; // last 30 days
const snapshots = await Promise.all(
  dates.map(d => fetch(`/mounjaro-prices/daily-snapshots/${d}.json`).then(r => r.json()).catch(() => null))
);
```

### Option 3: Chart.js / Recharts Integration
```javascript
// Build trend data from snapshots
const trendData = snapshots.filter(Boolean).map(snap => ({
  date: snap.date,
  min_2_5mg: Math.min(...snap.pharmacies.map(p => p.prices['2.5mg']).filter(Boolean)),
  avg_2_5mg: snap.pharmacies.map(p => p.prices['2.5mg']).filter(Boolean).reduce((s,v) => s+v, 0) / snap.pharmacies.length,
  // ... repeat for other dosages
}));
```

---

## Scheduled Task

- **Name:** Mounjaro Price Scraper
- **Schedule:** Daily at 6:00 AM (Asia/Dubai timezone)
- **Task ID:** 82898a1e-5638-4787-9fa1-181d31542616
- **What it does:**
  1. Fetches the Monj.co.uk price page
  2. Parses the WordPress table (column-1 through column-11)
  3. Saves a daily snapshot to `/mounjaro-prices/daily-snapshots/YYYY-MM-DD.json`
  4. Updates the master `/mounjaro-prices/price-history.json`
  5. Reports summary stats

---

## Price Summary (as of 2026-05-24)

| Dosage | Min     | Average | Max     | Cheapest Pharmacy |
|--------|---------|---------|---------|-------------------|
| 2.5mg  | £130.00 | £166.21 | £239.00 | Slimming Direct   |
| 5mg    | £153.00 | £189.01 | £259.00 | Jood Life         |
| 7.5mg  | £204.99 | £244.66 | £304.00 | Next Script       |
| 10mg   | £229.00 | £272.05 | £329.00 | Medicine Marketplace |
| 12.5mg | £246.00 | £290.22 | £349.00 | Next Script       |
| 15mg   | £266.00 | £308.12 | £369.00 | Medicine Marketplace |
