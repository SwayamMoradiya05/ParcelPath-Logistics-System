document.addEventListener("DOMContentLoaded", () => {

    const driverSelect = document.getElementById("driverSelect");
    const shipmentList = document.getElementById("shipmentList");
    const stopCounter = document.getElementById("stopCounter");

    if(driverSelect){

        driverSelect.addEventListener("change", () => {

            console.log("Driver Selected:", driverSelect.value);

        });

    }

    if(shipmentList && stopCounter){

        const updateStops = () => {

            const checked = shipmentList.querySelectorAll("input[type='checkbox']:checked");

            stopCounter.textContent = checked.length;

        };

        shipmentList.querySelectorAll("input[type='checkbox']").forEach(item => {

            item.addEventListener("change", updateStops);

        });

        updateStops();

    }

});