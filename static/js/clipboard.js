document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll("[data-copy]").forEach(button => {

        button.addEventListener("click", async () => {

            const target = document.getElementById(button.dataset.copy);

            if(!target){

                return;

            }

            try{

                await navigator.clipboard.writeText(target.innerText.trim());

                const original = button.innerHTML;

                button.innerHTML = "Copied";

                setTimeout(() => {

                    button.innerHTML = original;

                },1500);

            }catch(error){

                console.error(error);

            }

        });

    });

});