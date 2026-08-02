document.addEventListener("DOMContentLoaded", () => {

    const shipmentChart = document.getElementById("shipmentChart");

    if(shipmentChart){

        new Chart(shipmentChart,{

            type:"line",

            data:{

                labels:[
                    "Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"
                ],

                datasets:[{

                    label:"Shipments",

                    data:[
                        120,150,170,220,260,310,
                        280,340,370,410,450,500
                    ],

                    fill:false,

                    tension:.35

                }]

            },

            options:{

                responsive:true,

                maintainAspectRatio:false,

                plugins:{

                    legend:{
                        display:true
                    }

                }

            }

        });

    }

});