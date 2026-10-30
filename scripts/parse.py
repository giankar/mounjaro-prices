import json, os
from datetime import datetime, timedelta

dubai_time = datetime.now(datetime.timezone.utc) + timedelta(hours=4)
today_str = dubai_time.strftime("%Y-%m-%d")
scraped_at = dubai_time.strftime("%Y-%m-%dT%H:%M:%S+04:00")

dosage_names = ["2.5mg", "5mg", "7.5mg", "10mg", "12.5mg", "15mg"]

pharmacies = [
    ["Asda", "https://monj.co.uk/asda-online-doctor-discount-codes/", 172.47, 192.47, 252.47, 282.47, 292.47, 302.47, 4.5, "1116105", "", "No Discount Available"],
    ["Ashcroft Pharmacy", "https://monj.co.uk/ashcroft-pharmacy-discount-codes/", 156.98, 171.98, 231.98, 256.98, 276.98, 301.98, 4.8, "9012896", "", "£17 Off 1st Orders"],
    ["Ayp Healthcare", "https://monj.co.uk/ayp-healthcare-discount-codes/", 137.99, 157.99, 208.99, 235.99, 247.99, 269.99, 3.9, "9012896", "", "More Details"],
    ["Bolt Pharmacy", "https://monj.co.uk/bolt-pharmacy-discount-codes/", 169.00, 199.00, 259.00, 289.00, 309.00, 319.00, 4.5, "9012918", "SUB", "£40 Off 1st Orders"],
    ["Boots", "https://www.boots.com/online/pharmacy/", 176.97, 189.97, 267.97, 302.97, 314.97, 334.97, 4.3, "1034053", "", "First Orders Must Be Collected in Store"],
    ["Chequp", "https://monj.co.uk/chequp-health-discount-codes/", 162.99, 202.99, 262.99, 292.99, 302.99, 332.99, 4.4, "9011284", "AS/SUB", ""],
    ["Click 2 Pharmacy", "https://monj.co.uk/click2pharmacy-discount-codes/", 150.98, 178.98, 227.98, 254.98, 274.98, 293.98, 4.8, "1033781", "", "£20 Off 1st Orders | £10 Off Return Orders"],
    ["Curate", "https://monj.co.uk/curate-discount-codes/", 189.00, 199.00, 259.00, 289.00, 309.00, 329.00, 3.9, "9012920", "", "25% Off 2.5mg,5mg & 7.5mg | £30 Off 10mg,12.5mg & 15mg"],
    ["Curely", "https://monj.co.uk/curely-discount-codes/", 139.59, 185.00, 238.00, 260.00, 289.00, 305.00, 4.6, "9012401", "SUB", "15% Off Subscriptions | 5% Off PAYG"],
    ["Cuva Health", "https://monj.co.uk/cuva-health-discount-codes/", 143.98, 178.98, 233.98, 263.98, 283.98, 303.98, 4.9, "9012581", "", "£15 Off 2.5mg | £35 Off 5mg to 15mg"],
    ["Dotor", "https://monj.co.uk/dotor-discounts-codes-savings/", 179.94, 199.94, 254.94, 284.94, 304.94, 314.94, 4.3, "9012775", "", "£40 Off All Orders"],
    ["Dr Weightmans", "https://monj.co.uk/dr-weightmans-discount-codes/", 149.99, 164.99, 218.99, 239.99, 259.99, 284.99, 4.9, "1092500", "", "More Details"],
    ["e-Surgery", "https://monj.co.uk/e-surgery-discount-codes-and-latest-savings-2026/", 176.46, 211.71, 282.29, 317.59, 341.13, 359.95, 4.7, "9012167", "SUB", "£40 Off First Orders"],
    ["Envigore", "https://monj.co.uk/envigore-discount-codes-and-savings/", 225.00, 254.00, 304.00, 310.00, 334.00, 344.00, 4.8, "9012382", "", "£5 Off First Order"],
    ["Farmeci", "https://monj.co.uk/farmeci-discount-code/", 145.00, 179.00, 239.00, 259.00, 279.00, 299.00, 4.6, "9010938", "", "NEW ONLY: 25% OFF 2.5MG | 10% OFF OTHERS"],
    ["GenMeds", "https://monj.co.uk/genmeds-discounts-codes-savings/", 184.98, 204.98, 254.98, 284.98, 304.98, 314.98, 4.7, "9013006", "", "£50-£85 Off 1st Orders | £30 Off Return Orders"],
    ["Get A Drip", "https://monj.co.uk/get-a-drip-discounts-codes/", 159.00, 179.00, 229.00, 259.00, 279.00, 299.00, 3.3, "9012347", "SUB", "£30 to £56 Off First Orders"],
    ["Get Weightloss", "https://monj.co.uk/get-weightloss-discount-codes/", 133.99, 160.00, 208.50, 238.47, 247.98, 269.00, 4.7, "9011648", "", "£10 Off 1st Orders"],
    ["Goodbody Clinic", "https://monj.co.uk/goodbody-clinic-discount-codes/", 239.00, 259.00, 299.00, 329.00, 349.00, 369.00, 4.8, "9012347", "AS/SUB", "£80 Off First Orders"],
    ["Happy Pharmacy", "https://monj.co.uk/happy-pharmacy-discount-codes/", 144.24, 179.24, 234.24, 259.24, 274.24, 304.24, 4.8, "9012585", "", "10% Off 1st Orders"],
    ["Hey Slim", "https://monj.co.uk/heyslim-discount-codes/", 169.00, 189.00, 249.00, 279.00, 299.00, 309.00, 4.1, "9012739", "", "£30 Off 1st Orders"],
    ["IQ Doctor", "https://monj.co.uk/iq-doctor-discount-codes/", 179.99, 199.99, 249.99, 279.99, 299.99, 309.99, 4.6, "9010411", "", "Up to £80 Off | £20 Return Orders"],
    ["Jood Life", "https://monj.co.uk/jood-life-discount-code/", 139.00, 153.00, 205.00, 230.00, 247.00, 269.00, 4.3, "9012739", "", "£10 Off First Orders"],
    ["Juniper", "https://monj.co.uk/juniper-discount-codes/", 199.00, 229.00, 279.00, 304.00, 329.00, 339.00, 4.5, "9011842", "AS/SUB", "£50–£65 Off 1st Orders"],
    ["Live Well Weight Loss", "https://monj.co.uk/livewell-pharmacy-discount-codes/", 147.95, 172.95, 228.95, 252.95, 272.95, 292.95, 4.7, "9012516", "AS", "£5 Off 1st Orders"],
    ["Lloyds Pharmacy", "https://monj.co.uk/lloyds-pharmacy-discount-codes/", 185.94, 195.94, 255.94, 285.94, 305.94, 315.94, 4.3, "9011437", "", "£40 Off 1st Orders"],
    ["Lotus Weight Loss", "https://monj.co.uk/lotus-weight-loss-discounts-and-codes/", 154.00, 168.00, 221.00, 246.00, 268.00, 284.00, 4.1, "9010938", "AS", "£50 off 2.5mg | £25 off all other doses"],
    ["Manchester Chemist", "https://monj.co.uk/manchester-chemist-discount-codes-offers/", 150.00, 170.00, 220.00, 240.00, 260.00, 280.00, 4.7, "9010683", "", "More Details"],
    ["MedExpress", "https://monj.co.uk/medexpress-discount-codes/", 183.94, 193.94, 253.94, 283.94, 303.94, 313.94, 4.2, "9012633", "", "£50 Off First Orders"],
    ["Medhut", "https://monj.co.uk/medhut-discount-codes/", 135.99, 159.99, 207.99, 236.99, 254.99, 274.99, 4.6, "9012752", "", "More Details"],
    ["Medicine Marketplace", "https://monj.co.uk/medicine-marketplace-discount-codes/", 137.00, 154.00, 205.00, 229.00, 246.00, 266.00, 4.6, "1116946", "", "More Details"],
    ["Medino", "https://monj.co.uk/medino-discounts-and-codes/", 147.49, 169.99, 249.99, 269.99, 299.99, 319.99, 4.8, "9011921", "", "10% Off 1st Orders | 5% Off Return Orders"],
    ["MSH Weight Loss", "https://monj.co.uk/msh-weight-loss-discount-codes/", 189.00, 209.00, 249.00, 289.00, 299.00, 319.00, 4.5, "1039469", "", "More Details"],
    ["My London Pharmacy", "https://monj.co.uk/my-london-london-pharmacy-discount-code/", 145.00, 179.00, 239.00, 259.00, 279.00, 299.00, 4.6, "9011790", "", "NEW ONLY: 25% OFF 2.5MG | 10% OFF OTHERS"],
    ["Next Script", "https://monj.co.uk/next-script-pharmacy-discount-codes/", 131.00, 154.00, 204.99, 230.00, 246.00, 266.00, 4.0, "9012568", "", "More Details"],
    ["Nulife Pharmacy", "https://monj.co.uk/nulife-pharmacy-discount-codes/", 133.99, 158.99, 206.99, 235.99, 250.99, 270.99, 4.6, "9012931", "", "More Details"],
    ["Numan", "https://monj.co.uk/numan-discounts-codes/", 209.00, 239.00, 289.00, 309.00, 329.00, 339.00, 4.6, "9011408", "AS/SUB", ""],
    ["OnlineMeds", "https://monj.co.uk/onlinemeds-discount-codes-and-offers/", 167.99, 182.49, 233.99, 258.49, 279.99, 299.99, 4.7, "9012658", "", "£30 Off 1st Orders"],
    ["Oushk", "https://www.oushkpharmacy.com/", 173.99, 179.98, 232.98, 283.99, 276.99, 314.99, 4.6, "9012610", "", "£30 Off 1st Orders | £20 Off Return Orders"],
    ["Pharmacy Advance", "https://pharmacyadvance.co.uk/", 154.99, 174.99, 244.99, 274.99, 294.99, 314.99, 4.3, "9012423", "", "More Details"],
    ["Pharmacy Express", "https://monj.co.uk/pharmacy-express-dsicount-codes/", 144.99, 164.99, 224.99, 244.99, 264.99, 284.99, 5.0, "9012468", "", "More Details"],
    ["Pharmacy2U", "https://monj.co.uk/pharmacy2u-discount-codes/", 176.24, 196.24, 251.24, 286.24, 296.24, 306.24, 4.6, "9010146", "", "Upto £75 Off 1st Orders"],
    ["Pharmica", "https://monj.co.uk/pharmica-discount-codes-savings-offers/", 159.99, 199.99, 259.99, 284.99, 309.99, 319.99, 4.9, "9012030", "", "£35 Off 1st Order | £20 Off Return Orders"],
    ["Pharmulous", "https://pharmulous.co.uk/", 144.98, 169.98, 219.98, 244.98, 264.98, 279.98, 4.8, "9012252", "", ""],
    ["Pills2U", "https://monj.co.uk/pills2u-discount-codes/", 145.99, 164.98, 218.98, 243.99, 264.99, 289.99, 4.6, "9012634", "", "£10 Off 1st Orders"],
    ["PillSorted", "https://monj.co.uk/pillsorted-discount-code-voucher-for-weight-loss-treatment/", 186.98, 206.98, 256.98, 286.98, 306.98, 316.98, 4.7, "9011258", "", "£40 Off 1st Orders"],
    ["PillSphere", "https://monj.co.uk/pillsphere-discount-codes", 165.99, 187.99, 238.99, 265.99, 287.99, 299.99, 4.5, "9012694", "", ""],
    ["Second Nature", "https://monj.co.uk/second-nature-discount-codes-savings-and-offers/", 229.00, 259.00, 289.00, 309.00, 329.00, 349.00, 4.5, "9013068", "AS/SUB", "£50 Off 1st Orders"],
    ["Shape8", "https://monj.co.uk/shape8-pharmacy-discount-codes/", 168.99, 188.94, 243.99, 266.99, 287.99, 308.99, 3.8, "1124246", "", "£45 Off 1st Orders"],
    ["Simple Online Pharmacy", "https://monj.co.uk/simple-online-pharmacy-discount-codes/", 173.00, 203.99, 263.99, 303.99, 313.99, 323.99, 4.7, "9011287", "", "£40 Off 1st Orders"],
    ["Skin & Shape", "https://monj.co.uk/skin-and-shape-discount-codes/", 174.99, 199.99, 249.99, 279.99, 299.99, 309.99, 4.8, "9012790", "", "£40 Off 1st Orders | £25 Off Return Orders"],
    ["Slimming Direct", "https://monj.co.uk/slimming-direct-discount-codes/", 130.00, 165.00, 230.00, 250.00, 265.00, 300.00, 4.2, "1031513", "", "More Details"],
    ["Superdrug", "https://monj.co.uk/superdrug-discount-codes/", 180.50, 193.50, 271.50, 306.50, 318.50, 338.50, 4.5, "9010736", "", ""],
    ["Swift Doctor", "https://monj.co.uk/swift-doctor-discount-codes-and-offers/", 149.00, 169.00, 225.00, 249.00, 265.00, 289.00, 4.9, "9012809", "", "£10 Off First Orders"],
    ["Swift Medi", "https://monj.co.uk/swift-medi-discounts-codes/", 192.75, 198.99, 258.20, 292.50, 302.99, 334.55, 4.6, "9012840", "", "£50 Off 1st Orders | £20 Off Return Orders"],
    ["The Care Pharmacy", "https://monj.co.uk/the-care-pharmacy-discount-codes-and-offers/", 149.99, 184.99, 234.99, 259.99, 279.99, 299.99, 4.9, "9010308", "", "£22.50 Off First Orders"],
    ["The Family Chemist", "https://monj.co.uk/the-family-chemist-discount-codes-and-savings-vouchers/", 164.99, 174.99, 234.99, 259.99, 274.99, 294.99, 4.8, "9012915", "AS", "£40 Off 2.5mg | £35 Off First Orders | £10 Off Return Orders"],
    ["The Independent Pharmacy", "https://monj.co.uk/the-independent-pharmacy-discount-codes-and-offers/", 179.99, 199.99, 259.99, 289.99, 304.99, 324.99, 4.8, "9012559", "", "20% Off First Orders"],
    ["Tribelle", "https://monj.co.uk/tribelle-discounts-codes-offers-savings/", 169.99, 173.99, 227.99, 253.99, 273.99, 293.99, 4.8, "9012688", "", "£20 Off 1st Orders"],
    ["Voy", "https://monj.co.uk/voy-discounts-codes-offers-voucher/", 214.00, 244.00, 294.00, 324.00, 344.00, 359.00, 4.7, "9012134", "AS/SUB", ""],
    ["Well Pharmacy", "https://monj.co.uk/well-pharmacy-discount-codes/", 153.95, 193.95, 253.95, 293.95, 313.95, 323.95, 4.3, "9010492", "", "£9.99 Off 1st Orders"],
    ["WePrescribe", "https://monj.co.uk/weprescribe-discount-codes-and-offers/", 166.49, 191.49, 246.49, 264.49, 291.49, 306.49, 4.8, "9012132", "", "£41.50 Off 1st orders"],
    ["YourPharmacy", "https://monj.co.uk/your-pharmacy-discount-codes-and-offers/", 172.95, 193.95, 258.95, 279.95, 293.95, 302.95, 4.5, "9012029", "", "£25 Off 1st Orders"],
    ["Zava", "https://monj.co.uk/zava-discount-codes-and-offers/", 169.99, 187.99, 249.99, 279.99, 299.99, 309.99, 4.4, "9011147", "", "£40 Off 1st Orders | £15 Off Return Orders"],
]

