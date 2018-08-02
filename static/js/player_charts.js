var ctx = $("#statsChart");
        var scatterChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Stats for {{name}}',
                    data: [
                    {% for data in player_stats %}
                    {
                        x: {{ data.season }},
                        {% for passing in data.passing %}
                            y: {{ passing.total_yards }},
                        {% endfor %}
                        name: '{{ name }}'
                        
                    },
                    {% endfor %}
                    ],
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'linear',
                        position: 'bottom',
                        scaleLabel: {
                            display: true,
                            labelString: 'Season'
                        },
                        ticks: {
                            max: 2009,
                            min: 2017,
                            stepSize: 1000
                        }
                    }],
                    yAxes: [{
                        type: 'linear',
                        scaleLabel: {
                            display: true,
                            labelString: 'Total Yards'
                        },
                    }]
                },
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            var player_data = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index] || '';
                            return player_data.y + ' yards';
                        },
                        // labelColor: function(tooltipItem, chart) {
                        //     return {
                        //         borderColor: 'rgb(255, 0, 0)',
                        //         backgroundColor: 'rgb(255, 0, 0)'
                        //     }
                        // },
                        // labelTextColor:function(tooltipItem, chart){
                        //     return '#543453';
                        //  }
                    }
                }
            },
        });