document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll("[data-search]").forEach(input => {

        input.addEventListener("keyup", () => {

            const keyword = input.value.toLowerCase();

            const target = document.getElementById(input.dataset.search);

            if(!target){

                return;

            }

            target.querySelectorAll("[data-filter]").forEach(item => {

                item.style.display = item.innerText.toLowerCase().includes(keyword)
                    ? ""
                    : "none";

            });

        });

    });

});