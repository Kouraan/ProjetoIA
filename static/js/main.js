var map;

document.addEventListener('DOMContentLoaded', function() {
    const bragaLatLng = [41.5454, -8.4265];
    map = L.map('map').setView(bragaLatLng, 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
});


var taxiMarkers = {};
var orderMarkers = {};
        
fetch('/start', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        number_of_taxis: 5,
        search_algorithm: 2
    })
})
.then(res => res.json())
.then(data => console.log("Simulation started:", data))
.catch(err => console.error(err));


async function updateTaxis() {
    const res = await fetch("/taxis");
    const taxis = await res.json();

    taxis.forEach(taxi => {
        const id = taxi.id;

        const lat = taxi.position[0];
        const lon = taxi.position[1];

        const latOffset = 0.0005;
        const lonOffset = 0.0010;
        const bounds = [
            [lat - latOffset, lon - lonOffset], // SW
            [lat + latOffset, lon + lonOffset]  // NE
        ];

        if (taxiMarkers[id]) {
            taxiMarkers[id].setBounds(bounds);
        } else {
            taxiMarkers[id] = L.rectangle(bounds, {
                color: "#ff7800",
                weight: 1,
                fillOpacity: 0.8
            }).addTo(map);
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



setInterval(updateOrders, 20)
setInterval(updateTaxis, 20)
