# Mounjaro UK Price Tracker

Daily non-discounted Mounjaro retail prices from 65+ UK pharmacies.

**Source:** [Monj.co.uk](https://monj.co.uk/mounjaro-price-list-non-discounted-uk/)  
**Updated:** Daily at 6am Dubai time  
**Total pharmacies:** 64

## JSON Feeds

| Feed | URL | Description |
|------|-----|-------------|
| **price-history.json** | [raw](https://raw.githubusercontent.com/giankar/mounjaro-prices/main/price-history.json) | Latest full dataset with all 64 pharmacies |
| **time-series.json** | [raw](https://raw.githubusercontent.com/giankar/mounjaro-prices/main/time-series.json) | Min/avg/max per dosage per day |
| **daily-snapshots/** | [browse](https://github.com/giankar/mounjaro-prices/tree/main/daily-snapshots) | Full daily archives (one file per day) |

## Quick Start

\`\`\`javascript
// Fetch latest prices
const res = await fetch('https://raw.githubusercontent.com/giankar/mounjaro-prices/main/price-history.json');
const data = await res.json();
console.log(data.pharmacies[0]); // { name: "Asda", prices: {...} }
\`\`\`

## Data Structure

### price-history.json
\`\`\`json
{
  "meta": { "source": "...", "last_scraped": "2026-05-24T...", "total_pharmacies": 64 },
  "pharmacies": [{
    "name": "Pharmacy Name",
    "url": "https://...",
    "prices": { "2.5mg": 172.47, "5mg": 192.47, ... },
    "trustpilot": 4.5,
    "gphc": "1116105",
    "subscription": false,
    "discounts": "Description"
  }]
}
\`\`\`

### time-series.json
\`\`\`json
[{
  "date": "2026-05-24",
  "2.5mg_min": 130.00, "2.5mg_avg": 166.21, "2.5mg_max": 239.00,
  "5mg_min": 153.00, "5mg_avg": 189.01, "5mg_max": 259.00,
  ...
}]
\`\`\`