document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".file-upload").forEach(wrapper => {

        const input = wrapper.querySelector("input[type='file']");
        const label = wrapper.querySelector(".file-name");

        if(!input || !label){

            return;

        }

        input.addEventListener("change", () => {

            if(input.files.length){

                label.textContent = input.files[0].name;

            }else{

                label.textContent = "Choose File";

            }

        });

    });

});