const Utils = {

    formatDate(date){

        return new Date(date).toLocaleDateString();

    },

    formatTime(date){

        return new Date(date).toLocaleTimeString([],{

            hour:"2-digit",
            minute:"2-digit"

        });

    },

    showToast(message){

        const toast = document.createElement("div");

        toast.className = "toast-message";

        toast.innerText = message;

        document.body.appendChild(toast);

        setTimeout(() => {

            toast.classList.add("show");

        },100);

        setTimeout(() => {

            toast.classList.remove("show");

            setTimeout(() => {

                toast.remove();

            },300);

        },3000);

    },

    loading(button){

        if(!button){

            return;

        }

        button.disabled = true;

        button.dataset.original = button.innerHTML;

        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading';

    },

    reset(button){

        if(!button){

            return;

        }

        button.disabled = false;

        button.innerHTML = button.dataset.original;

    }

};