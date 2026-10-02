document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll("form").forEach(form => {

        form.addEventListener("submit", event => {

            const button = form.querySelector("button[type='submit']");

            if(button){

                Utils.loading(button);

            }

        });

    });

    document.querySelectorAll("[data-bs-toggle='tooltip']").forEach(element => {

        new bootstrap.Tooltip(element);

    });

    document.querySelectorAll("[data-bs-toggle='popover']").forEach(element => {

        new bootstrap.Popover(element);

    });

});