let notificationSocket = null;

document.addEventListener("DOMContentLoaded", () => {

    if(!window.WebSocket){

        return;

    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";

    notificationSocket = new WebSocket(

        `${protocol}://${window.location.host}/ws/notifications/`

    );

    notificationSocket.onopen = () => {

        console.log("ParcelPath notification socket connected.");

    };

    notificationSocket.onmessage = event => {

        const data = JSON.parse(event.data);

        if(data.message){

            Utils.showToast(data.message);

        }

    };

    notificationSocket.onerror = error => {

        console.error(error);

    };

    notificationSocket.onclose = () => {

        console.log("Notification socket disconnected.");

    };

});