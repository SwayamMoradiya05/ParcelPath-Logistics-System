document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".availability-switch").forEach(toggle => {

        toggle.addEventListener("change", () => {

            const status = toggle.closest("tr").querySelector(".driver-status");

            if(toggle.checked){

                status.textContent = "Available";
                status.className = "badge bg-success driver-status";

            }else{

                status.textContent = "Unavailable";
                status.className = "badge bg-danger driver-status";

            }

        });

    });

    const routeButton = document.getElementById("openRoute");

    if(routeButton){

        routeButton.addEventListener("click", () => {

            window.scrollTo({
                top:0,
                behavior:"smooth"
            });

        });

    }

});