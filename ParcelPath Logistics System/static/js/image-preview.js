document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll("[data-image-input]").forEach(input => {

        input.addEventListener("change", event => {

            const file = event.target.files[0];

            if(!file){

                return;

            }

            const preview = document.getElementById(

                input.dataset.imageInput

            );

            if(!preview){

                return;

            }

            const reader = new FileReader();

            reader.onload = e => {

                preview.src = e.target.result;

            };

            reader.readAsDataURL(file);

        });

    });

});