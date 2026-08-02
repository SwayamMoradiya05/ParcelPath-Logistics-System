document.addEventListener("DOMContentLoaded", () => {

    const mapContainer = document.getElementById("deliveryMap");

    if(!mapContainer){

        return;

    }

    const latitude = parseFloat(mapContainer.dataset.lat);

    const longitude = parseFloat(mapContainer.dataset.lng);

    if(Number.isNaN(latitude) || Number.isNaN(longitude)){

        return;

    }

    const map = L.map("deliveryMap").setView([latitude, longitude], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{

        attribution:"© OpenStreetMap contributors"

    }).addTo(map);

    L.marker([latitude, longitude]).addTo(map);

});