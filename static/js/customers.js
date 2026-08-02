document.addEventListener("DOMContentLoaded", () => {

    const searchInput = document.getElementById("customerSearch");

    if(searchInput){

        searchInput.addEventListener("keyup", () => {

            const keyword = searchInput.value.toLowerCase();

            document.querySelectorAll(".customer-row").forEach(row => {

                row.style.display = row.innerText.toLowerCase().includes(keyword)
                    ? ""
                    : "none";

            });

        });

    }

});