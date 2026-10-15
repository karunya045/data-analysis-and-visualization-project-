/**
 * app.js — shell behaviour shared across views:
 *   - sidebar navigation
 *   - the place detail modal
 *   - one-time data loading (so dashboard.js and map.js don't both re-fetch)
 *   - small number-formatting helpers
 */
const App = (() => {
  const state = {
    overview: null,
    trends: null,
    places: null,
    _loadPromise: null
  };

  // ---------- data loading (fetched once, shared) ----------
  async function loadData() {
    if (state._loadPromise) return state._loadPromise;
    state._loadPromise = (async () => {
      const [overviewRes, trendsRes, placesRes] = await Promise.all([
        fetch('/api/overview'),
        fetch('/api/trends'),
        fetch('/api/places')
      ]);
      state.overview = await overviewRes.json();
      state.trends = await trendsRes.json();
      state.places = await placesRes.json();
      return state;
    })();
    return state._loadPromise;
  }

  // ---------- navigation ----------
  function switchView(viewName) {
    document.querySelectorAll('.nav-item').forEach((btn) => {
      btn.classList.toggle('is-active', btn.dataset.view === viewName);
    });
    document.querySelectorAll('.view').forEach((section) => {
      section.classList.toggle('is-active', section.id === `view-${viewName}`);
    });
    window.dispatchEvent(new CustomEvent('view:changed', { detail: { view: viewName } }));
  }

  function initNav() {
    document.querySelectorAll('.nav-item[data-view]').forEach((btn) => {
      btn.addEventListener('click', () => switchView(btn.dataset.view));
    });
    document.querySelectorAll('[data-goto]').forEach((btn) => {
      btn.addEventListener('click', () => switchView(btn.dataset.goto));
    });
  }

  // ---------- place modal ----------
  function initModal() {
    const overlay = document.getElementById('place-modal');
    const closeBtn = document.getElementById('modal-close');
    const close = () => overlay.classList.add('hidden');
    closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  }

  function openPlaceModal({ title, category, circuitName, history, footfallLabel, revenueLabel, imageUrl }) {
    const overlay = document.getElementById('place-modal');
    document.getElementById('modal-category').textContent = category || '';
    document.getElementById('modal-title').textContent = title || '';
    document.getElementById('modal-circuit').textContent = circuitName ? `Part of the ${circuitName} circuit` : '';
    document.getElementById('modal-history').textContent = history || '';

    const img = document.getElementById('modal-image');
    img.textContent = '';
    if (imageUrl) {
      img.style.backgroundImage = `url("${imageUrl}")`;
      img.style.color = 'transparent';
    } else {
      img.style.backgroundImage = 'none';
      img.style.color = '';
      img.textContent = title || '';
    }

    const stats = document.getElementById('modal-stats');
    stats.innerHTML = '';
    if (footfallLabel) {
      stats.innerHTML += `<div><div class="modal-stat-value">${footfallLabel}</div><div class="modal-stat-label">2-yr footfall (circuit)</div></div>`;
    }
    if (revenueLabel) {
      stats.innerHTML += `<div><div class="modal-stat-value">${revenueLabel}</div><div class="modal-stat-label">Est. revenue (circuit)</div></div>`;
    }

    overlay.classList.remove('hidden');
  }

  // ---------- formatting helpers ----------
  const formatNumber = (n) => Number(n).toLocaleString('en-IN');
  const formatMillions = (n) => `${(n / 1_000_000).toFixed(2)}M`;
  const formatLakhsAsCrore = (lakhs) => `\u20B9${(lakhs / 100).toLocaleString('en-IN', { maximumFractionDigits: 1 })} Cr`;

  function init() {
    initNav();
    initModal();
  }

  document.addEventListener('DOMContentLoaded', init);

  return { loadData, state, switchView, openPlaceModal, formatNumber, formatMillions, formatLakhsAsCrore };
})();
