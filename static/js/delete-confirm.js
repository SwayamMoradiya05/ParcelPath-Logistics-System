document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".delete-record").forEach(button => {

        button.addEventListener("click", event => {

            const message = button.dataset.message ||
                "Are you sure you want to delete this record?";

            if(!confirm(message)){

                event.preventDefault();

            }

        });

    });

});