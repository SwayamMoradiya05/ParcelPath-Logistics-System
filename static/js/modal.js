document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll("[data-open-modal]").forEach(button => {

        button.addEventListener("click", () => {

            const target = button.dataset.openModal;

            const modalElement = document.getElementById(target);

            if(!modalElement){

                return;

            }

            const modal = new bootstrap.Modal(modalElement);

            modal.show();

        });

    });

    document.querySelectorAll("[data-close-modal]").forEach(button => {

        button.addEventListener("click", () => {

            const modalElement = button.closest(".modal");

            if(!modalElement){

                return;

            }

            const modal = bootstrap.Modal.getInstance(modalElement);

            if(modal){

                modal.hide();

            }

        });

    });

});