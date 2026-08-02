document.addEventListener("DOMContentLoaded", () => {

    const switcher = document.getElementById("themeSwitcher");

    if(!switcher){

        return;

    }

    const saved = localStorage.getItem("parcelpath-theme") || "light";

    document.documentElement.setAttribute("data-theme",saved);

    switcher.checked = saved === "dark";

    switcher.addEventListener("change", () => {

        const theme = switcher.checked ? "dark" : "light";

        document.documentElement.setAttribute("data-theme",theme);

        localStorage.setItem("parcelpath-theme",theme);

    });

});