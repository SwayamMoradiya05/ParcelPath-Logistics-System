document.addEventListener("DOMContentLoaded", () => {

    const loader = document.getElementById("pageLoader");

    if(!loader){

        return;

    }

    window.addEventListener("load", () => {

        loader.classList.add("fade");

        setTimeout(() => {

            loader.remove();

        },400);

    });

});