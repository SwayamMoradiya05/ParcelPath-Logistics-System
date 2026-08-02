document.addEventListener("DOMContentLoaded", () => {

    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("dashboardSidebar");

    if(sidebarToggle && sidebar){

        sidebarToggle.addEventListener("click", () => {
            sidebar.classList.toggle("show");
        });

    }

    document.querySelectorAll(".dashboard-card").forEach(card => {

        card.addEventListener("mouseenter", () => {
            card.style.transform = "translateY(-6px)";
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });

    });

    const refreshButton = document.getElementById("refreshDashboard");

    if(refreshButton){

        refreshButton.addEventListener("click", () => {
            location.reload();
        });

    }

});