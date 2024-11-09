document.addEventListener("DOMContentLoaded", function() {
    // Task Completion Trends Chart (Bar)
    var ctxTrends = document.getElementById('completionTrendsChart').getContext('2d');
    var completionTrendsChart = new Chart(ctxTrends, {
        type: 'bar',
        data: {
            labels: ['On Time', 'Overdue'],
            datasets: [{
                label: 'Tasks Completed',
                data: [chartData.onTimeTasks, chartData.overdueTasks],
                backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)'],
                borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Tasks Per Day Chart (Line)
    var ctxDay = document.getElementById('tasksPerDayChart').getContext('2d');
    var tasksPerDayChart = new Chart(ctxDay, {
        type: 'line',
        data: {
            labels: chartData.dayLabels,
            datasets: [{
                label: 'Tasks Completed Per Day',
                data: chartData.dayCounts,
                borderColor: 'rgba(54, 162, 235, 1)',
                fill: false
            }]
        }
    });

    // Tasks Per Week Chart (Bar)
    var ctxWeek = document.getElementById('tasksPerWeekChart').getContext('2d');
    var tasksPerWeekChart = new Chart(ctxWeek, {
        type: 'bar',
        data: {
            labels: chartData.weekLabels,
            datasets: [{
                label: 'Tasks Completed Per Week',
                data: chartData.weekCounts,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        }
    });

    // Spending By Category Chart (Pie)
    var ctxCategory = document.getElementById('spendingByCategoryChart').getContext('2d');
    var spendingByCategoryChart = new Chart(ctxCategory, {
        type: 'pie',
        data: {
            labels: chartData.categoryLabels,
            datasets: [{
                data: chartData.categoryTotals,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)', 
                    'rgba(54, 162, 235, 0.2)', 
                    'rgba(255, 206, 86, 0.2)', 
                    'rgba(75, 192, 192, 0.2)', 
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)', 
                    'rgba(54, 162, 235, 1)', 
                    'rgba(255, 206, 86, 1)', 
                    'rgba(75, 192, 192, 1)', 
                    'rgba(153, 102, 255, 1)', 
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        }
    });
});
