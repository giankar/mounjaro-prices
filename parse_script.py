import re, json, statistics, os, sys
from datetime import datetime, timezone, timedelta

dubai = timezone(timedelta(hours=4))
today = datetime.now(dubai).strftime("%Y-%m-%d")
now_iso = datetime.now(dubai).isoformat()

# Read page content from file
with open("/home/user/page_full.md", "r") as f:
    page = f.read()

# Find all table rows
rows = []
for line in page.split("\n"):
    line = line.strip()
    if re.match(r'^\|\[[^\]]+\]\(https?://', line):
        rows.append(line)

print(f"Found {len(rows)} pharmacy rows in page", file=sys.stderr)

pharmacies = []
for row in rows:
    cols = [c.strip() for c in row.split("|")]
    cols = [c for c in cols if c]
    if len(cols) < 11:
        continue

    name_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', cols[0])
    if not name_match:
        continue
    pharmacy_name = name_match.group(1)
    pharmacy_url = name_match.group(2)

    dosages = ["2.5mg", "5mg", "7.5mg", "10mg", "12.5mg", "15mg"]
    prices = {}
    for i, dosage in enumerate(dosages):
        pm = re.search(r'£\s*([\d.]+)', cols[1+i])
        if pm:
            prices[dosage] = float(pm.group(1))

    tp_match = re.search(r'\[([\d.]+)\]', cols[7])
    trustpilot = float(tp_match.group(1)) if tp_match else None

    gphc_match = re.search(r'\[(\d+)\]', cols[8])
    gphc = gphc_match.group(1) if gphc_match else ""

    subscription = bool(re.search(r'\bYes\b', cols[9])) if cols[9] else False

    disc_match = re.search(r'\[([^\]]*)\]\(', cols[10])
    discounts = disc_match.group(1) if disc_match else "—"

    pharmacies.append({
        "pharmacy_name": pharmacy_name,
        "pharmacy_url": pharmacy_url,
        "prices": prices,
        "trustpilot": trustpilot,
        "gphc": gphc,
        "subscription": subscription,
        "discounts": discounts
    })

print(f"Parsed {len(pharmacies)} pharmacies", file=sys.stderr)

dosages = ["2.5mg", "5mg", "7.5mg", "10mg", "12.5mg", "15mg"]
stats = {}
for d in dosages:
    vals = [p["prices"][d] for p in pharmacies if d in p["prices"]]
    stats[f"{d}_min"] = min(vals)
    stats[f"{d}_max"] = max(vals)
    stats[f"{d}_avg"] = round(statistics.mean(vals), 2)

os.makedirs("/home/user/output", exist_ok=True)

snapshot = {
    "date": today,
    "scraped_at": now_iso,
    "total_pharmacies": len(pharmacies),
    "pharmacies": pharmacies
}

price_history = {
    "meta": {
        "source": "https://monj.co.uk/mounjaro-price-list-non-discounted-uk/",
        "last_scraped": now_iso,
        "total_pharmacies": len(pharmacies)
    },
    "pharmacies": pharmacies
}

ts_entry = {"date": today, **stats}

with open("/home/user/output/snapshot.json", "w") as f:
    json.dump(snapshot, f, indent=2)
with open("/home/user/output/price_history.json", "w") as f:
    json.dump(price_history, f, indent=2)
with open("/home/user/output/ts_entry.json", "w") as f:
    json.dump(ts_entry, f, indent=2)

# Compare with old
with open("/home/user/old_price_history.json") as f:
    old_data = json.load(f)
old_pharm = {p["pharmacy_name"]: p["prices"] for p in old_data["pharmacies"]}

changes = []
new_pharmacies = []
for p in pharmacies:
    name = p["pharmacy_name"]
    if name not in old_pharm:
        new_pharmacies.append(name)
        continue
    for d in dosages:
        old_val = old_pharm[name].get(d)
        new_val = p["prices"].get(d)
        if old_val is not None and new_val is not None and abs(old_val - new_val) > 0.005:
            changes.append(f"{name} {d}: £{old_val:.2f} → £{new_val:.2f} ({new_val-old_val:+.2f})")

summary = {
    "total": len(pharmacies),
    "stats": stats,
    "changes": len(changes),
    "change_details": changes[:50],
    "new_pharmacies": new_pharmacies
}
print(json.dumps(summary, indent=2))
