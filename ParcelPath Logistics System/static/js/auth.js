document.addEventListener("DOMContentLoaded", () => {

    const passwordFields = document.querySelectorAll(".password-field");

    passwordFields.forEach(field => {

        const toggle = field.parentElement.querySelector(".toggle-password");

        if(toggle){

            toggle.addEventListener("click", () => {

                if(field.type === "password"){

                    field.type = "text";
                    toggle.classList.replace("bi-eye","bi-eye-slash");

                }else{

                    field.type = "password";
                    toggle.classList.replace("bi-eye-slash","bi-eye");

                }

            });

        }

    });

    const strengthBar = document.getElementById("passwordStrength");

    const password = document.getElementById("id_password");

    if(password && strengthBar){

        password.addEventListener("input", () => {

            const value = password.value.length;

            strengthBar.style.width = Math.min(value * 8,100) + "%";

            if(value < 6){

                strengthBar.className = "progress-bar bg-danger";

            }else if(value < 10){

                strengthBar.className = "progress-bar bg-warning";

            }else{

                strengthBar.className = "progress-bar bg-success";

            }

        });

    }

});