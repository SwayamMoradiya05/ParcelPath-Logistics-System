document.addEventListener("DOMContentLoaded", () => {

    const trackingForm = document.getElementById("trackingForm");

    if(trackingForm){

        trackingForm.addEventListener("submit", event => {

            const trackingInput = document.getElementById("trackingNumber");

            if(trackingInput.value.trim() === ""){

                event.preventDefault();

                alert("Please enter a tracking number.");

                trackingInput.focus();

            }

        });

    }

    const copyButton = document.getElementById("copyTracking");

    if(copyButton){

        copyButton.addEventListener("click", () => {

            const trackingNumber = document.getElementById("trackingValue").innerText;

            navigator.clipboard.writeText(trackingNumber);

            copyButton.innerText = "Copied";

            setTimeout(() => {

                copyButton.innerText = "Copy";

            },2000);

        });

    }

});