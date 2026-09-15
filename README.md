# Telangana Tourism Dashboard

A full-stack analytics dashboard for Telangana tourism (2024–2025), with an
interactive map — click any attraction to see its category, history, and
circuit-level stats.

## Folder structure

```
telangana-tourism/
├── backend/
│   ├── server.js         ← plain Node.js HTTP server (zero npm packages)
│   ├── package.json
│   └── data/
│       ├── trends.json   ← monthly domestic/foreign/total visitors, 2024 & 2025
│       └── places.json   ← 12 tourist circuits: attractions, history, footfall, revenue
└── public/                ← served as static files by server.js
    ├── index.html
    ├── css/styles.css
    └── js/
        ├── config.js      ← put your Geoapify API key here
        ├── app.js         ← nav, modal, shared data loading
        ├── dashboard.js   ← KPI cards, charts, destinations grid
        └── map.js         ← Leaflet + Geoapify map and geocoding
```

## 1. Add your Geoapify API key

Open `public/js/config.js` and replace the placeholder:

```js
const GEOAPIFY_API_KEY = "YOUR_GEOAPIFY_API_KEY";
```

Get a free key at **https://myprojects.geoapify.com/** (no card required,
3,000 requests/day free). Without a key, every page works except the map,
which will show a banner telling you to add one.

## 2. Run it

No `npm install` needed — the backend only uses Node's built-in modules.

```bash
cd backend
node server.js
```

Then open **http://localhost:3000** in your browser.

> Opening `public/index.html` directly (double-clicking it) will **not**
> work — the dashboard needs the backend running so it can fetch `/api/...`.

## How the map works

- `places.json` lists each circuit's named attractions (e.g. Charminar,
  Golconda Fort) but no coordinates.
- On first visit to the "Interactive Map" tab, `map.js` sends each attraction
  name to Geoapify's **Geocoding API** to get its lat/lon, then plots it with
  `L.circleMarker`. Results are cached in `localStorage`, so it's instant after
  the first load.
- Map tiles come from Geoapify's **Map Tiles API** via Leaflet.
- Clicking a marker opens the shared modal (`App.openPlaceModal` in `app.js`)
  with the attraction name, its circuit's category/history, and footfall/revenue.

## API endpoints

| Route | Returns |
|---|---|
| `GET /api/overview` | Aggregated KPIs (totals, YoY growth, top circuit) |
| `GET /api/trends` | Full monthly series for 2024 and 2025 |
| `GET /api/places` | All 12 circuits, sorted by rank |
| `GET /api/places/:id` | One circuit, e.g. `/api/places/hyderabad` |

## Scope notes (things you may want to extend)

- **Images**: `places.image` is `null` for every circuit right now, so the
  modal shows a styled placeholder instead of a photo. Drop a URL into that
  field (or point it at your own uploaded images) to show real photos —
  no code changes needed.
- **History text** is currently per-circuit, not per-monument (that's the
  level of detail in the source spreadsheet). So e.g. Charminar and Golconda
  Fort — both in the Hyderabad circuit — currently show the same history
  paragraph. Give a place its own `history` field in `places.json` if you
  want monument-specific write-ups.
- The original dashboard mockup's 33-district choropleth map isn't included —
  this build's map plots individual attractions (matching "click a place, see
  its history") rather than shading district polygons. Say the word if you'd
  like that choropleth added too.
