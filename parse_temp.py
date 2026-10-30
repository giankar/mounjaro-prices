import re, json, statistics
from datetime import datetime, timezone, timedelta

# Dubai timezone (UTC+4)
dubai = timezone(timedelta(hours=4))
today = datetime.now(dubai).strftime("%Y-%m-%d")
now_iso = datetime.now(dubai).isoformat()

# We'll read the page from the file we'll create
page = open("/home/user/page.md", "r").read()

# Parse table rows - find markdown table rows (start with |[)
rows = []
lines = page.split("\n")
for line in lines:
    line = line.strip()
    if line.startswith("|[") and "|" in line:
        rows.append(line)

print(f"Found {len(rows)} pharmacy rows")

pharmacies = []
for row in rows:
    # Split by | and trim
    cols = [c.strip() for c in row.split("|")]
    # Remove first/last empty
    cols = cols[1:-1]
    if len(cols) < 11:
        continue

    # col 0: Pharmacy name + URL
    name_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', cols[0])
    if not name_match:
        continue
    pharmacy_name = name_match.group(1)
    pharmacy_url = name_match.group(2)

    # cols 1-6: prices
    prices = {}
    dosages = ["2.5mg", "5mg", "7.5mg", "10mg", "12.5mg", "15mg"]
    for i, dosage in enumerate(dosages):
        price_match = re.search(r'£\s*([\d.]+)', cols[1+i])
        if price_match:
            prices[dosage] = float(price_match.group(1))

    # col 7: Trustpilot
    tp_match = re.search(r'\[([\d.]+)\]', cols[7])
    trustpilot = float(tp_match.group(1)) if tp_match else None

    # col 8: GPhC
    gphc_match = re.search(r'\[(\d+)\]', cols[8])
    gphc = gphc_match.group(1) if gphc_match else ""

    # col 9: Additional support (A/S) - not needed per task

    # col 10: Subscription
    subscription = "SUB" in cols[9].upper() if cols[9] else False

    # col 11: Discounts
    discount_match = re.search(r'\[([^\]]*)\]\s*\(', cols[10])
    discounts = discount_match.group(1) if discount_match else "—"

    pharmacies.append({
        "pharmacy_name": pharmacy_name,
        "pharmacy_url": pharmacy_url,
        "prices": prices,
        "trustpilot": trustpilot,
        "gphc": gphc,
        "subscription": subscription,
        "discounts": discounts
    })

print(f"Parsed {len(pharmacies)} pharmacies")

# Compute stats per dosage
dosages = ["2.5mg", "5mg", "7.5mg", "10mg", "12.5mg", "15mg"]
stats = {}
for d in dosages:
    vals = [p["prices"][d] for p in pharmacies if d in p["prices"]]
    stats[f"{d}_min"] = min(vals)
    stats[f"{d}_max"] = max(vals)
    stats[f"{d}_avg"] = round(statistics.mean(vals), 2)

print("Stats:", json.dumps(stats, indent=2))

# 1. Daily snapshot
snapshot = {
    "date": today,
    "scraped_at": now_iso,
    "total_pharmacies": len(pharmacies),
    "pharmacies": pharmacies
}

# 2. Price history
price_history = {
    "meta": {
        "source": "https://monj.co.uk/mounjaro-price-list-non-discounted-uk/",
        "last_scraped": now_iso,
        "total_pharmacies": len(pharmacies)
    },
    "pharmacies": pharmacies
}

# 3. Time series entry
ts_entry = {
    "date": today,
    **stats
}

# Write output files
os.makedirs("/home/user/output", exist_ok=True)

with open("/home/user/output/snapshot.json", "w") as f:
    json.dump(snapshot, f, indent=2)

with open("/home/user/output/price_history.json", "w") as f:
    json.dump(price_history, f, indent=2)

with open("/home/user/output/ts_entry.json", "w") as f:
    json.dump(ts_entry, f, indent=2)

print(f"\nSnapshot: /mounjaro-prices/daily-snapshots/{today}.json")
print(f"Pharmacies: {len(pharmacies)}")
for d in dosages:
    print(f"  {d}: min=£{stats[f'{d}_min']:.2f} avg=£{stats[f'{d}_avg']:.2f} max=£{stats[f'{d}_max']:.2f}")
PYEOF
