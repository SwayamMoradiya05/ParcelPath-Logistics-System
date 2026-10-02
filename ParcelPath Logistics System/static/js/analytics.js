document.addEventListener("DOMContentLoaded", () => {

    const revenueChart = document.getElementById("revenueChart");

    if(!revenueChart){

        return;

    }

    new Chart(revenueChart,{

        type:"bar",

        data:{

            labels:[
                "Mon","Tue","Wed","Thu","Fri","Sat","Sun"
            ],

            datasets:[{

                label:"Completed Deliveries",

                data:[24,31,28,36,42,39,45]

            }]

        },

        options:{

            responsive:true,

            maintainAspectRatio:false,

            scales:{

                y:{
                    beginAtZero:true
                }

            }

        }

    });

});