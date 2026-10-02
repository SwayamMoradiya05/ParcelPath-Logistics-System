document.addEventListener("DOMContentLoaded", () => {

    const refreshElement = document.getElementById("autoRefresh");

    if(!refreshElement){

        return;

    }

    const interval = parseInt(

        refreshElement.dataset.interval || "60000"

    );

    setInterval(() => {

        fetch(window.location.href,{

            headers:{
                "X-Requested-With":"XMLHttpRequest"
            }

        }).catch(error => {

            console.error(error);

        });

    },interval);

});