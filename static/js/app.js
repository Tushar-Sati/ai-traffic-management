async function loadDashboardCharts() {
    const response = await fetch("/api/analytics");
    const data = await response.json();
    renderLineChart("dailyChart", "High Risk Incidents", data.daily);
    renderBarChart("monthlyChart", "Monthly Incidents", data.monthly, "#2f6fef");
    renderDoughnutChart("riskMixChart", data.risk_mix);
    renderBarChart("weatherChart", "Weather Records", data.weather, "#009879");
    renderBarChart("roadChart", "Road Records", data.roads, "#d97706");
}

function renderLineChart(id, label, rows) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    new Chart(canvas, {
        type: "line",
        data: {
            labels: rows.map(row => row.label),
            datasets: [{
                label,
                data: rows.map(row => row.total),
                borderColor: "#1769e0",
                backgroundColor: "rgba(23,105,224,0.12)",
                tension: 0.35,
                pointRadius: 4,
                fill: true
            }]
        },
        options: chartOptions()
    });
}

function renderBarChart(id, label, rows, color) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    new Chart(canvas, {
        type: "bar",
        data: {
            labels: rows.map(row => row.label),
            datasets: [{
                label,
                data: rows.map(row => row.total),
                backgroundColor: color,
                borderRadius: 6
            }]
        },
        options: chartOptions()
    });
}

function renderDoughnutChart(id, rows) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const palette = {
        "High Risk": "#dc3545",
        "Medium Risk": "#f2b705",
        "Low Risk": "#198754"
    };
    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: rows.map(row => row.label),
            datasets: [{
                data: rows.map(row => row.total),
                backgroundColor: rows.map(row => palette[row.label] || "#6c757d"),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            cutout: "68%",
            plugins: { legend: { position: "bottom" } }
        }
    });
}

function chartOptions() {
    return {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: "rgba(101,117,139,0.16)" } }
        }
    };
}

function bindPredictionForm() {
    const form = document.getElementById("predictionForm");
    const result = document.getElementById("predictionResult");
    if (!form || !result) return;
    const presets = {
        high: { location: "Ring Road", traffic_density: 89, weather: "Rain", vehicle_count: 850, speed: 21, road_condition: "Damaged" },
        medium: { location: "Metro Cross", traffic_density: 62, weather: "Cloudy", vehicle_count: 520, speed: 36, road_condition: "Moderate" },
        low: { location: "Green Corridor", traffic_density: 28, weather: "Clear", vehicle_count: 180, speed: 62, road_condition: "Good" }
    };
    document.querySelectorAll("[data-preset]").forEach(button => {
        button.addEventListener("click", () => {
            const preset = presets[button.dataset.preset];
            Object.entries(preset).forEach(([key, value]) => {
                const input = form.elements[key];
                if (input) input.value = value;
            });
        });
    });
    form.addEventListener("submit", async event => {
        event.preventDefault();
        const payload = Object.fromEntries(new FormData(form).entries());
        result.className = "result-panel";
        result.innerHTML = "<h3>Calculating...</h3>";
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) {
            result.innerHTML = `<h3>Prediction Failed</h3><p>${data.error}</p>`;
            return;
        }
        const riskClass = data.risk_level.includes("High") ? "risk-high" : data.risk_level.includes("Medium") ? "risk-medium" : "risk-low";
        result.className = `result-panel ${riskClass}`;
        result.innerHTML = `
            <span class="eyebrow">Prediction Result</span>
            <h3>${data.risk_level}</h3>
            <div class="probability-ring"><strong>${data.probability}%</strong><span>confidence</span></div>
            <p>${data.recommendation}</p>
        `;
    });
}

async function loadTrafficMap() {
    const el = document.getElementById("trafficMap");
    if (!el) return;
    const map = L.map("trafficMap").setView([28.6139, 77.2090], 11);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);
    const response = await fetch("/api/map-points");
    const points = await response.json();
    const bounds = [];
    const layers = [];
    points.forEach(point => {
        const color = point.risk_level.includes("High") ? "#dc3545" : point.risk_level.includes("Medium") ? "#ffc107" : "#198754";
        const marker = L.circleMarker([point.lat, point.lng], {
            radius: 9,
            color,
            fillColor: color,
            fillOpacity: 0.82
        }).addTo(map);
        marker.bindPopup(`<strong>${point.location}</strong><br>${point.risk_level}<br>Density: ${point.traffic_density}<br>Vehicles: ${point.vehicle_count}`);
        marker.riskLevel = point.risk_level;
        layers.push(marker);
        bounds.push([point.lat, point.lng]);
    });
    if (bounds.length) map.fitBounds(bounds, { padding: [30, 30] });
    document.querySelectorAll("[data-risk-filter]").forEach(button => {
        button.addEventListener("click", () => {
            document.querySelectorAll("[data-risk-filter]").forEach(item => item.classList.remove("active"));
            button.classList.add("active");
            const filter = button.dataset.riskFilter;
            layers.forEach(layer => {
                const visible = filter === "all" || layer.riskLevel === filter;
                if (visible && !map.hasLayer(layer)) layer.addTo(map);
                if (!visible && map.hasLayer(layer)) map.removeLayer(layer);
            });
        });
    });
}
