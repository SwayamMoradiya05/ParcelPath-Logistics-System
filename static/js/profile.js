document.addEventListener("DOMContentLoaded", () => {

    const imageInput = document.getElementById("profileImage");

    const preview = document.getElementById("profilePreview");

    if(imageInput && preview){

        imageInput.addEventListener("change", event => {

            const file = event.target.files[0];

            if(!file){

                return;

            }

            const reader = new FileReader();

            reader.onload = e => {

                preview.src = e.target.result;

            };

            reader.readAsDataURL(file);

        });

    }

    const removeButton = document.getElementById("removeProfileImage");

    if(removeButton && preview){

        removeButton.addEventListener("click", () => {

            preview.src = "/static/images/default-user.png";

            if(imageInput){

                imageInput.value = "";

            }

        });

    }

});