document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".table-sort").forEach(table => {

        const headers = table.querySelectorAll("th[data-sort]");

        headers.forEach((header,index) => {

            header.style.cursor = "pointer";

            header.addEventListener("click", () => {

                const rows = [...table.querySelector("tbody").rows];

                const ascending = !header.classList.contains("asc");

                headers.forEach(h => h.classList.remove("asc","desc"));

                header.classList.add(ascending ? "asc" : "desc");

                rows.sort((a,b) => {

                    const first = a.cells[index].innerText.trim();

                    const second = b.cells[index].innerText.trim();

                    return ascending
                        ? first.localeCompare(second,undefined,{numeric:true})
                        : second.localeCompare(first,undefined,{numeric:true});

                });

                const tbody = table.querySelector("tbody");

                rows.forEach(row => tbody.appendChild(row));

            });

        });

    });

});