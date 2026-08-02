document.addEventListener("DOMContentLoaded", () => {

    const forms = document.querySelectorAll("form[data-validate]");

    forms.forEach(form => {

        form.addEventListener("submit", event => {

            let valid = true;

            form.querySelectorAll("[required]").forEach(field => {

                if(field.value.trim() === ""){

                    valid = false;

                    field.classList.add("is-invalid");

                }else{

                    field.classList.remove("is-invalid");

                    field.classList.add("is-valid");

                }

            });

            if(!valid){

                event.preventDefault();

            }

        });

    });

    document.querySelectorAll("input,textarea,select").forEach(field => {

        field.addEventListener("input", () => {

            if(field.value.trim() !== ""){

                field.classList.remove("is-invalid");

            }

        });

    });

});