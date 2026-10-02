document.addEventListener("DOMContentLoaded", () => {

    const themeButton = document.getElementById("themeToggle");

    if(!themeButton){

        return;

    }

    const savedTheme = localStorage.getItem("parcelpath-theme");

    if(savedTheme === "dark"){

        document.body.classList.add("dark-theme");

    }

    themeButton.addEventListener("click", () => {

        document.body.classList.toggle("dark-theme");

        if(document.body.classList.contains("dark-theme")){

            localStorage.setItem("parcelpath-theme","dark");

        }else{

            localStorage.setItem("parcelpath-theme","light");

        }

    });

});