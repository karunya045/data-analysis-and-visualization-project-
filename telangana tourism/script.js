const TELANGANA_DATA = {
    domestic2023: 58.448,
    foreign2023: 0.161,
    domestic2024: 88.240,
    foreign2024: 0.155
};


// -------------------------------
// CALCULATIONS
// -------------------------------

const total2024 =
    TELANGANA_DATA.domestic2024 +
    TELANGANA_DATA.foreign2024;

const domesticGrowth =
    ((TELANGANA_DATA.domestic2024 -
      TELANGANA_DATA.domestic2023)
      / TELANGANA_DATA.domestic2023) * 100;


// -------------------------------
// UPDATE KPI
// -------------------------------

document.getElementById("totalVisitors").textContent =
    total2024.toFixed(2) + "M";

document.getElementById("domesticVisitors").textContent =
    TELANGANA_DATA.domestic2024.toFixed(2) + "M";

document.getElementById("foreignVisitors").textContent =
    TELANGANA_DATA.foreign2024.toFixed(3) + "M";

document.getElementById("growth").textContent =
    domesticGrowth.toFixed(2) + "%";


// -------------------------------
// GROWTH CHART
// -------------------------------

new Chart(
    document.getElementById("growthChart"),
    {
        type: "bar",

        data: {
            labels: ["2023", "2024"],

            datasets: [
                {
                    label: "Domestic Visitors (Million)",
                    data: [
                        TELANGANA_DATA.domestic2023,
                        TELANGANA_DATA.domestic2024
                    ]
                },

                {
                    label: "Foreign Visitors (Million)",
                    data: [
                        TELANGANA_DATA.foreign2023,
                        TELANGANA_DATA.foreign2024
                    ]
                }
            ]
        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    position: "bottom"
                }
            },

            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    }
);


// -------------------------------
// VISITOR COMPOSITION
// -------------------------------

new Chart(
    document.getElementById("visitorChart"),
    {
        type: "doughnut",

        data: {
            labels: [
                "Domestic",
                "Foreign"
            ],

            datasets: [
                {
                    data: [
                        TELANGANA_DATA.domestic2024,
                        TELANGANA_DATA.foreign2024
                    ]
                }
            ]
        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    }
);


// -------------------------------
// MAP
// -------------------------------

const GEOAPIFY_KEY = "YOUR_NEW_API_KEY_HERE";

const map = L.map("map").setView(
    [17.95, 79.30],
    7
);

L.tileLayer(
    `https://maps.geoapify.com/v1/tile/osm-bright/{z}/{x}/{y}.png?apiKey=${GEOAPIFY_KEY}`,
    {
        maxZoom: 20,

        attribution:
            'Powered by <a href="https://www.geoapify.com/" target="_blank">Geoapify</a> | © OpenStreetMap contributors'
    }
).addTo(map);


// Add tourism places
if (typeof tourismPlaces !== "undefined") {

    tourismPlaces.forEach(place => {

        const marker = L.marker([
            place.lat,
            place.lon
        ]).addTo(map);

        marker.bindPopup(`
            <div style="min-width:220px">
                <h3>${place.name}</h3>
                <p><b>District:</b> ${place.district}</p>
                <p><b>Type:</b> ${place.type}</p>
            </div>
        `);

    });

}