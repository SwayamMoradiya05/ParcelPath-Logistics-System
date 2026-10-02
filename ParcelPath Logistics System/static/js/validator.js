document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll("[data-required]").forEach(field => {

        field.addEventListener("blur", () => {

            if(field.value.trim() === ""){

                field.classList.add("is-invalid");

            }else{

                field.classList.remove("is-invalid");
                field.classList.add("is-valid");

            }

        });

    });

    const emailFields = document.querySelectorAll("[data-email]");

    emailFields.forEach(field => {

        field.addEventListener("blur", () => {

            const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if(field.value && !pattern.test(field.value)){

                field.classList.add("is-invalid");

            }else{

                field.classList.remove("is-invalid");

            }

        });

    });

});