pharmacy_list = []
for p in pharmacies:
    name, url, p25, p5, p75, p10, p125, p15, tp, gphc, subscription, discounts = p
    entry = {
        "name": name,
        "url": url,
        "prices": {"2.5mg": p25, "5mg": p5, "7.5mg": p75, "10mg": p10, "12.5mg": p125, "15mg": p15},
        "trustpilot": tp,
        "gphc": gphc,
        "subscription": subscription if subscription else None,
        "discounts": discounts if discounts else None
    }
    pharmacy_list.append(entry)

stats = {}
for d in dosage_names:
    prices = [p["prices"][d] for p in pharmacy_list]
    stats[d] = {"min": round(min(prices), 2), "avg": round(sum(prices) / len(prices), 2), "max": round(max(prices), 2)}

# Daily snapshot
snapshot = {
    "date": today_str,
    "scraped_at": scraped_at,
    "source": "https://monj.co.uk/mounjaro-price-list-non-discounted-uk/",
    "total_pharmacies": len(pharmacy_list),
    "stats": stats,
    "pharmacies": pharmacy_list
}

# Price history
price_history = {
    "meta": {
        "source": "https://monj.co.uk/mounjaro-price-list-non-discounted-uk/",
        "description": "Mounjaro UK non-discounted retail prices across pharmacies",
        "dosages": dosage_names,
        "last_scraped": scraped_at,
        "total_pharmacies": len(pharmacy_list)
    },
    "pharmacies": pharmacy_list
}

# Time series entry
ts_entry = {"date": today_str, "total_pharmacies": len(pharmacy_list), "stats": stats}

# Save
os.makedirs('/home/user/output', exist_ok=True)
with open('/home/user/output/daily-snapshot.json', 'w') as f:
    json.dump(snapshot, f, indent=2)
with open('/home/user/output/price-history.json', 'w') as f:
    json.dump(price_history, f, indent=2)
with open('/home/user/output/time-series-entry.json', 'w') as f:
    json.dump(ts_entry, f, indent=2)

print(f"OK: {len(pharmacy_list)} pharmacies")
for d in dosage_names:
    s = stats[d]
    print(f"  {d}: min=£{s['min']:.2f} avg=£{s['avg']:.2f} max=£{s['max']:.2f}")
