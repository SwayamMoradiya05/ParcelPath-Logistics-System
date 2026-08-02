document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.getElementById("sidebar");

    const toggle = document.getElementById("sidebarToggle");

    if(toggle && sidebar){

        toggle.addEventListener("click", () => {

            sidebar.classList.toggle("sidebar-open");

        });

    }

    document.querySelectorAll(".sidebar a").forEach(link => {

        if(link.href === window.location.href){

            link.classList.add("active");

        }

    });

});