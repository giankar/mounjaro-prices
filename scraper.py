#!/usr/bin/env python3
"""
Mounjaro UK Price Scraper
Scrapes https://monj.co.uk/mounjaro-price-list-non-discounted-uk/
Outputs structured JSON to the daily snapshots directory.

The page uses a WordPress table with class="column-N" on each <td>:
  column-1: Pharmacy name + link
  column-2: 2.5mg price
  column-3: 5mg price
  column-4: 7.5mg price
  column-5: 10mg price
  column-6: 12.5mg price
  column-7: 15mg price
  column-8: Trustpilot score
  column-9: GPhC registration
  column-10: Subscription indicator
  column-11: Discounts info
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

def extract_prices_from_html(html):
    """Parse the Monj price table from raw HTML."""
    pharmacies = []
    dosages = ['2.5mg', '5mg', '7.5mg', '10mg', '12.5mg', '15mg']

    # Find all table rows in <tbody>
    tbody_match = re.search(r'<tbody>(.*?)</tbody>', html, re.DOTALL)
    if not tbody_match:
        print('ERROR: Could not find <tbody> in HTML', file=sys.stderr)
        return []

    rows_html = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody_match.group(1), re.DOTALL)
    print(f'Found {len(rows_html)} rows in tbody')

    for row_html in rows_html:
        # Extract cells by class column-N
        cells = {}
        for m in re.finditer(r'<td class="column-(\d+)">(.*?)</td>', row_html, re.DOTALL):
            col_num = int(m.group(1))
            cells[col_num] = m.group(2).strip()

        if not cells or 1 not in cells:
            continue

        # Parse pharmacy name and URL from column-1
        name_match = re.search(r'<a[^>]*>([^<]+)</a>', cells[1])
        if not name_match:
            continue
        name = name_match.group(1).strip()

        url_match = re.search(r'href="([^"]+)"', cells[1])
        url = url_match.group(1) if url_match else ''

        # Parse prices from columns 2-7
        prices = {}
        for i, dose in enumerate(dosages):
            col = i + 2
            if col in cells:
                price_text = re.sub(r'<[^>]+>', '', cells[col]).strip()
                price_text = price_text.replace('£', '').replace(',', '').replace('*', '').strip()
                try:
                    if price_text:
                        prices[dose] = round(float(price_text), 2)
                except ValueError:
                    pass

        if not any(v is not None for v in prices.values()):
            continue

        # Trustpilot from column-8
        trustpilot = None
        if 8 in cells:
            tp_text = re.sub(r'<[^>]+>', '', cells[8]).strip()
            tp_match = re.search(r'([\d.]+)', tp_text)
            if tp_match:
                try:
                    trustpilot = float(tp_match.group(1))
                except ValueError:
                    pass

        # GPhC from column-9
        gphc = ''
        if 9 in cells:
            gphc_text = re.sub(r'<[^>]+>', '', cells[9]).strip()
            gphc_match = re.search(r'(\d+)', gphc_text)
            if gphc_match:
                gphc = gphc_match.group(1)

        # Subscription from column-10
        subscription = False
        if 10 in cells:
            subscription = 'SUB' in cells[10].upper()

        # Discounts from column-11
        discounts = ''
        if 11 in cells:
            discounts = re.sub(r'<[^>]+>', '', cells[11]).strip()

        pharmacies.append({
            'name': name,
            'url': url,
            'prices': prices,
            'trustpilot': trustpilot,
            'gphc': gphc,
            'subscription': subscription,
            'discounts': discounts
        })

    return pharmacies


def scrape(url):
    """Fetch and parse the price page."""
    import urllib.request
    import urllib.error

    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; MounjaroPriceTracker/1.0; +https://monj.co.uk)'
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except urllib.error.URLError as e:
        print(f'ERROR: Failed to fetch {url}: {e}', file=sys.stderr)
        sys.exit(1)

    pharmacies = extract_prices_from_html(html)

    if not pharmacies:
        print('ERROR: No pharmacy data extracted. The page structure may have changed.', file=sys.stderr)
        sys.exit(1)

    return pharmacies


def main():
    url = 'https://monj.co.uk/mounjaro-price-list-non-discounted-uk/'
    now = datetime.now(timezone.utc)
    date_str = now.strftime('%Y-%m-%d')

    print(f'Scraping {url}...')
    pharmacies = scrape(url)
    print(f'Extracted {len(pharmacies)} pharmacies.')

    snapshot = {
        'date': date_str,
        'scraped_at': now.isoformat(),
        'source': url,
        'pharmacies': pharmacies
    }

    # Write daily snapshot (working directory for scheduled tasks)
    output_dir = Path('data')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f'{date_str}.json'
    output_path.write_text(json.dumps(snapshot, indent=2))
    print(f'Wrote {output_path}')

    # Also update the aggregate price-history.json
    history_path = output_dir / 'price-history.json'
    existing = {}
    if history_path.exists():
        try:
            existing = json.loads(history_path.read_text())
        except json.JSONDecodeError:
            pass

    # Build history with today's full data
    existing['meta'] = {
        'source': url,
        'description': 'Mounjaro UK non-discounted retail prices across pharmacies',
        'dosages': ['2.5mg', '5mg', '7.5mg', '10mg', '12.5mg', '15mg'],
        'last_scraped': now.isoformat(),
        'total_pharmacies': len(pharmacies)
    }
    existing['pharmacies'] = pharmacies

    history_path.write_text(json.dumps(existing, indent=2))
    print(f'Updated {history_path}')

    # Print summary
    for dose in ['2.5mg', '5mg', '7.5mg', '10mg', '12.5mg', '15mg']:
        dose_prices = [p['prices'][dose] for p in pharmacies if p['prices'].get(dose) is not None]
        if dose_prices:
            print(f'  {dose}: min=£{min(dose_prices):.2f}  avg=£{sum(dose_prices)/len(dose_prices):.2f}  max=£{max(dose_prices):.2f}  ({len(dose_prices)} pharmacies)')


if __name__ == '__main__':
    main()
