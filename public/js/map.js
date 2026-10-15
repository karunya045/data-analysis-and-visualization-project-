/**
 * map.js — the interactive map view.
 *
 * - Loads Geoapify raster tiles into a Leaflet map.
 * - Geocodes every named attraction (from places.json) via the Geoapify
 *   Geocoding API, caching results in localStorage so repeat visits are instant.
 * - Renders one marker per attraction; clicking a marker opens the shared
 *   place modal (see app.js) with its image/history/stats.
 * - Lazily initialises on first visit to the Map view (Leaflet requires a
 *   visible container), and re-validates its size on later visits.
 */
(() => {
  let leafletMap = null;
  let mapReadyPromise = null;
  const markersByPlace = {};

  function hasValidApiKey() {
    return typeof GEOAPIFY_API_KEY === 'string' && GEOAPIFY_API_KEY && GEOAPIFY_API_KEY !== 'YOUR_GEOAPIFY_API_KEY';
  }

  function categoryColor(category = '') {
    if (/unesco/i.test(category)) return '#b5573a';
    if (/pilgrimage|spiritual/i.test(category)) return '#c9982e';
    if (/wildlife|nature|eco/i.test(category)) return '#1f6e52';
    return '#0e3b2e';
  }

  function showBanner(html) {
    const banner = document.getElementById('map-key-banner');
    banner.innerHTML = html;
    banner.classList.remove('hidden');
  }

  // ---------- geocoding (Geoapify), cached in localStorage ----------
  async function geocodeAttraction(name) {
    const query = `${name}, Telangana, India`;
    const cacheKey = `geoapify_geocode_v1:${query}`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try { return JSON.parse(cached); } catch (e) { /* fall through and re-fetch */ }
    }
    const url = `https://api.geoapify.com/v1/geocode/search?text=${encodeURIComponent(query)}&filter=countrycode:in&format=json&limit=1&apiKey=${GEOAPIFY_API_KEY}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Geocoding request failed for "${name}" (${res.status})`);
    const data = await res.json();
    if (!data.results || !data.results.length) throw new Error(`No geocoding result for "${name}"`);
    const coords = { lat: data.results[0].lat, lon: data.results[0].lon };
    localStorage.setItem(cacheKey, JSON.stringify(coords));
    return coords;
  }

  async function addMarkersForPlace(place) {
    const settled = await Promise.allSettled(
      place.attractions.map((name) => geocodeAttraction(name).then((coords) => ({ name, coords })))
    );

    const markers = [];
    settled.forEach((result) => {
      if (result.status !== 'fulfilled') {
        console.warn(result.reason?.message || 'Geocoding failed');
        return;
      }
      const { name, coords } = result.value;
      const marker = L.circleMarker([coords.lat, coords.lon], {
        radius: 7,
        weight: 2,
        color: '#ffffff',
        fillColor: categoryColor(place.category),
        fillOpacity: 0.95
      }).addTo(leafletMap);
      marker.bindTooltip(name, { direction: 'top', offset: [0, -4] });
      marker.on('click', () => openPlaceDetail(place, name));
      markers.push(marker);
    });
    return markers;
  }

  function openPlaceDetail(place, attractionName) {
    App.openPlaceModal({
      title: attractionName,
      category: place.category,
      circuitName: place.name,
      history: place.history,
      footfallLabel: App.formatMillions(place.totalFootfall),
      revenueLabel: App.formatLakhsAsCrore(place.revenueLakhs),
      imageUrl: place.image || null
    });
  }

  // ---------- circuit sidebar list ----------
  function renderCircuitList(places) {
    const list = document.getElementById('circuit-list');
    list.innerHTML = places
      .map(
        (p) => `
      <li>
        <button class="circuit-list-item" data-id="${p.id}" type="button">
          <span>${p.name}</span>
          <span class="count">${p.attractions.length} sites</span>
        </button>
      </li>`
      )
      .join('');
    list.querySelectorAll('[data-id]').forEach((btn) => {
      btn.addEventListener('click', () => focusCircuit(btn.dataset.id));
    });
  }

  function focusCircuit(id) {
    const group = markersByPlace[id];
    if (!leafletMap || !group || !group.length) return;
    const bounds = L.latLngBounds(group.map((m) => m.getLatLng()));
    leafletMap.flyToBounds(bounds, { padding: [70, 70], maxZoom: 12, duration: 0.8 });
  }

  // ---------- main init (runs once, on first visit to the Map view) ----------
  async function initMap() {
    const data = await App.loadData();
    const places = data.places;

    leafletMap = L.map('leaflet-map', { scrollWheelZoom: true }).setView([17.9, 79.6], 7);
    renderCircuitList(places);

    if (!hasValidApiKey()) {
      document.getElementById('map-loading').classList.add('hidden');
      showBanner(
        `Add your free Geoapify API key in <code>public/js/config.js</code> to load map tiles and plot attractions. ` +
        `Get one at <a href="https://myprojects.geoapify.com/" target="_blank" rel="noopener">myprojects.geoapify.com</a> — takes about a minute, no card needed.`
      );
      return;
    }

    const isRetina = window.devicePixelRatio > 1;
    const tileUrl = `https://maps.geoapify.com/v1/tile/osm-bright/{z}/{x}/{y}${isRetina ? '@2x' : ''}.png?apiKey=${GEOAPIFY_API_KEY}`;
    L.tileLayer(tileUrl, {
      attribution:
        'Powered by <a href="https://www.geoapify.com/" target="_blank" rel="noopener">Geoapify</a> | ' +
        '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
      maxZoom: 20
    }).addTo(leafletMap);

    await Promise.all(
      places.map(async (place) => {
        markersByPlace[place.id] = await addMarkersForPlace(place);
      })
    );

    document.getElementById('map-loading').classList.add('hidden');

    const allMarkers = Object.values(markersByPlace).flat();
    if (allMarkers.length) {
      leafletMap.fitBounds(L.latLngBounds(allMarkers.map((m) => m.getLatLng())), { padding: [40, 40] });
    } else {
      showBanner(
        `No attractions could be geocoded. Double-check the Geoapify API key in <code>public/js/config.js</code> is correct and active.`
      );
    }
  }

  function ensureMapInitialized() {
    if (!mapReadyPromise) mapReadyPromise = initMap();
    return mapReadyPromise;
  }

  // ---------- wiring ----------
  window.addEventListener('view:changed', (e) => {
    if (e.detail.view !== 'map') return;
    if (!mapReadyPromise) {
      ensureMapInitialized();
    } else {
      mapReadyPromise.then(() => leafletMap && setTimeout(() => leafletMap.invalidateSize(), 50));
    }
  });

  // Fired by dashboard.js's "View on map" buttons
  window.addEventListener('map:focus-circuit', async (e) => {
    await ensureMapInitialized();
    focusCircuit(e.detail.id);
  });
})();
