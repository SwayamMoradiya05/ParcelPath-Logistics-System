document.addEventListener("DOMContentLoaded", () => {

    const exportButtons = document.querySelectorAll("[data-export]");

    exportButtons.forEach(button => {

        button.addEventListener("click", () => {

            const tableId = button.dataset.export;

            const table = document.getElementById(tableId);

            if(!table){

                return;

            }

            let csv = [];

            table.querySelectorAll("tr").forEach(row => {

                const cols = row.querySelectorAll("th,td");

                const data = [];

                cols.forEach(col => {

                    data.push('"' + col.innerText.replace(/"/g,'""') + '"');

                });

                csv.push(data.join(","));

            });

            const blob = new Blob([csv.join("\n")],{

                type:"text/csv"

            });

            const url = URL.createObjectURL(blob);

            const link = document.createElement("a");

            link.href = url;

            link.download = "parcelpath-export.csv";

            link.click();

            URL.revokeObjectURL(url);

        });

    });

});