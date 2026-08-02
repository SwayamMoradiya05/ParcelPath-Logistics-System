document.addEventListener("DOMContentLoaded", () => {

    const markAllButton = document.getElementById("markAllRead");

    if(markAllButton){

        markAllButton.addEventListener("click", () => {

            document.querySelectorAll(".notification-item").forEach(item => {

                item.classList.remove("unread");

                const badge = item.querySelector(".badge");

                if(badge){

                    badge.remove();

                }

            });

        });

    }

    document.querySelectorAll(".notification-item").forEach(item => {

        item.addEventListener("click", () => {

            item.classList.remove("unread");

        });

    });

});