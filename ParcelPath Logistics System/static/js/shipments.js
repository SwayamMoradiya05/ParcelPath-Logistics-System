document.addEventListener("DOMContentLoaded", () => {

    const statusSelect = document.getElementById("shipmentStatus");

    if(statusSelect){

        statusSelect.addEventListener("change", () => {

            const badge = document.getElementById("statusPreview");

            if(!badge){

                return;

            }

            badge.innerText = statusSelect.value;

            badge.className = "badge";

            switch(statusSelect.value){

                case "Booked":
                    badge.classList.add("bg-secondary");
                    break;

                case "Confirmed":
                    badge.classList.add("bg-info");
                    break;

                case "In Transit":
                    badge.classList.add("bg-warning","text-dark");
                    break;

                case "Out For Delivery":
                    badge.classList.add("bg-primary");
                    break;

                case "Delivered":
                    badge.classList.add("bg-success");
                    break;

                case "Cancelled":
                    badge.classList.add("bg-danger");
                    break;

                default:
                    badge.classList.add("bg-secondary");

            }

        });

    }

});