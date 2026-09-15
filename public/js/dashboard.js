/**
 * dashboard.js — Overview KPIs/charts and the Destinations grid.
 * (Map rendering lives in map.js.)
 */
(() => {
  function accentColor(n) {
    const palette = ['#0e3b2e', '#175a45', '#1f6e52', '#c9982e', '#b5573a', '#4b5147'];
    return palette[(n - 1) % palette.length];
  }

  function renderKPIs(overview) {
    const row = document.getElementById('kpi-row');
    const sign = overview.yoyGrowthPct >= 0 ? '+' : '';
    const domesticPct = ((overview.totalDomestic / overview.totalTourists) * 100).toFixed(1);
    const foreignPct = ((overview.totalForeign / overview.totalTourists) * 100).toFixed(1);

    row.innerHTML = `
      <div class="kpi-card accent">
        <div class="kpi-label">Total Tourists, 2024&ndash;25</div>
        <div class="kpi-value">${App.formatMillions(overview.totalTourists)}</div>
        <div class="kpi-sub">${sign}${overview.yoyGrowthPct}% YoY (2024&rarr;2025)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Domestic Tourists</div>
        <div class="kpi-value">${App.formatMillions(overview.totalDomestic)}</div>
        <div class="kpi-sub positive">${domesticPct}% of total</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Foreign Tourists</div>
        <div class="kpi-value">${App.formatMillions(overview.totalForeign)}</div>
        <div class="kpi-sub positive">${foreignPct}% of total</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Est. Tourism Revenue</div>
        <div class="kpi-value">${App.formatLakhsAsCrore(overview.totalRevenueLakhs)}</div>
        <div class="kpi-sub">${App.formatNumber(Math.round(overview.totalRevenueLakhs))} Lakhs INR</div>
      </div>
    `;
  }

  function renderTrendChart(trends) {
    const labels = trends['2024'].monthly.map((m) => m.month);
    new Chart(document.getElementById('chart-trend'), {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: '2024',
            data: trends['2024'].monthly.map((m) => m.total),
            borderColor: '#1f6e52',
            backgroundColor: 'rgba(31,110,82,0.10)',
            tension: 0.35,
            fill: true,
            pointRadius: 3
          },
          {
            label: '2025',
            data: trends['2025'].monthly.map((m) => m.total),
            borderColor: '#c9982e',
            backgroundColor: 'rgba(201,152,46,0.10)',
            tension: 0.35,
            fill: true,
            pointRadius: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { family: 'Inter' } } } },
        scales: {
          y: { ticks: { callback: (v) => `${(v / 1e6).toFixed(1)}M` }, grid: { color: '#edefe6' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  function renderDomesticForeignChart(overview) {
    new Chart(document.getElementById('chart-domestic-foreign'), {
      type: 'doughnut',
      data: {
        labels: ['Domestic', 'Foreign'],
        datasets: [{ data: [overview.totalDomestic, overview.totalForeign], backgroundColor: ['#175a45', '#c9982e'], borderWidth: 0 }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { family: 'Inter' } } } }
      }
    });
  }

  function renderTopCircuitsChart(places) {
    const top = [...places].sort((a, b) => b.totalFootfall - a.totalFootfall).slice(0, 6);
    new Chart(document.getElementById('chart-top-circuits'), {
      type: 'bar',
      data: {
        labels: top.map((p) => p.name),
        datasets: [{ data: top.map((p) => p.totalFootfall), backgroundColor: '#1f6e52', borderRadius: 6, maxBarThickness: 26 }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { callback: (v) => `${(v / 1e6).toFixed(1)}M` }, grid: { color: '#edefe6' } },
          y: { grid: { display: false } }
        }
      }
    });
  }

  function renderMiniDestinations(places) {
    const top = [...places].sort((a, b) => b.totalFootfall - a.totalFootfall).slice(0, 5);
    document.getElementById('mini-destinations').innerHTML = top
      .map(
        (p, i) => `
      <div class="mini-dest-row">
        <span class="mini-dest-rank">${i + 1}</span>
        <span class="mini-dest-name">${p.name}</span>
        <span class="mini-dest-footfall">${App.formatMillions(p.totalFootfall)}</span>
      </div>`
      )
      .join('');
  }

  function renderDestinationsGrid(places) {
    const grid = document.getElementById('destinations-grid');
    const sorted = [...places].sort((a, b) => a.rank - b.rank);
    grid.innerHTML = sorted
      .map(
        (p) => `
      <div class="dest-card">
        <div class="dest-card-media" style="background: linear-gradient(135deg, ${accentColor(p.rank)}, ${accentColor(p.rank + 3)})">
          <span class="dest-card-rank">#${p.rank}</span>
          <h3>${p.name}</h3>
        </div>
        <div class="dest-card-body">
          <span class="dest-card-category">${p.category}</span>
          <p class="dest-card-history">${p.history}</p>
          <p class="dest-card-attractions"><strong>Attractions:</strong> ${p.attractions.join(', ')}</p>
          <div class="dest-card-footer">
            <span class="dest-card-footfall">${App.formatMillions(p.totalFootfall)} visitors</span>
            <button class="dest-card-btn" data-place-id="${p.id}" type="button">View on map</button>
          </div>
        </div>
      </div>`
      )
      .join('');

    grid.querySelectorAll('[data-place-id]').forEach((btn) => {
      btn.addEventListener('click', () => {
        App.switchView('map');
        window.dispatchEvent(new CustomEvent('map:focus-circuit', { detail: { id: btn.dataset.placeId } }));
      });
    });
  }

  async function init() {
    const data = await App.loadData();
    renderKPIs(data.overview);
    renderTrendChart(data.trends);
    renderDomesticForeignChart(data.overview);
    renderTopCircuitsChart(data.places);
    renderMiniDestinations(data.places);
    renderDestinationsGrid(data.places);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
