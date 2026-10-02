document.addEventListener("DOMContentLoaded", () => {

    const alerts = document.querySelectorAll(".alert-dismissible");

    alerts.forEach(alert => {

        setTimeout(() => {

            alert.classList.add("fade");

            setTimeout(() => {

                alert.remove();

            },300);

        },5000);

    });

    document.querySelectorAll(".alert-close").forEach(button => {

        button.addEventListener("click", () => {

            const alert = button.closest(".alert");

            if(alert){

                alert.remove();

            }

        });

    });

});