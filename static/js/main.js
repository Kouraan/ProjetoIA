var map;
var taxiMarkers = {};
var orderMarkers = {};

async function startSimulation() {
    try {
        const res = await fetch('/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                number_of_taxis: 5,
                search_algorithm: 2
            })
        });
        const data = await res.json();
        console.log("Simulation started:", data);
        return true;
    } catch (err) {
        console.error("Error starting simulation:", err);
        return false;
    }
}

async function updateTaxis() {
    const res = await fetch("/taxis");
    const taxis = await res.json();

    taxis.forEach(taxi => {
        const id = taxi.id;

        const lat = taxi.position[0];
        const lon = taxi.position[1];

        if (taxiMarkers[id]) {
            taxiMarkers[id].setLatLng([lat, lon]);
        } else {
            taxiMarkers[id] = L.circleMarker([lat, lon], {
                color: "#ff7800",
                fillColor: "#ff7800",
                fillOpacity: 0.8,
                radius: 8,
                weight: 2
            }).addTo(map);
            
            // Add popup with taxi info
            taxiMarkers[id].bindPopup(`Taxi ${id}`);
        }
    });
}

async function updateOrders() {
    const res = await fetch("/orders");
    const orders = await res.json();

    const currentOrderIds = orders.map(order => order.id.toString());

    Object.keys(orderMarkers).forEach(id => {
        if (!currentOrderIds.includes(id)) {
            map.removeLayer(orderMarkers[id]);
            delete orderMarkers[id];
        }
    });

    orders.forEach(order => {
        const id = order.id.toString();
        const lat = order.position[0];
        const lon = order.position[1];

        if (orderMarkers[id]) {
            orderMarkers[id].setLatLng([lat, lon]);
        } else {
            orderMarkers[id] = L.circleMarker([lat, lon], {
                color: 'blue',
                fillColor: 'lightblue',
                fillOpacity: 0.7,
                radius: 10
            }).addTo(map);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const bragaLatLng = [41.5454, -8.4265];
    map = L.map('map').setView(bragaLatLng, 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    
    startSimulation().then(success => {
        if (success) {
            setInterval(updateTaxis, 100);
            setInterval(updateOrders, 100);
        }
    });
});
