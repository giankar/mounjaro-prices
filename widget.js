/**
 * Mounjaro UK Price Tracker Widget — Embeddable Graph
 * Usage: Include this single JS file + a <div id="mounjaro-widget"></div>
 * Data source: /mounjaro-prices/daily-snapshots/ — static JSON files updated daily
 *
 * This widget renders:
 *  1. Cheapest pharmacy per dosage
 *  2. Price range (min/avg/max) per dosage
 *  3. Full pharmacy price table (sortable)
 *  4. When 2+ days of data exist: line graph tracking price trends per dosage
 */
(function () {
  const WIDGET_ID = 'mounjaro-widget';
  const DATA_BASE = '/mounjaro-prices';
  const DOSAGES = ['2.5mg', '5mg', '7.5mg', '10mg', '12.5mg', '15mg'];
  const COLORS = ['#2563eb', '#7c3aed', '#dc2626', '#ea580c', '#059669', '#d97706'];

  // ------------------- helpers -------------------
  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);
    if (attrs) Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
      else if (k.startsWith('on')) el.addEventListener(k.slice(2).toLowerCase(), v);
      else el.setAttribute(k, v);
    });
    children.forEach(c => {
      if (typeof c === 'string') el.appendChild(document.createTextNode(c));
      else if (c instanceof Node) el.appendChild(c);
    });
    return el;
  }

  function fmt(price) { return '£' + price.toFixed(2); }

  // ------------------- data fetching -------------------
  async function loadSnapshots() {
    // In production, serve a manifest file listing all snapshots.
    // For the demo, we load the master price-history.json + daily snapshots.
    const snapshots = [];
    try {
      // Try loading list of snapshots
      const resp = await fetch(DATA_BASE + '/price-history.json');
      if (resp.ok) {
        const master = await resp.json();
        // also try to load individual daily snapshots
        const today = new Date();
        for (let d = 0; d < 90; d++) {
          const dt = new Date(today);
          dt.setDate(dt.getDate() - d);
          const dateStr = dt.toISOString().slice(0, 10);
          try {
            const sr = await fetch(DATA_BASE + '/daily-snapshots/' + dateStr + '.json');
            if (sr.ok) {
              const snap = await sr.json();
              snapshots.unshift(snap); // oldest first
            }
          } catch(e) { /* skip missing days */ }
        }
      }
    } catch(e) {
      console.warn('Could not load snapshots:', e);
    }
    return snapshots;
  }

  // ------------------- render sections -------------------
  function renderCheapest(snapshot) {
    const cheapest = {};
    DOSAGES.forEach(dose => {
      let best = null;
      snapshot.pharmacies.forEach(p => {
        const price = p.prices[dose];
        if (price != null && (best === null || price < best.price)) {
          best = { name: p.name, price };
        }
      });
      cheapest[dose] = best;
    });

    const cards = DOSAGES.map((dose, i) =>
      h('div', { class: 'mj-card', style: { borderTop: '3px solid ' + COLORS[i] } },
        h('div', { class: 'mj-card-dose' }, dose),
        h('div', { class: 'mj-card-price' }, fmt(cheapest[dose].price)),
        h('div', { class: 'mj-card-pharmacy' }, cheapest[dose].name)
      )
    );

    return h('div', {},
      h('h3', { class: 'mj-section-title' }, '🏆 Cheapest Pharmacy Per Dosage'),
      h('div', { class: 'mj-cards' }, ...cards)
    );
  }

  function renderPriceRange(snapshot) {
    const rows = DOSAGES.map((dose, i) => {
      const prices = snapshot.pharmacies.map(p => p.prices[dose]).filter(Boolean).sort((a,b) => a-b);
      const min = prices[0];
      const max = prices[prices.length-1];
      const avg = prices.reduce((s,v) => s+v, 0) / prices.length;
      return h('tr', {},
        h('td', { style: { fontWeight: 600 } }, dose),
        h('td', { style: { color: '#059669' } }, fmt(min)),
        h('td', {}, fmt(avg)),
        h('td', { style: { color: '#dc2626' } }, fmt(max))
      );
    });

    return h('div', {},
      h('h3', { class: 'mj-section-title' }, '📊 Price Range Per Dosage'),
      h('table', { class: 'mj-table' },
        h('thead', {},
          h('tr', {},
            h('th', {}, 'Dosage'),
            h('th', {}, 'Min'),
            h('th', {}, 'Average'),
            h('th', {}, 'Max')
          )
        ),
        h('tbody', {}, ...rows)
      )
    );
  }

  function renderTrendChart(snapshots) {
    if (snapshots.length < 2) return h('div', { class: 'mj-empty' }, '📈 Price trend chart will appear after 2+ days of data.');

    const container = h('div', { style: { position: 'relative' } });
    const canvas = h('canvas', { id: 'mj-trend-canvas', style: { maxWidth: '100%', height: '400px' } });
    container.appendChild(h('h3', { class: 'mj-section-title' }, '📈 Price Trends Over Time'));
    container.appendChild(canvas);

    setTimeout(() => drawChart(canvas, snapshots), 100);
    return container;
  }

  function drawChart(canvas, snapshots) {
    const ctx = canvas.getContext('2d');
    const W = canvas.parentElement.clientWidth;
    const H = 400;
    canvas.width = W;
    canvas.height = H;
    const pad = { top: 30, right: 30, bottom: 60, left: 60 };
    const pw = W - pad.left - pad.right;
    const ph = H - pad.top - pad.bottom;

    // Build datasets: for each dosage, track min price across all pharmacies per day
    const datasets = DOSAGES.map((dose, i) => {
      const points = snapshots.map(snap => {
        const prices = snap.pharmacies.map(p => p.prices[dose]).filter(Boolean);
        const min = prices.length ? Math.min(...prices) : null;
        const avg = prices.length ? prices.reduce((s,v) => s+v, 0) / prices.length : null;
        return { date: snap.date, min, avg };
      });
      return { label: dose, color: COLORS[i], points };
    });

    // Find global min/max
    let yMin = Infinity, yMax = -Infinity;
    datasets.forEach(ds => ds.points.forEach(p => {
      if (p.min !== null) { yMin = Math.min(yMin, p.min - 5); yMax = Math.max(yMax, p.min + 5); }
    }));
    if (!isFinite(yMin)) { yMin = 100; yMax = 400; }

    const xScale = (i) => pad.left + (i / (snapshots.length - 1)) * pw;
    const yScale = (v) => pad.top + ph - ((v - yMin) / (yMax - yMin)) * ph;

    // Clear
    ctx.clearRect(0, 0, W, H);

    // Grid lines
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 0.5;
    for (let v = Math.ceil(yMin / 10) * 10; v <= yMax; v += 10) {
      const y = yScale(v);
      ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(W - pad.right, y); ctx.stroke();
      ctx.fillStyle = '#6b7280'; ctx.font = '11px sans-serif';
      ctx.textAlign = 'right'; ctx.fillText('£' + v, pad.left - 8, y + 4);
    }

    // X axis labels
    ctx.fillStyle = '#6b7280'; ctx.font = '11px sans-serif'; ctx.textAlign = 'center';
    snapshots.forEach((snap, i) => {
      if (i % Math.max(1, Math.floor(snapshots.length / 8)) === 0 || i === snapshots.length - 1) {
        ctx.fillText(snap.date.slice(5), xScale(i), H - pad.bottom + 20);
      }
    });

    // Draw lines
    datasets.forEach(ds => {
      ctx.strokeStyle = ds.color;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      let first = true;
      ds.points.forEach((p, i) => {
        if (p.min === null) return;
        const x = xScale(i), y = yScale(p.min);
        if (first) { ctx.moveTo(x, y); first = false; }
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      // Dots + labels at last point
      ds.points.forEach((p, i) => {
        if (p.min === null) return;
        const x = xScale(i), y = yScale(p.min);
        ctx.fillStyle = ds.color;
        ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI*2); ctx.fill();
        if (i === ds.points.length - 1) {
          ctx.font = 'bold 12px sans-serif'; ctx.textAlign = 'left';
          ctx.fillText(ds.label, x + 6, y);
        }
      });
    });
  }

  function renderFullTable(snapshot) {
    const sorted = [...snapshot.pharmacies].sort((a, b) => {
      const aMin = Math.min(...DOSAGES.map(d => a.prices[d]).filter(Boolean));
      const bMin = Math.min(...DOSAGES.map(d => b.prices[d]).filter(Boolean));
      return aMin - bMin;
    });

    const rows = sorted.map(p => {
      const minPrice = Math.min(...DOSAGES.map(d => p.prices[d]).filter(Boolean));
      const maxPrice = Math.max(...DOSAGES.map(d => p.prices[d]).filter(Boolean));
      return h('tr', {},
        h('td', { style: { fontWeight: 600 } }, p.name),
        h('td', { style: { color: '#059669' } }, fmt(minPrice)),
        h('td', { style: { color: '#dc2626' } }, fmt(maxPrice)),
        ...DOSAGES.map(d => h('td', {}, p.prices[d] != null ? fmt(p.prices[d]) : '-')),
        h('td', {}, p.trustpilot != null ? '⭐ ' + p.trustpilot : '-')
      );
    });

    return h('div', {},
      h('h3', { class: 'mj-section-title' }, '📋 All Pharmacies (sorted by cheapest entry dose)'),
      h('div', { class: 'mj-table-wrap' },
        h('table', { class: 'mj-table mj-table-full' },
          h('thead', {},
            h('tr', {},
              h('th', {}, 'Pharmacy'),
              h('th', {}, 'Min'),
              h('th', {}, 'Max'),
              ...DOSAGES.map(d => h('th', {}, d)),
              h('th', {}, 'Trustpilot')
            )
          ),
          h('tbody', {}, ...rows)
        )
      )
    );
  }

  // ------------------- main render -------------------
  async function init() {
    const root = document.getElementById(WIDGET_ID);
    if (!root) return;
    root.innerHTML = '<div class="mj-loading">⏳ Loading Mounjaro price data...</div>';

    const snapshots = await loadSnapshots();
    if (!snapshots.length) {
      root.innerHTML = '<p>No price data available yet.</p>';
      return;
    }

    const latest = snapshots[snapshots.length - 1];
    root.innerHTML = '';

    root.appendChild(h('div', { class: 'mj-header' },
      h('h2', { style: { margin: 0, color: '#1e3a5f' } }, '💊 Mounjaro UK Retail Prices'),
      h('p', { style: { margin: '4px 0 0', color: '#6b7280', fontSize: '14px' } },
        'Non-discounted prices — Last updated: ' + latest.date + ' — Source: ',
        h('a', { href: 'https://monj.co.uk/mounjaro-price-list-non-discounted-uk/', target: '_blank', style: { color: '#2563eb' } }, 'Monj.co.uk')
      )
    ));

    root.appendChild(h('div', { class: 'mj-grid' },
      h('div', { class: 'mj-grid-left' },
        renderCheapest(latest),
        renderPriceRange(latest)
      ),
      h('div', { class: 'mj-grid-right' },
        renderTrendChart(snapshots)
      )
    ));

    root.appendChild(renderFullTable(latest));
  }

  // ------------------- styles injection -------------------
  const css = `
  #${WIDGET_ID} { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1f2937; max-width: 1200px; margin: 0 auto; }
  #${WIDGET_ID} * { box-sizing: border-box; }
  .mj-header { text-align: center; margin-bottom: 24px; }
  .mj-loading { text-align: center; padding: 40px; font-size: 18px; color: #6b7280; }
  .mj-empty { text-align: center; padding: 40px; color: #9ca3af; font-style: italic; }
  .mj-section-title { font-size: 16px; font-weight: 600; margin: 0 0 12px 0; color: #374151; }
  .mj-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }
  @media (max-width: 768px) { .mj-grid { grid-template-columns: 1fr; } }
  .mj-grid-left > div { margin-bottom: 24px; }
  .mj-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  @media (max-width: 500px) { .mj-cards { grid-template-columns: repeat(2, 1fr); } }
  .mj-card { background: #fff; border-radius: 10px; padding: 14px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .mj-card-dose { font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }
  .mj-card-price { font-size: 22px; font-weight: 700; color: #1f2937; margin: 4px 0; }
  .mj-card-pharmacy { font-size: 12px; color: #6b7280; }
  .mj-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .mj-table th { background: #f9fafb; padding: 8px 10px; text-align: left; font-weight: 600; color: #374151; border-bottom: 2px solid #e5e7eb; white-space: nowrap; }
  .mj-table td { padding: 7px 10px; border-bottom: 1px solid #f3f4f6; }
  .mj-table tr:hover td { background: #f9fafb; }
  .mj-table-wrap { max-height: 600px; overflow-y: auto; border: 1px solid #e5e7eb; border-radius: 8px; }
  .mj-table-full th { position: sticky; top: 0; z-index: 1; }
  `;

  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
