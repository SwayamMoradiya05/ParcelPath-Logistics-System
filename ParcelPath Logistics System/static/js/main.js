document.addEventListener("DOMContentLoaded", () => {

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add("fade");
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });

    const currentPath = window.location.pathname;

    document.querySelectorAll(".navbar .nav-link").forEach(link => {
        if(link.getAttribute("href") === currentPath){
            link.classList.add("active");
        }
    });

    document.querySelectorAll("[data-confirm]").forEach(button => {
        button.addEventListener("click", e => {
            if(!confirm(button.dataset.confirm)){
                e.preventDefault();
            }
        });
    });

    document.querySelectorAll(".password-toggle").forEach(toggle => {

        toggle.addEventListener("click", () => {

            const input = toggle.previousElementSibling;

            if(input.type === "password"){
                input.type = "text";
                toggle.classList.replace("bi-eye","bi-eye-slash");
            }else{
                input.type = "password";
                toggle.classList.replace("bi-eye-slash","bi-eye");
            }

        });

    });

});