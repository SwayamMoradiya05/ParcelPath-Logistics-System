document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("dashboardSearch");

    if(!input){

        return;

    }

    input.addEventListener("keyup", () => {

        const keyword = input.value.toLowerCase();

        document.querySelectorAll(".dashboard-search-item").forEach(item => {

            item.style.display = item.textContent
                .toLowerCase()
                .includes(keyword)
                ? ""
                : "none";

        });

    });

});