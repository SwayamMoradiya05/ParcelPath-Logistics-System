document.addEventListener("DOMContentLoaded", () => {

    const printButton = document.getElementById("printInvoice");

    if(printButton){

        printButton.addEventListener("click", () => {

            window.print();

        });

    }

    const downloadButton = document.getElementById("downloadInvoice");

    if(downloadButton){

        downloadButton.addEventListener("click", () => {

            alert("PDF download will be available after backend integration.");

        });

    }

});