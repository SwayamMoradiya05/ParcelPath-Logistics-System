document.addEventListener("DOMContentLoaded", () => {

    const statusElement = document.getElementById("liveTrackingStatus");

    if(!statusElement){

        return;

    }

    const trackingNumber = statusElement.dataset.tracking;

    if(!trackingNumber){

        return;

    }

    const refreshTracking = async () => {

        try{

            const response = await fetch(`/tracking/api/${trackingNumber}/`);

            if(!response.ok){

                return;

            }

            const data = await response.json();

            const status = document.getElementById("trackingStatus");
            const location = document.getElementById("trackingLocation");
            const updated = document.getElementById("trackingUpdated");

            if(status){

                status.textContent = data.status;

            }

            if(location){

                location.textContent = data.location;

            }

            if(updated){

                updated.textContent = data.updated_at;

            }

        }catch(error){

            console.error(error);

        }

    };

    refreshTracking();

    setInterval(refreshTracking,30000);

});