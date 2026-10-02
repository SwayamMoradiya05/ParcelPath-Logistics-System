document.addEventListener("DOMContentLoaded", () => {

    const table = document.querySelector("[data-pagination]");

    if(!table){

        return;

    }

    const rows = [...table.querySelectorAll("tbody tr")];

    const perPage = parseInt(table.dataset.pagination) || 10;

    const pager = document.getElementById("pagination");

    let current = 1;

    function render(){

        rows.forEach((row,index) => {

            row.style.display =
                index >= (current - 1) * perPage &&
                index < current * perPage
                ? ""
                : "none";

        });

    }

    const pages = Math.ceil(rows.length / perPage);

    for(let i = 1; i <= pages; i++){

        const button = document.createElement("button");

        button.className = "btn btn-outline-primary btn-sm me-2";

        button.innerText = i;

        button.addEventListener("click", () => {

            current = i;

            render();

        });

        pager.appendChild(button);

    }

    render();

});